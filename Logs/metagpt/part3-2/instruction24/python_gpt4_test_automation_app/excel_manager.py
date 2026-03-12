import openpyxl
import pandas as pd
from typing import Dict, Any

class ExcelManager:
    """
    Handles creation and analysis of Excel files for input and output test scenarios.
    Uses openpyxl for writing and pandas for reading/analyzing.
    """

    def create_input_excel(self, data: Dict[str, Any], path: str):
        """
        Creates an Excel file at the given path from the provided data dictionary.
        The data dict should be structured as {sheet_name: [row_dict, ...], ...}
        Each row_dict is a mapping of column_name to value.
        """
        wb = openpyxl.Workbook()
        # Remove the default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)

        for sheet_name, rows in data.items():
            ws = wb.create_sheet(title=sheet_name)
            if not rows:
                continue
            # Get all column names from the first row
            columns = list(rows[0].keys())
            ws.append(columns)
            for row in rows:
                ws.append([row.get(col, "") for col in columns])
        wb.save(path)

    def analyze_output_excel(self, path: str) -> Dict[str, Any]:
        """
        Analyzes the Excel file at the given path and returns its contents as a dictionary.
        The returned dict is structured as {sheet_name: [row_dict, ...], ...}
        Each row_dict is a mapping of column_name to value.
        """
        xls = pd.ExcelFile(path)
        result = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            # Convert DataFrame to list of dicts
            rows = df.to_dict(orient="records")
            result[sheet_name] = rows
        return result
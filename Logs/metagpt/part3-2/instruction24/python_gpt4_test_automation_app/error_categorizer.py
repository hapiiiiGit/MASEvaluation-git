from typing import Dict, List, Any

class ErrorCategorizer:
    """
    Handles error categorization logic for analyzed output data.
    Provides categorize_errors(output_data: dict) -> list and configurable_categories: dict.
    """

    def __init__(self, categories: Dict[str, str] = None):
        # Default error categories can be customized
        self.configurable_categories = categories if categories else {
            "MissingValue": "A required value is missing.",
            "TypeMismatch": "Data type does not match expected type.",
            "OutOfRange": "Value is out of allowed range.",
            "FormatError": "Value format is incorrect.",
            "LogicError": "Logical inconsistency detected.",
            "UnknownError": "Uncategorized error."
        }

    def categorize_errors(self, output_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Analyzes output_data and returns a list of categorized errors.
        Each error is a dict: {"category": str, "description": str}
        """
        errors = []
        for sheet_name, rows in output_data.items():
            for row_idx, row in enumerate(rows):
                for col, value in row.items():
                    # Example error checks (can be extended/configured)
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        errors.append({
                            "category": "MissingValue",
                            "description": f"Sheet '{sheet_name}', Row {row_idx+2}, Column '{col}': {self.configurable_categories['MissingValue']}"
                        })
                    elif isinstance(value, str) and value.lower() == "error":
                        errors.append({
                            "category": "LogicError",
                            "description": f"Sheet '{sheet_name}', Row {row_idx+2}, Column '{col}': {self.configurable_categories['LogicError']}"
                        })
                    elif isinstance(value, str) and not self._is_valid_format(value):
                        errors.append({
                            "category": "FormatError",
                            "description": f"Sheet '{sheet_name}', Row {row_idx+2}, Column '{col}': {self.configurable_categories['FormatError']}"
                        })
                    elif self._is_out_of_range(value):
                        errors.append({
                            "category": "OutOfRange",
                            "description": f"Sheet '{sheet_name}', Row {row_idx+2}, Column '{col}': {self.configurable_categories['OutOfRange']}"
                        })
                    # Add more error checks as needed

        if not errors:
            errors.append({
                "category": "UnknownError",
                "description": "No errors detected or unable to categorize errors."
            })
        return errors

    def _is_valid_format(self, value: str) -> bool:
        # Example: check if value is a valid number or date string
        # Extend this function for more format checks
        try:
            float(value)
            return True
        except ValueError:
            pass
        # Check for date format (YYYY-MM-DD)
        import re
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            return True
        return False

    def _is_out_of_range(self, value: Any) -> bool:
        # Example: check if numeric value is out of range
        if isinstance(value, (int, float)):
            if value < 0 or value > 1e6:  # Example range
                return True
        return False
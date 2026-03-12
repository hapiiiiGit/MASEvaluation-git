import os
import logging
from typing import List
from models import StudentRecord
import gspread
from google.oauth2.service_account import Credentials

class SheetsClient:
    """
    Handles aggregation and update of student data in a master Google Sheet.
    """

    def __init__(self, creds_path: str, sheet_name: str):
        """
        Initialize the SheetsClient.

        Args:
            creds_path (str): Path to the Google service account credentials JSON file.
            sheet_name (str): Name of the master Google Sheet.
        """
        self.logger = logging.getLogger("SheetsClient")
        self.creds_path = creds_path
        self.sheet_name = sheet_name
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        self.gc = self._authorize()
        self.sheet = self._open_sheet()

    def _authorize(self):
        """
        Authorize with Google Sheets API using service account credentials.

        Returns:
            gspread.Client: Authorized gspread client.
        """
        creds = Credentials.from_service_account_file(self.creds_path, scopes=self.scope)
        gc = gspread.authorize(creds)
        return gc

    def _open_sheet(self):
        """
        Open the master Google Sheet.

        Returns:
            gspread.Spreadsheet: The opened spreadsheet object.
        """
        try:
            sheet = self.gc.open(self.sheet_name)
            self.logger.info(f"Opened Google Sheet: {self.sheet_name}")
            return sheet
        except Exception as e:
            self.logger.error(f"Failed to open Google Sheet '{self.sheet_name}': {e}")
            raise

    def update_master_sheet(self, student_records: List[StudentRecord]):
        """
        Update the master Google Sheet with the provided student records.

        Args:
            student_records (List[StudentRecord]): List of student records to update.
        """
        worksheet = self.sheet.sheet1
        # Prepare header
        header = [
            "student_id", "name", "email", "machform_data", "academic_pathway",
            "pdf_path", "salesforce_id", "status"
        ]
        # Prepare rows
        rows = [header]
        for record in student_records:
            row = [
                record.student_id,
                record.name,
                record.email,
                str(record.machform_data),
                record.academic_pathway if record.academic_pathway else "",
                record.pdf_path if record.pdf_path else "",
                record.salesforce_id if record.salesforce_id else "",
                record.status
            ]
            rows.append(row)
        try:
            worksheet.clear()
            worksheet.append_rows(rows)
            self.logger.info(f"Updated master sheet with {len(student_records)} student records.")
        except Exception as e:
            self.logger.error(f"Failed to update master sheet: {e}")
            raise

    def get_student_records(self) -> List[StudentRecord]:
        """
        Retrieve student records from the master Google Sheet.

        Returns:
            List[StudentRecord]: List of StudentRecord objects.
        """
        worksheet = self.sheet.sheet1
        try:
            all_values = worksheet.get_all_values()
            if not all_values or len(all_values) < 2:
                return []
            header = all_values[0]
            records = []
            for row in all_values[1:]:
                data = dict(zip(header, row))
                # Convert machform_data from string to dict
                try:
                    machform_data = eval(data.get("machform_data", "{}"))
                except Exception:
                    machform_data = {}
                record = StudentRecord(
                    student_id=data.get("student_id", ""),
                    name=data.get("name", ""),
                    email=data.get("email", ""),
                    machform_data=machform_data,
                    academic_pathway=data.get("academic_pathway", ""),
                    pdf_path=data.get("pdf_path", ""),
                    salesforce_id=data.get("salesforce_id", ""),
                    status=data.get("status", "pending")
                )
                records.append(record)
            self.logger.info(f"Retrieved {len(records)} student records from master sheet.")
            return records
        except Exception as e:
            self.logger.error(f"Failed to retrieve student records: {e}")
            return []
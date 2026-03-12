import os
import logging
from typing import Optional
from models import StudentRecord

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

class DocsClient:
    """
    Handles filling a branded Google Docs template with pathway details and exporting as PDF.
    """

    def __init__(self, creds_path: str, template_doc_id: str, output_folder_id: str):
        """
        Initialize the DocsClient.

        Args:
            creds_path (str): Path to the Google service account credentials JSON file.
            template_doc_id (str): Google Docs template document ID.
            output_folder_id (str): Google Drive folder ID to store generated docs.
        """
        self.logger = logging.getLogger("DocsClient")
        self.creds_path = creds_path
        self.template_doc_id = template_doc_id
        self.output_folder_id = output_folder_id
        self.scopes = [
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds = Credentials.from_service_account_file(self.creds_path, scopes=self.scopes)
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def fill_template(self, student: StudentRecord) -> Optional[str]:
        """
        Fill the branded Google Docs template with student pathway details.

        Args:
            student (StudentRecord): The student record to fill into the template.

        Returns:
            str: The new Google Doc ID.
        """
        try:
            # 1. Copy the template
            copy_title = f"{student.name} - Academic Pathway"
            copied_file = self.drive_service.files().copy(
                fileId=self.template_doc_id,
                body={
                    'name': copy_title,
                    'parents': [self.output_folder_id]
                }
            ).execute()
            new_doc_id = copied_file['id']
            self.logger.info(f"Copied template for student {student.student_id} to doc {new_doc_id}")

            # 2. Prepare replacements
            replacements = {
                "{{STUDENT_NAME}}": student.name,
                "{{STUDENT_ID}}": student.student_id,
                "{{STUDENT_EMAIL}}": student.email,
                "{{ACADEMIC_PATHWAY}}": student.academic_pathway or "",
                "{{STATUS}}": student.status,
                # Add more fields as needed from machform_data
            }
            # Flatten machform_data for replacement
            for form_key, form_data in student.machform_data.items():
                for k, v in form_data.items():
                    replacements[f"{{{{{form_key.upper()}_{k.upper()}}}}}"] = str(v)

            # 3. Replace placeholders in the document
            requests = []
            for placeholder, value in replacements.items():
                requests.append({
                    "replaceAllText": {
                        "containsText": {
                            "text": placeholder,
                            "matchCase": True
                        },
                        "replaceText": value
                    }
                })
            self.docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={"requests": requests}
            ).execute()
            self.logger.info(f"Filled template for student {student.student_id} in doc {new_doc_id}")
            return new_doc_id
        except HttpError as e:
            self.logger.error(f"Google Docs API error for student {student.student_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error filling template for student {student.student_id}: {e}")
            return None

    def export_pdf(self, doc_id: str) -> Optional[str]:
        """
        Export the filled Google Doc as a PDF and download it locally.

        Args:
            doc_id (str): The Google Doc ID to export.

        Returns:
            str: Path to the downloaded PDF file.
        """
        try:
            # 1. Export the document as PDF from Google Drive
            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType='application/pdf'
            )
            pdf_filename = f"{doc_id}.pdf"
            pdf_path = os.path.join("templates", pdf_filename)
            with open(pdf_path, "wb") as f:
                f.write(request.execute())
            self.logger.info(f"Exported doc {doc_id} as PDF to {pdf_path}")
            return pdf_path
        except HttpError as e:
            self.logger.error(f"Google Drive API error exporting PDF for doc {doc_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error exporting PDF for doc {doc_id}: {e}")
            return None
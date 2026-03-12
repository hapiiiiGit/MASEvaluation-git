import logging
from typing import Optional
from simple_salesforce import Salesforce, SalesforceMalformedRequest
from models import StudentRecord

class SalesforceClient:
    """
    Handles uploading PDF documents and student records to Salesforce,
    linking to the correct Contact or custom object.
    """

    def __init__(
        self,
        username: str,
        password: str,
        security_token: str,
        domain: str = 'login',
        contact_object: str = 'Contact',
        pdf_object: str = 'ContentVersion',
        pdf_link_field: str = 'FirstName',  # Example field to match student name
        pdf_title_field: str = 'Title',     # Title field for ContentVersion
        pdf_file_field: str = 'VersionData' # File field for ContentVersion
    ):
        """
        Initialize the SalesforceClient.

        Args:
            username (str): Salesforce username.
            password (str): Salesforce password.
            security_token (str): Salesforce security token.
            domain (str): Salesforce domain ('login' or 'test').
            contact_object (str): Salesforce object name for contacts.
            pdf_object (str): Salesforce object name for PDF documents.
            pdf_link_field (str): Field to match student name/email.
            pdf_title_field (str): Field for PDF title.
            pdf_file_field (str): Field for PDF file data.
        """
        self.logger = logging.getLogger("SalesforceClient")
        try:
            self.sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain
            )
            self.logger.info("Salesforce authentication successful.")
        except Exception as e:
            self.logger.error(f"Salesforce authentication failed: {e}")
            raise

        self.contact_object = contact_object
        self.pdf_object = pdf_object
        self.pdf_link_field = pdf_link_field
        self.pdf_title_field = pdf_title_field
        self.pdf_file_field = pdf_file_field

    def _find_contact_id(self, student: StudentRecord) -> Optional[str]:
        """
        Find the Salesforce Contact ID for the student by email.

        Args:
            student (StudentRecord): The student record.

        Returns:
            Optional[str]: The Contact ID if found, else None.
        """
        try:
            query = f"SELECT Id FROM {self.contact_object} WHERE Email = '{student.email}' LIMIT 1"
            result = self.sf.query(query)
            records = result.get('records', [])
            if records:
                contact_id = records[0]['Id']
                self.logger.info(f"Found Contact ID {contact_id} for student {student.email}")
                return contact_id
            else:
                self.logger.warning(f"No Contact found for student email: {student.email}")
                return None
        except SalesforceMalformedRequest as e:
            self.logger.error(f"Malformed Salesforce query: {e.content}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding Contact for student {student.email}: {e}")
            return None

    def upload_document(self, student: StudentRecord, pdf_path: str) -> Optional[str]:
        """
        Upload the PDF document to Salesforce and link to the correct Contact.

        Args:
            student (StudentRecord): The student record.
            pdf_path (str): Path to the PDF file.

        Returns:
            Optional[str]: The Salesforce ContentVersion ID if successful, else None.
        """
        if not pdf_path or not student:
            self.logger.error("Missing PDF path or student record.")
            return None

        # Read PDF file data
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read PDF file {pdf_path}: {e}")
            return None

        # Find the Contact ID
        contact_id = self._find_contact_id(student)
        if not contact_id:
            self.logger.error(f"Cannot upload PDF: Contact not found for student {student.email}")
            return None

        # Upload PDF as ContentVersion
        try:
            pdf_title = f"{student.name} - Academic Pathway"
            content_version = {
                self.pdf_title_field: pdf_title,
                self.pdf_file_field: pdf_data,
                "PathOnClient": pdf_title + ".pdf"
            }
            result = self.sf.__getattr__(self.pdf_object).create(content_version)
            content_version_id = result.get('id')
            self.logger.info(f"Uploaded PDF to Salesforce ContentVersion: {content_version_id}")

            # Link ContentVersion to Contact via ContentDocumentLink
            # First, get ContentDocumentId from ContentVersion
            query = f"SELECT ContentDocumentId FROM ContentVersion WHERE Id = '{content_version_id}'"
            doc_result = self.sf.query(query)
            doc_records = doc_result.get('records', [])
            if not doc_records:
                self.logger.error(f"ContentDocumentId not found for ContentVersion {content_version_id}")
                return content_version_id

            content_document_id = doc_records[0]['ContentDocumentId']
            # Create ContentDocumentLink
            link_result = self.sf.ContentDocumentLink.create({
                "ContentDocumentId": content_document_id,
                "LinkedEntityId": contact_id,
                "ShareType": "V",  # Viewer
                "Visibility": "AllUsers"
            })
            self.logger.info(f"Linked PDF ContentDocument {content_document_id} to Contact {contact_id}")

            return content_version_id
        except SalesforceMalformedRequest as e:
            self.logger.error(f"Salesforce malformed request: {e.content}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to upload PDF to Salesforce: {e}")
            return None
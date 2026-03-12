import os
import logging
from typing import Dict, List
from models import StudentRecord
from machform_client import MachFormClient
from sheets_client import SheetsClient
from openai_client import OpenAIClient
from docs_client import DocsClient
from pdf_exporter import PDFExporter
from email_sender import EmailSender
from salesforce_client import SalesforceClient
import admin_dashboard

# Configuration - In production, use config.py or environment variables
MACHFORM_BASE_URLS = {
    "form1": os.getenv("MACHFORM_FORM1_URL", "https://machform.example.com/api/form1"),
    "form2": os.getenv("MACHFORM_FORM2_URL", "https://machform.example.com/api/form2"),
    "form3": os.getenv("MACHFORM_FORM3_URL", "https://machform.example.com/api/form3"),
}
MACHFORM_API_KEYS = {
    "form1": os.getenv("MACHFORM_FORM1_API_KEY", "form1_api_key"),
    "form2": os.getenv("MACHFORM_FORM2_API_KEY", "form2_api_key"),
    "form3": os.getenv("MACHFORM_FORM3_API_KEY", "form3_api_key"),
}
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH", "config/google_service_account.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Student Master Sheet")
GOOGLE_DOCS_TEMPLATE_ID = os.getenv("GOOGLE_DOCS_TEMPLATE_ID", "your_template_doc_id")
GOOGLE_DRIVE_OUTPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_OUTPUT_FOLDER_ID", "your_output_folder_id")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_email_password")
SENDER_NAME = os.getenv("SENDER_NAME", "Admissions Office")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME", "your_sf_username")
SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "your_sf_password")
SALESFORCE_TOKEN = os.getenv("SALESFORCE_TOKEN", "your_sf_token")
SALESFORCE_DOMAIN = os.getenv("SALESFORCE_DOMAIN", "login")
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", None)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Main")

def collect_student_data() -> List[StudentRecord]:
    """
    Fetch data from 3 MachForms, aggregate into StudentRecord objects.
    """
    machform_client = MachFormClient(MACHFORM_BASE_URLS, MACHFORM_API_KEYS)
    all_data = machform_client.fetch_all_forms()
    # Aggregate by student_id (assuming each form has 'student_id' field)
    student_map: Dict[str, Dict[str, Dict]] = {}
    for form_id, submissions in all_data.items():
        for entry in submissions:
            student_id = entry.get("student_id")
            if not student_id:
                continue
            if student_id not in student_map:
                student_map[student_id] = {}
            student_map[student_id][form_id] = entry
    # Build StudentRecord objects
    students = []
    for student_id, forms in student_map.items():
        # Use form1 for name/email if available, else fallback
        name = ""
        email = ""
        for form in forms.values():
            if not name and "name" in form:
                name = form["name"]
            if not email and "email" in form:
                email = form["email"]
        student = StudentRecord(
            student_id=student_id,
            name=name,
            email=email,
            machform_data=forms,
            status="data_collected"
        )
        students.append(student)
    logger.info(f"Collected data for {len(students)} students from MachForms.")
    return students

def process_students(students: List[StudentRecord]):
    """
    For each student, generate pathway, fill template, export PDF, email, upload to Salesforce.
    """
    sheets_client = SheetsClient(GOOGLE_CREDS_PATH, GOOGLE_SHEET_NAME)
    openai_client = OpenAIClient(OPENAI_API_KEY)
    docs_client = DocsClient(GOOGLE_CREDS_PATH, GOOGLE_DOCS_TEMPLATE_ID, GOOGLE_DRIVE_OUTPUT_FOLDER_ID)
    pdf_exporter = PDFExporter(WKHTMLTOPDF_PATH)
    email_sender = EmailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_NAME, SENDER_EMAIL)
    salesforce_client = SalesforceClient(SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_TOKEN, SALESFORCE_DOMAIN)

    for student in students:
        try:
            # Generate academic pathway
            student.academic_pathway = openai_client.generate_pathway(student.to_dict())
            student.status = "pathway_generated"
            logger.info(f"Generated pathway for {student.student_id}")

            # Fill Google Docs template
            doc_id = docs_client.fill_template(student)
            if not doc_id:
                student.status = "error"
                logger.error(f"Failed to fill template for {student.student_id}")
                continue

            # Export as PDF
            pdf_path = docs_client.export_pdf(doc_id)
            if not pdf_path:
                student.status = "error"
                logger.error(f"Failed to export PDF for {student.student_id}")
                continue
            student.pdf_path = pdf_path
            student.status = "pdf_sent"
            logger.info(f"Exported PDF for {student.student_id}")

            # Email PDF to student
            subject = "Your Personalized Academic Pathway"
            body = f"""
            <p>Dear {student.name},</p>
            <p>Please find attached your personalized academic pathway. If you have any questions, contact admissions.</p>
            <p>Best regards,<br>Admissions Office</p>
            """
            try:
                email_sender.send_email(student.email, subject, body, pdf_path)
                student.status = "pdf_sent"
                logger.info(f"Emailed PDF to {student.email}")
            except Exception as e:
                student.status = "error"
                logger.error(f"Failed to send email to {student.email}: {e}")
                continue

            # Upload PDF to Salesforce
            try:
                sf_id = salesforce_client.upload_document(student, pdf_path)
                student.salesforce_id = sf_id
                student.status = "sf_uploaded"
                logger.info(f"Uploaded PDF to Salesforce for {student.student_id}")
            except Exception as e:
                student.status = "error"
                logger.error(f"Failed to upload PDF to Salesforce for {student.student_id}: {e}")
                continue

            # Mark as completed
            student.status = "completed"
        except Exception as e:
            student.status = "error"
            logger.error(f"Error processing student {student.student_id}: {e}")

    # Update master sheet
    sheets_client.update_master_sheet(students)
    logger.info("Master Google Sheet updated with all student records.")

def main():
    logger.info("Starting student evaluation automation workflow...")
    # Step 1: Collect student data from MachForms
    students = collect_student_data()
    if not students:
        logger.error("No student data collected. Exiting.")
        return

    # Step 2: Update master Google Sheet with collected data
    sheets_client = SheetsClient(GOOGLE_CREDS_PATH, GOOGLE_SHEET_NAME)
    sheets_client.update_master_sheet(students)
    logger.info("Initial student data written to master sheet.")

    # Step 3: Process each student (generate pathway, docs, PDF, email, Salesforce)
    process_students(students)

    # Step 4: Start admin dashboard (Flask app)
    logger.info("Starting admin dashboard web app...")
    admin_dashboard.app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
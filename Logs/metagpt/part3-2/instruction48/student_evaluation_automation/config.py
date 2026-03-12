import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# MachForm configuration
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

# Google configuration
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH", "config/google_service_account.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Student Master Sheet")
GOOGLE_DOCS_TEMPLATE_ID = os.getenv("GOOGLE_DOCS_TEMPLATE_ID", "your_template_doc_id")
GOOGLE_DRIVE_OUTPUT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_OUTPUT_FOLDER_ID", "your_output_folder_id")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_email_password")
SENDER_NAME = os.getenv("SENDER_NAME", "Admissions Office")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
USE_TLS = os.getenv("USE_TLS", "True").lower() in ("true", "1", "yes")

# Salesforce configuration
SALESFORCE_USERNAME = os.getenv("SALESFORCE_USERNAME", "your_sf_username")
SALESFORCE_PASSWORD = os.getenv("SALESFORCE_PASSWORD", "your_sf_password")
SALESFORCE_TOKEN = os.getenv("SALESFORCE_TOKEN", "your_sf_token")
SALESFORCE_DOMAIN = os.getenv("SALESFORCE_DOMAIN", "login")
SALESFORCE_CONTACT_OBJECT = os.getenv("SALESFORCE_CONTACT_OBJECT", "Contact")
SALESFORCE_PDF_OBJECT = os.getenv("SALESFORCE_PDF_OBJECT", "ContentVersion")
SALESFORCE_PDF_LINK_FIELD = os.getenv("SALESFORCE_PDF_LINK_FIELD", "FirstName")
SALESFORCE_PDF_TITLE_FIELD = os.getenv("SALESFORCE_PDF_TITLE_FIELD", "Title")
SALESFORCE_PDF_FILE_FIELD = os.getenv("SALESFORCE_PDF_FILE_FIELD", "VersionData")

# PDF Exporter configuration
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", None)

# Flask/General configuration
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Other settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Utility: Centralized config object (optional)
class Config:
    MACHFORM_BASE_URLS = MACHFORM_BASE_URLS
    MACHFORM_API_KEYS = MACHFORM_API_KEYS
    GOOGLE_CREDS_PATH = GOOGLE_CREDS_PATH
    GOOGLE_SHEET_NAME = GOOGLE_SHEET_NAME
    GOOGLE_DOCS_TEMPLATE_ID = GOOGLE_DOCS_TEMPLATE_ID
    GOOGLE_DRIVE_OUTPUT_FOLDER_ID = GOOGLE_DRIVE_OUTPUT_FOLDER_ID
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENAI_MODEL = OPENAI_MODEL
    SMTP_SERVER = SMTP_SERVER
    SMTP_PORT = SMTP_PORT
    SMTP_USER = SMTP_USER
    SMTP_PASSWORD = SMTP_PASSWORD
    SENDER_NAME = SENDER_NAME
    SENDER_EMAIL = SENDER_EMAIL
    USE_TLS = USE_TLS
    SALESFORCE_USERNAME = SALESFORCE_USERNAME
    SALESFORCE_PASSWORD = SALESFORCE_PASSWORD
    SALESFORCE_TOKEN = SALESFORCE_TOKEN
    SALESFORCE_DOMAIN = SALESFORCE_DOMAIN
    SALESFORCE_CONTACT_OBJECT = SALESFORCE_CONTACT_OBJECT
    SALESFORCE_PDF_OBJECT = SALESFORCE_PDF_OBJECT
    SALESFORCE_PDF_LINK_FIELD = SALESFORCE_PDF_LINK_FIELD
    SALESFORCE_PDF_TITLE_FIELD = SALESFORCE_PDF_TITLE_FIELD
    SALESFORCE_PDF_FILE_FIELD = SALESFORCE_PDF_FILE_FIELD
    WKHTMLTOPDF_PATH = WKHTMLTOPDF_PATH
    FLASK_SECRET_KEY = FLASK_SECRET_KEY
    APP_HOST = APP_HOST
    APP_PORT = APP_PORT
    DEBUG = DEBUG
    LOG_LEVEL = LOG_LEVEL
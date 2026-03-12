## Implementation approach

We will use Python as the main language, leveraging open-source libraries for integration:
- MachForms: Data fetched via HTTP requests (assuming API or webhooks; otherwise, web scraping).
- Google Sheets: Use `gspread` or `google-api-python-client` for Sheets API.
- OpenAI API: Use `openai` Python SDK.
- Google Docs & PDF: Use `google-api-python-client` for Docs, and `pdfkit` or Google Docs export for PDF.
- Email: Use `smtplib` or `sendgrid` for sending emails.
- Salesforce: Use `simple-salesforce` for API integration.
- Admin Tracking Interface: Use `Flask` or `FastAPI` for a web dashboard, with `Bootstrap` for UI.
- Security: Use OAuth2 for Google and Salesforce, environment variables for secrets, and logging for audit.

## File list

- main.py
- config.py
- machform_client.py
- sheets_client.py
- openai_client.py
- docs_client.py
- pdf_exporter.py
- email_sender.py
- salesforce_client.py
- admin_dashboard.py
- models.py
- utils.py
- requirements.txt
- templates/
    - branded_template.docx
- static/
    - style.css
- docs/
    - system_design.md
    - system_design-sequence-diagram.mermaid
    - system_design-sequence-diagram.mermaid-class-diagram

## Data structures and interfaces:

```mermaid
classDiagram
    class StudentRecord {
        +student_id: str
        +name: str
        +email: str
        +machform_data: dict
        +academic_pathway: str
        +pdf_path: str
        +salesforce_id: str
        +status: str
        +__init__(student_id: str, name: str, email: str, machform_data: dict)
    }
    class MachFormClient {
        +fetch_form_data(form_id: str) -> list[dict]
    }
    class SheetsClient {
        +update_master_sheet(student_records: list[StudentRecord])
        +get_student_records() -> list[StudentRecord]
    }
    class OpenAIClient {
        +generate_pathway(student_data: dict) -> str
    }
    class DocsClient {
        +fill_template(student: StudentRecord) -> str
        +export_pdf(doc_id: str) -> str
    }
    class PDFExporter {
        +export(doc_path: str) -> str
    }
    class EmailSender {
        +send_email(to: str, subject: str, body: str, attachment: str)
    }
    class SalesforceClient {
        +upload_document(student: StudentRecord, pdf_path: str) -> str
    }
    class AdminDashboard {
        +get_status(student_id: str) -> dict
        +list_students(status: str = None) -> list[StudentRecord]
        +manual_resend(student_id: str)
    }
    class Logger {
        +log(action: str, details: dict)
    }
    StudentRecord <.. AdminDashboard
    MachFormClient <.. StudentRecord
    SheetsClient <.. StudentRecord
    OpenAIClient <.. StudentRecord
    DocsClient <.. StudentRecord
    PDFExporter <.. DocsClient
    EmailSender <.. StudentRecord
    SalesforceClient <.. StudentRecord
    Logger <.. AdminDashboard
```

## Program call flow:

```mermaid
sequenceDiagram
    participant MF as MachFormClient
    participant SC as SheetsClient
    participant OA as OpenAIClient
    participant DC as DocsClient
    participant PE as PDFExporter
    participant ES as EmailSender
    participant SF as SalesforceClient
    participant AD as AdminDashboard
    participant SR as StudentRecord
    participant LG as Logger
    MF->>MF: fetch_form_data(form_id)
    MF-->>SR: return machform_data
    SR->>SC: update_master_sheet(student_records)
    SC-->>SR: get_student_records()
    SR->>OA: generate_pathway(student_data)
    OA-->>SR: return academic_pathway
    SR->>DC: fill_template(student)
    DC-->>SR: return doc_id
    SR->>DC: export_pdf(doc_id)
    DC-->>SR: return pdf_path
    SR->>PE: export(doc_path)
    PE-->>SR: return pdf_path
    SR->>ES: send_email(to, subject, body, attachment)
    ES-->>SR: email sent
    SR->>SF: upload_document(student, pdf_path)
    SF-->>SR: return salesforce_id
    AD->>SR: get_status(student_id)
    AD->>SR: list_students(status)
    AD->>SR: manual_resend(student_id)
    LG->>AD: log(action, details)
```

## Anything UNCLEAR

- MachForm API details: Is there a REST API or only webhooks/exports?
- Exact data fields/formats from MachForms?
- Should admins be able to edit pathways before sending?
- Branding requirements for Google Docs template?
- Salesforce object for PDF attachment?
- Expected student volume per cycle?

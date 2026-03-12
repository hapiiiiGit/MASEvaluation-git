import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from models import StudentRecord
from sheets_client import SheetsClient
from openai_client import OpenAIClient
from docs_client import DocsClient
from pdf_exporter import PDFExporter
from email_sender import EmailSender
from salesforce_client import SalesforceClient

# Configuration (should be loaded from config.py in production)
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

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Initialize clients
sheets_client = SheetsClient(GOOGLE_CREDS_PATH, GOOGLE_SHEET_NAME)
openai_client = OpenAIClient(OPENAI_API_KEY)
docs_client = DocsClient(GOOGLE_CREDS_PATH, GOOGLE_DOCS_TEMPLATE_ID, GOOGLE_DRIVE_OUTPUT_FOLDER_ID)
pdf_exporter = PDFExporter(WKHTMLTOPDF_PATH)
email_sender = EmailSender(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_NAME, SENDER_EMAIL)
salesforce_client = SalesforceClient(SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_TOKEN, SALESFORCE_DOMAIN)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdminDashboard")

def get_status(student_id: str) -> dict:
    """
    Get the status of a student by ID.
    """
    students = sheets_client.get_student_records()
    for student in students:
        if student.student_id == student_id:
            return student.to_dict()
    return {}

def list_students(status: str = None) -> list:
    """
    List students, optionally filtered by status.
    """
    students = sheets_client.get_student_records()
    if status:
        students = [s for s in students if s.status == status]
    return students

def manual_resend(student_id: str) -> bool:
    """
    Manually re-send the academic pathway PDF to the student and update Salesforce.
    """
    students = sheets_client.get_student_records()
    student = next((s for s in students if s.student_id == student_id), None)
    if not student:
        logger.error(f"Student {student_id} not found for manual resend.")
        return False

    # Regenerate pathway if needed
    if not student.academic_pathway or student.status not in ["pathway_generated", "pdf_sent", "sf_uploaded", "completed"]:
        student.academic_pathway = openai_client.generate_pathway(student.to_dict())
        student.status = "pathway_generated"

    # Fill template and export PDF
    doc_id = docs_client.fill_template(student)
    if not doc_id:
        logger.error(f"Failed to fill template for student {student_id}")
        return False
    pdf_path = docs_client.export_pdf(doc_id)
    if not pdf_path:
        logger.error(f"Failed to export PDF for student {student_id}")
        return False
    student.pdf_path = pdf_path
    student.status = "pdf_sent"

    # Send email
    subject = "Your Personalized Academic Pathway"
    body = f"""
    <p>Dear {student.name},</p>
    <p>Please find attached your personalized academic pathway. If you have any questions, contact admissions.</p>
    <p>Best regards,<br>Admissions Office</p>
    """
    try:
        email_sender.send_email(student.email, subject, body, pdf_path)
        student.status = "pdf_sent"
    except Exception as e:
        logger.error(f"Failed to send email to {student.email}: {e}")
        return False

    # Upload to Salesforce
    try:
        sf_id = salesforce_client.upload_document(student, pdf_path)
        student.salesforce_id = sf_id
        student.status = "sf_uploaded"
    except Exception as e:
        logger.error(f"Failed to upload PDF to Salesforce for student {student.email}: {e}")
        return False

    # Update master sheet
    sheets_client.update_master_sheet([student])
    student.status = "completed"
    sheets_client.update_master_sheet([student])
    logger.info(f"Manual resend completed for student {student_id}")
    return True

@app.route('/')
def dashboard():
    """
    Admin dashboard: list students with status indicators.
    """
    status_filter = request.args.get('status')
    students = list_students(status_filter)
    return render_template('dashboard.html', students=students, status_filter=status_filter)

@app.route('/student/<student_id>')
def student_detail(student_id):
    """
    Detail view for a student.
    """
    student = get_status(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('dashboard'))
    return render_template('student_detail.html', student=student)

@app.route('/resend/<student_id>', methods=['POST'])
def resend(student_id):
    """
    Manual resend of academic pathway PDF and Salesforce upload.
    """
    success = manual_resend(student_id)
    if success:
        flash("Resend successful.", "success")
    else:
        flash("Resend failed. Check logs for details.", "danger")
    return redirect(url_for('student_detail', student_id=student_id))

@app.route('/search')
def search():
    """
    Search students by name, email, or ID.
    """
    query = request.args.get('q', '').lower()
    students = sheets_client.get_student_records()
    results = []
    for s in students:
        if query in s.name.lower() or query in s.email.lower() or query in s.student_id.lower():
            results.append(s)
    return render_template('dashboard.html', students=results, status_filter=None, search_query=query)

@app.route('/download_pdf/<student_id>')
def download_pdf(student_id):
    """
    Download the student's PDF document.
    """
    students = sheets_client.get_student_records()
    student = next((s for s in students if s.student_id == student_id), None)
    if not student or not student.pdf_path or not os.path.isfile(student.pdf_path):
        flash("PDF not found for this student.", "danger")
        return redirect(url_for('student_detail', student_id=student_id))
    return send_file(student.pdf_path, as_attachment=True)

@app.route('/api/students')
def api_students():
    """
    API endpoint: list students as JSON.
    """
    status_filter = request.args.get('status')
    students = list_students(status_filter)
    return jsonify([s.to_dict() for s in students])

@app.route('/api/student/<student_id>')
def api_student_detail(student_id):
    """
    API endpoint: get student detail as JSON.
    """
    student = get_status(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student)

# Template rendering (minimal HTML for demonstration)
# In production, place dashboard.html and student_detail.html in templates/
if not os.path.exists("templates/dashboard.html"):
    with open("templates/dashboard.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Student Evaluation Dashboard</h1>
    <form method="get" action="/search">
        <input type="text" name="q" placeholder="Search by name, email, or ID">
        <button type="submit">Search</button>
    </form>
    <form method="get" action="/">
        <select name="status" onchange="this.form.submit()">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="data_collected">Data Collected</option>
            <option value="pathway_generated">Pathway Generated</option>
            <option value="pdf_sent">PDF Sent</option>
            <option value="sf_uploaded">Salesforce Uploaded</option>
            <option value="completed">Completed</option>
            <option value="error">Error</option>
        </select>
    </form>
    <table border="1">
        <tr>
            <th>ID</th><th>Name</th><th>Email</th><th>Status</th><th>Actions</th>
        </tr>
        {% for student in students %}
        <tr>
            <td>{{ student.student_id }}</td>
            <td>{{ student.name }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.status }}</td>
            <td>
                <a href="{{ url_for('student_detail', student_id=student.student_id) }}">View</a>
                <form method="post" action="{{ url_for('resend', student_id=student.student_id) }}" style="display:inline;">
                    <button type="submit">Resend</button>
                </form>
                <a href="{{ url_for('download_pdf', student_id=student.student_id) }}">Download PDF</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
""")
if not os.path.exists("templates/student_detail.html"):
    with open("templates/student_detail.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Student Detail</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <h1>Student Detail</h1>
    <p><strong>ID:</strong> {{ student.student_id }}</p>
    <p><strong>Name:</strong> {{ student.name }}</p>
    <p><strong>Email:</strong> {{ student.email }}</p>
    <p><strong>Status:</strong> {{ student.status }}</p>
    <p><strong>Academic Pathway:</strong> {{ student.academic_pathway }}</p>
    <p><strong>Salesforce ID:</strong> {{ student.salesforce_id }}</p>
    <p><strong>PDF Path:</strong> {{ student.pdf_path }}</p>
    <form method="post" action="{{ url_for('resend', student_id=student.student_id) }}">
        <button type="submit">Manual Resend</button>
    </form>
    <a href="{{ url_for('download_pdf', student_id=student.student_id) }}">Download PDF</a>
    <a href="{{ url_for('dashboard') }}">Back to Dashboard</a>
</body>
</html>
""")

# Static CSS (minimal)
if not os.path.exists("static/style.css"):
    with open("static/style.css", "w") as f:
        f.write("""
body { font-family: Arial, sans-serif; margin: 20px; }
h1 { color: #2c3e50; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { padding: 8px 12px; border: 1px solid #ccc; }
th { background: #f4f4f4; }
form { margin-bottom: 10px; }
button { padding: 6px 12px; }
""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from fastapi import APIRouter, Depends, HTTPException, Response as FastAPIResponse
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend.models import Survey, Question, Response as SurveyResponse, User
from backend.database import get_db
from backend.api.auth import get_current_user

router = APIRouter()

def generate_pdf_report(survey: Survey, questions, responses):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, f"Survey Report: {survey.title}")
    y -= 30

    # Description
    p.setFont("Helvetica", 12)
    if survey.description:
        p.drawString(40, y, f"Description: {survey.description}")
        y -= 20

    # Questions
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "Questions:")
    y -= 20
    p.setFont("Helvetica", 12)
    for idx, q in enumerate(questions, 1):
        p.drawString(50, y, f"{idx}. {q.text} (Type: {q.type})")
        y -= 18
        if q.options:
            p.drawString(70, y, f"Options: {', '.join(q.options)}")
            y -= 16
        if y < 100:
            p.showPage()
            y = height - 40

    y -= 10
    p.setFont("Helvetica-Bold", 13)
    p.drawString(40, y, "Responses:")
    y -= 20
    p.setFont("Helvetica", 11)
    for resp_idx, resp in enumerate(responses, 1):
        p.drawString(50, y, f"Response #{resp_idx} (User ID: {resp.user_id if resp.user_id else 'Anonymous'})")
        y -= 16
        for q in questions:
            ans = resp.answers.get(str(q.id)) or resp.answers.get(int(q.id))
            p.drawString(70, y, f"{q.text}: {ans}")
            y -= 14
            if y < 100:
                p.showPage()
                y = height - 40
        y -= 6
        if y < 100:
            p.showPage()
            y = height - 40

    p.save()
    buffer.seek(0)
    return buffer

def generate_csv_report(survey: Survey, questions, responses):
    # Prepare data for DataFrame
    data = []
    question_ids = [q.id for q in questions]
    question_texts = [q.text for q in questions]
    for resp in responses:
        row = {
            "response_id": resp.id,
            "user_id": resp.user_id,
            "submitted_at": resp.submitted_at
        }
        for q in questions:
            ans = resp.answers.get(str(q.id)) or resp.answers.get(int(q.id))
            row[q.text] = ans
        data.append(row)
    columns = ["response_id", "user_id", "submitted_at"] + question_texts
    df = pd.DataFrame(data, columns=columns)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

@router.get("/{survey_id}/report/pdf")
def get_pdf_report(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to generate report for this survey")
    questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey.id).all()
    pdf_buffer = generate_pdf_report(survey, questions, responses)
    filename = f"survey_{survey.id}_report.pdf"
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

@router.get("/{survey_id}/report/csv")
def get_csv_report(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to generate report for this survey")
    questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey.id).all()
    csv_buffer = generate_csv_report(survey, questions, responses)
    filename = f"survey_{survey.id}_report.csv"
    return StreamingResponse(csv_buffer, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })
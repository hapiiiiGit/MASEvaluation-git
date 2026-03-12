from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List

from backend.schemas import RadarChartData, HeatmapData
from backend.models import Survey, Question, Response, User, QuestionType
from backend.database import get_db
from backend.api.auth import get_current_user

router = APIRouter()

def compute_radar_data(survey: Survey, responses: List[Response]) -> Dict:
    # For radar chart, let's assume we aggregate numeric/rating answers per question
    labels = []
    data = []
    for question in survey.questions:
        if question.type in [QuestionType.rating, QuestionType.number]:
            labels.append(question.text)
            # Collect all answers for this question
            values = []
            for response in responses:
                answer = response.answers.get(str(question.id)) or response.answers.get(int(question.id))
                if isinstance(answer, (int, float)):
                    values.append(float(answer))
            avg = sum(values) / len(values) if values else 0
            data.append(avg)
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Average Score",
                "data": data,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 2,
            }
        ]
    }

def compute_heatmap_data(survey: Survey, responses: List[Response]) -> Dict:
    # For heatmap, let's assume we show frequency of answers for each choice question
    x_labels = []
    y_labels = []
    data_matrix = []

    # Find all single/multiple choice questions
    choice_questions = [q for q in survey.questions if q.type in [QuestionType.single_choice, QuestionType.multiple_choice]]
    if not choice_questions:
        return {
            "x_labels": [],
            "y_labels": [],
            "data": []
        }

    # x_labels: question text
    x_labels = [q.text for q in choice_questions]
    # y_labels: all possible options (union of all options)
    all_options = set()
    for q in choice_questions:
        if q.options:
            all_options.update(q.options)
    y_labels = list(all_options)

    # Build matrix: rows=options, cols=questions
    for option in y_labels:
        row = []
        for question in choice_questions:
            count = 0
            for response in responses:
                answer = response.answers.get(str(question.id)) or response.answers.get(int(question.id))
                if question.type == QuestionType.single_choice:
                    if answer == option:
                        count += 1
                elif question.type == QuestionType.multiple_choice:
                    if isinstance(answer, list) and option in answer:
                        count += 1
            row.append(count)
        data_matrix.append(row)

    return {
        "x_labels": x_labels,
        "y_labels": y_labels,
        "data": data_matrix
    }

@router.get("/{survey_id}/analytics/radar", response_model=RadarChartData)
def get_radar_chart_data(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    survey.questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    responses = db.query(Response).filter(Response.survey_id == survey_id).all()
    radar_data = compute_radar_data(survey, responses)
    return radar_data

@router.get("/{survey_id}/analytics/heatmap", response_model=HeatmapData)
def get_heatmap_data(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    survey.questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    responses = db.query(Response).filter(Response.survey_id == survey_id).all()
    heatmap_data = compute_heatmap_data(survey, responses)
    return heatmap_data
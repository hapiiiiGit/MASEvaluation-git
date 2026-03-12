from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.schemas import SurveyCreate, SurveyResponse, SurveyUpdate
from backend.models import Survey, Question, User
from backend.database import get_db
from backend.api.auth import get_current_user

router = APIRouter()

# Create a new survey
@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
def create_survey(
    survey: SurveyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_survey = Survey(
        title=survey.title,
        description=survey.description,
        created_by=current_user.id
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)

    # Add questions
    for q in survey.questions:
        db_question = Question(
            survey_id=db_survey.id,
            text=q.text,
            type=q.type,
            options=q.options
        )
        db.add(db_question)
    db.commit()
    db.refresh(db_survey)
    # Reload questions
    db_survey.questions = db.query(Question).filter(Question.survey_id == db_survey.id).all()
    return db_survey

# Get all surveys
@router.get("/", response_model=List[SurveyResponse])
def list_surveys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    surveys = db.query(Survey).all()
    for survey in surveys:
        survey.questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    return surveys

# Get a single survey by ID
@router.get("/{survey_id}", response_model=SurveyResponse)
def get_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    survey.questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    return survey

# Update a survey
@router.put("/{survey_id}", response_model=SurveyResponse)
def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this survey")

    if survey_update.title is not None:
        survey.title = survey_update.title
    if survey_update.description is not None:
        survey.description = survey_update.description
    db.commit()

    # Update questions if provided
    if survey_update.questions is not None:
        for q_update in survey_update.questions:
            question = db.query(Question).filter(
                Question.survey_id == survey_id,
                Question.id == q_update.id
            ).first()
            if question:
                if q_update.text is not None:
                    question.text = q_update.text
                if q_update.type is not None:
                    question.type = q_update.type
                if q_update.options is not None:
                    question.options = q_update.options
        db.commit()
    survey.questions = db.query(Question).filter(Question.survey_id == survey.id).all()
    return survey

# Delete a survey
@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    if survey.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this survey")
    db.delete(survey)
    db.commit()
    return None
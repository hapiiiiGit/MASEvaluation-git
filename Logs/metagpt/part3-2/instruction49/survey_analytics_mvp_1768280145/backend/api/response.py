from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.schemas import ResponseCreate, ResponseResponse
from backend.models import Response, Survey, User
from backend.database import get_db
from backend.api.auth import get_current_user

router = APIRouter()

# Submit a response to a survey
@router.post("/{survey_id}/response", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
def submit_response(
    survey_id: int,
    response: ResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    db_response = Response(
        survey_id=survey_id,
        user_id=current_user.id if current_user else None,
        answers=response.answers
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

# Get all responses for a survey
@router.get("/{survey_id}/responses", response_model=List[ResponseResponse])
def list_responses(
    survey_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Only allow survey creator or admin to view all responses
    if survey.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view responses for this survey")

    responses = db.query(Response).filter(Response.survey_id == survey_id).all()
    return responses

# Get a single response by ID
@router.get("/{survey_id}/response/{response_id}", response_model=ResponseResponse)
def get_response(
    survey_id: int,
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = db.query(Response).filter(Response.id == response_id, Response.survey_id == survey_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")

    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Only allow survey creator, admin, or the user who submitted the response to view
    if (
        survey.created_by != current_user.id
        and current_user.role != "admin"
        and response.user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this response")

    return response
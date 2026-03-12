from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from schemas import FundDetailsRead, ErrorResponse
from utils.security import get_db, get_current_user_from_token
from services.fund_service import get_fund_details_for_user, update_fund_details_for_user
from utils.error_handlers import handle_fund_error

router = APIRouter()

@router.get(
    "/details",
    response_model=FundDetailsRead,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_fund_details(
    token: str = Query(..., description="Session token"),
    db: Session = Depends(get_db)
):
    """
    Retrieve the fund details for the authenticated user via mStock Type A User APIs.
    """
    try:
        user = get_current_user_from_token(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token.")
        fund_details = get_fund_details_for_user(db, user.id)
        if not fund_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund details not found.")
        return fund_details
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_fund_error(e)

@router.post(
    "/details",
    response_model=FundDetailsRead,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_fund_details(
    token: str = Query(..., description="Session token"),
    db: Session = Depends(get_db)
):
    """
    Update and return the latest fund details for the authenticated user via mStock Type A User APIs.
    """
    try:
        user = get_current_user_from_token(db, token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token.")
        fund_details = update_fund_details_for_user(db, user.id)
        if not fund_details:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fund details not found.")
        return fund_details
    except HTTPException as e:
        raise e
    except Exception as e:
        raise handle_fund_error(e)
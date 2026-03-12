from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from models import FundDetails, User
from schemas import FundDetailsRead
from services.mstock_client import mstock_get_fund_details
from utils.logger import logger

def get_fund_details_for_user(db: Session, user_id: int) -> FundDetailsRead:
    """
    Retrieve fund details for a user from the local database.
    If not present, fetch from mStock and store locally.
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        logger.warning(f"Fund details fetch failed: User ID '{user_id}' not found or inactive.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    fund_details = db.query(FundDetails).filter(FundDetails.user_id == user_id).first()
    if fund_details:
        logger.info(f"Fund details retrieved from DB for user_id={user_id}")
        return FundDetailsRead(
            user_id=fund_details.user_id,
            balance=fund_details.balance,
            currency=fund_details.currency,
            last_updated=fund_details.last_updated,
        )

    # If not in DB, fetch from mStock
    mstock_data = mstock_get_fund_details(user_id)
    if not mstock_data.get("success"):
        logger.error(f"mStock fund details fetch failed for user_id={user_id}: {mstock_data.get('error')}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to fetch fund details from mStock.")

    fund_details = FundDetails(
        user_id=user_id,
        balance=mstock_data["balance"],
        currency=mstock_data.get("currency", "USD"),
        last_updated=datetime.utcnow(),
    )
    db.add(fund_details)
    db.commit()
    db.refresh(fund_details)
    logger.info(f"Fund details fetched from mStock and stored for user_id={user_id}")
    return FundDetailsRead(
        user_id=fund_details.user_id,
        balance=fund_details.balance,
        currency=fund_details.currency,
        last_updated=fund_details.last_updated,
    )

def update_fund_details_for_user(db: Session, user_id: int) -> FundDetailsRead:
    """
    Update fund details for a user by fetching the latest data from mStock and updating the local database.
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        logger.warning(f"Fund details update failed: User ID '{user_id}' not found or inactive.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    mstock_data = mstock_get_fund_details(user_id)
    if not mstock_data.get("success"):
        logger.error(f"mStock fund details update failed for user_id={user_id}: {mstock_data.get('error')}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to update fund details from mStock.")

    fund_details = db.query(FundDetails).filter(FundDetails.user_id == user_id).first()
    if not fund_details:
        fund_details = FundDetails(
            user_id=user_id,
            balance=mstock_data["balance"],
            currency=mstock_data.get("currency", "USD"),
            last_updated=datetime.utcnow(),
        )
        db.add(fund_details)
    else:
        fund_details.balance = mstock_data["balance"]
        fund_details.currency = mstock_data.get("currency", "USD")
        fund_details.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(fund_details)
    logger.info(f"Fund details updated from mStock for user_id={user_id}")
    return FundDetailsRead(
        user_id=fund_details.user_id,
        balance=fund_details.balance,
        currency=fund_details.currency,
        last_updated=fund_details.last_updated,
    )
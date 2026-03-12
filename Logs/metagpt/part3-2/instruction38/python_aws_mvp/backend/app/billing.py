import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict
from .models import User
from .config import get_settings
from .auth import get_current_user

settings = get_settings()

# Initialize Stripe client
stripe.api_key = settings.STRIPE_API_KEY

# In-memory store for MVP (replace with DB in production)
fake_stripe_customers: Dict[str, str] = {}  # user_id -> stripe_customer_id
fake_subscriptions: Dict[str, str] = {}     # user_id -> stripe_subscription_id
fake_usage_records: Dict[str, float] = {}   # user_id -> usage

class CreateSubscriptionRequest(BaseModel):
    plan_id: str

class MeterUsageRequest(BaseModel):
    usage: float

class InvoiceResponse(BaseModel):
    invoice_id: str
    amount_due: int
    status: str
    hosted_invoice_url: Optional[str] = None

class BillingManager:
    @staticmethod
    def create_customer(user_id: str) -> str:
        if user_id in fake_stripe_customers:
            return fake_stripe_customers[user_id]
        try:
            customer = stripe.Customer.create(
                metadata={"user_id": user_id}
            )
            fake_stripe_customers[user_id] = customer.id
            return customer.id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stripe customer creation failed: {str(e)}"
            )

    @staticmethod
    def create_subscription(user_id: str, plan_id: str) -> str:
        customer_id = BillingManager.create_customer(user_id)
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": plan_id}],
                expand=["latest_invoice.payment_intent"]
            )
            fake_subscriptions[user_id] = subscription.id
            return subscription.id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stripe subscription creation failed: {str(e)}"
            )

    @staticmethod
    def meter_usage(user_id: str, usage: float) -> None:
        customer_id = BillingManager.create_customer(user_id)
        fake_usage_records[user_id] = fake_usage_records.get(user_id, 0.0) + usage
        # For MVP, we simulate usage metering. In production, use Stripe Usage Records API.
        # Example: stripe.UsageRecord.create(...)
        # Here, we just record usage in memory.

    @staticmethod
    def get_invoice(user_id: str) -> Dict:
        customer_id = BillingManager.create_customer(user_id)
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=1)
            if not invoices.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No invoices found for user"
                )
            invoice = invoices.data[0]
            return {
                "invoice_id": invoice.id,
                "amount_due": invoice.amount_due,
                "status": invoice.status,
                "hosted_invoice_url": invoice.hosted_invoice_url
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Stripe invoice retrieval failed: {str(e)}"
            )

# FastAPI router for billing
billing_router = APIRouter()

@billing_router.post("/create-customer", summary="Create Stripe customer for user")
async def create_customer(current_user: User = Depends(get_current_user)):
    customer_id = BillingManager.create_customer(current_user.user_id)
    return {"stripe_customer_id": customer_id}

@billing_router.post("/create-subscription", summary="Create Stripe subscription for user")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    subscription_id = BillingManager.create_subscription(current_user.user_id, request.plan_id)
    return {"stripe_subscription_id": subscription_id}

@billing_router.post("/meter-usage", summary="Record metered usage for user")
async def meter_usage(
    request: MeterUsageRequest,
    current_user: User = Depends(get_current_user)
):
    BillingManager.meter_usage(current_user.user_id, request.usage)
    return {"status": "usage recorded", "usage": request.usage}

@billing_router.get("/invoice", response_model=InvoiceResponse, summary="Get latest invoice for user")
async def get_invoice(current_user: User = Depends(get_current_user)):
    invoice = BillingManager.get_invoice(current_user.user_id)
    return InvoiceResponse(**invoice)

def get_billing_router():
    return billing_router
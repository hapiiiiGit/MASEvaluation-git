import os
import stripe
from datetime import datetime
from src.models import db, Transaction, User, Item

class PaymentProcessor:
    def __init__(self):
        self.stripe_api_key = os.getenv('STRIPE_API_KEY')
        stripe.api_key = self.stripe_api_key

    def process_payment(self, user: User, item: Item) -> Transaction:
        """
        Processes payment for the given user and item using Stripe.
        Returns a Transaction object (saved to DB).
        """
        try:
            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(item.price * 100),  # Stripe expects amount in cents
                currency='usd',
                metadata={
                    'user_id': user.id,
                    'item_id': item.id,
                    'roblox_username': user.roblox_username
                },
                description=f'Purchase of {item.name} by {user.username}'
            )

            # Simulate payment confirmation for server-side flow
            # In production, you'd handle client-side confirmation
            payment_confirmed = intent['status'] == 'requires_payment_method' or intent['status'] == 'succeeded'

            status = 'success' if payment_confirmed else 'failed'
            transaction = Transaction(
                user_id=user.id,
                item_id=item.id,
                amount=item.price,
                status=status,
                payment_provider='stripe',
                delivery_proof_url=None
            )
            db.session.add(transaction)
            db.session.commit()
            return transaction
        except Exception as e:
            transaction = Transaction(
                user_id=user.id,
                item_id=item.id,
                amount=item.price,
                status='failed',
                payment_provider='stripe',
                delivery_proof_url=None
            )
            db.session.add(transaction)
            db.session.commit()
            return transaction

    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verifies payment status for a given Stripe PaymentIntent ID.
        Returns True if payment is successful, False otherwise.
        """
        try:
            intent = stripe.PaymentIntent.retrieve(transaction_id)
            return intent['status'] == 'succeeded'
        except Exception:
            return False
import os
import pytest
from unittest.mock import patch, MagicMock

from src.models import db, User, Item, Transaction
from src.payment import PaymentProcessor

import tempfile
from flask import Flask

# Helper to create a Flask app and initialize the DB for testing
@pytest.fixture(scope='module')
def test_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'testsecret'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()

@pytest.fixture
def test_user(session):
    user = User(
        username='testuser',
        email='testuser@example.com',
        password_hash='hashedpassword',
        roblox_username='roblox_test',
        private_server_info='private_server_123'
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def test_item(session):
    item = Item(
        name='Test Item',
        description='A test item for purchase.',
        price=9.99,
        roblox_asset_id='asset_123'
    )
    session.add(item)
    session.commit()
    return item

@pytest.fixture
def payment_processor():
    # Patch stripe.api_key to avoid real API calls
    with patch('src.payment.stripe') as mock_stripe:
        mock_stripe.api_key = 'sk_test_dummy'
        yield PaymentProcessor()

def test_process_payment_success(payment_processor, test_user, test_item, session):
    # Mock Stripe PaymentIntent.create to simulate success
    with patch('src.payment.stripe.PaymentIntent.create') as mock_create:
        mock_create.return_value = {
            'status': 'succeeded'
        }
        transaction = payment_processor.process_payment(test_user, test_item)
        assert transaction.status == 'success'
        assert transaction.amount == test_item.price
        assert transaction.payment_provider == 'stripe'
        assert transaction.user_id == test_user.id
        assert transaction.item_id == test_item.id

def test_process_payment_failure(payment_processor, test_user, test_item, session):
    # Mock Stripe PaymentIntent.create to raise an exception
    with patch('src.payment.stripe.PaymentIntent.create', side_effect=Exception("Stripe error")):
        transaction = payment_processor.process_payment(test_user, test_item)
        assert transaction.status == 'failed'
        assert transaction.amount == test_item.price
        assert transaction.payment_provider == 'stripe'
        assert transaction.user_id == test_user.id
        assert transaction.item_id == test_item.id

def test_verify_payment_success(payment_processor):
    # Mock Stripe PaymentIntent.retrieve to simulate success
    with patch('src.payment.stripe.PaymentIntent.retrieve') as mock_retrieve:
        mock_retrieve.return_value = {'status': 'succeeded'}
        assert payment_processor.verify_payment('pi_test_success') is True

def test_verify_payment_failure(payment_processor):
    # Mock Stripe PaymentIntent.retrieve to simulate failure
    with patch('src.payment.stripe.PaymentIntent.retrieve') as mock_retrieve:
        mock_retrieve.return_value = {'status': 'requires_payment_method'}
        assert payment_processor.verify_payment('pi_test_fail') is False

def test_verify_payment_exception(payment_processor):
    # Mock Stripe PaymentIntent.retrieve to raise an exception
    with patch('src.payment.stripe.PaymentIntent.retrieve', side_effect=Exception("Stripe error")):
        assert payment_processor.verify_payment('pi_test_exception') is False
import os
import pytest
from unittest.mock import patch, MagicMock

from src.models import User, Item, Transaction
from src.roblox_bot import RobloxBot

@pytest.fixture
def test_user():
    return User(
        username='testuser',
        email='testuser@example.com',
        password_hash='hashedpassword',
        roblox_username='roblox_test',
        private_server_info='private_server_123'
    )

@pytest.fixture
def test_item():
    return Item(
        name='Test Item',
        description='A test item for purchase.',
        price=9.99,
        roblox_asset_id='asset_123'
    )

@pytest.fixture
def test_transaction(test_user, test_item):
    return Transaction(
        user_id=1,
        item_id=1,
        amount=test_item.price,
        status='delivered',
        payment_provider='stripe',
        delivery_proof_url='https://proof.example.com/proof123'
    )

@pytest.fixture
def roblox_bot():
    return RobloxBot()

def test_deliver_item_success(roblox_bot, test_user, test_item):
    # Mock requests.post to simulate successful delivery
    with patch('src.roblox_bot.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"delivery_proof_url": "https://proof.example.com/proof123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        proof_url = roblox_bot.deliver_item(test_user, test_item)
        assert proof_url == "https://proof.example.com/proof123"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['roblox_username'] == test_user.roblox_username
        assert kwargs['json']['asset_id'] == test_item.roblox_asset_id
        assert kwargs['json']['private_server_info'] == test_user.private_server_info

def test_deliver_item_failure(roblox_bot, test_user, test_item):
    # Mock requests.post to simulate failed delivery (exception)
    with patch('src.roblox_bot.requests.post', side_effect=Exception("Bot error")):
        proof_url = roblox_bot.deliver_item(test_user, test_item)
        assert proof_url == ""

def test_get_delivery_proof(roblox_bot, test_transaction):
    proof_url = roblox_bot.get_delivery_proof(test_transaction)
    assert proof_url == "https://proof.example.com/proof123"

def test_get_delivery_proof_empty(roblox_bot):
    # Transaction with no delivery_proof_url
    tx = Transaction(
        user_id=1,
        item_id=1,
        amount=9.99,
        status='delivered',
        payment_provider='stripe',
        delivery_proof_url=None
    )
    proof_url = roblox_bot.get_delivery_proof(tx)
    assert proof_url == ""
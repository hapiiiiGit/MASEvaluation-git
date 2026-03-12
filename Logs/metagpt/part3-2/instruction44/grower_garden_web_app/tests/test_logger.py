import os
import pytest
from unittest.mock import patch, MagicMock

from src.models import Transaction
from src.discord_logger import DiscordLogger

@pytest.fixture
def test_transaction():
    return Transaction(
        user_id=1,
        item_id=2,
        amount=19.99,
        status='delivered',
        payment_provider='stripe',
        delivery_proof_url='https://proof.example.com/proof456'
    )

@pytest.fixture
def discord_logger():
    # Patch os.getenv to provide a dummy webhook URL
    with patch('src.discord_logger.os.getenv', return_value='https://discord.com/api/webhooks/test_webhook'):
        yield DiscordLogger()

def test_log_transaction_success(discord_logger, test_transaction):
    # Patch requests.post to simulate successful Discord webhook call
    with patch('src.discord_logger.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        discord_logger.log_transaction(test_transaction)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['username'] == "Grower Garden Bot"
        assert 'embeds' in kwargs['json']
        embed = kwargs['json']['embeds'][0]
        assert embed['title'] == "New Transaction"
        assert any(field['name'] == "User ID" and field['value'] == str(test_transaction.user_id) for field in embed['fields'])

def test_log_transaction_no_webhook(test_transaction):
    # DiscordLogger with no webhook URL should not call requests.post
    with patch('src.discord_logger.os.getenv', return_value=''):
        logger = DiscordLogger()
        with patch('src.discord_logger.requests.post') as mock_post:
            logger.log_transaction(test_transaction)
            mock_post.assert_not_called()

def test_log_delivery_proof_success(discord_logger, test_transaction):
    # Patch requests.post to simulate successful Discord webhook call
    with patch('src.discord_logger.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response

        proof_url = test_transaction.delivery_proof_url
        discord_logger.log_delivery_proof(test_transaction, proof_url)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['username'] == "Grower Garden Bot"
        assert 'embeds' in kwargs['json']
        embed = kwargs['json']['embeds'][0]
        assert embed['title'] == "Delivery Proof"
        assert any(field['name'] == "Delivery Proof URL" and field['value'] == proof_url for field in embed['fields'])

def test_log_delivery_proof_no_webhook(test_transaction):
    # DiscordLogger with no webhook URL should not call requests.post
    with patch('src.discord_logger.os.getenv', return_value=''):
        logger = DiscordLogger()
        with patch('src.discord_logger.requests.post') as mock_post:
            logger.log_delivery_proof(test_transaction, test_transaction.delivery_proof_url)
            mock_post.assert_not_called()

def test_log_transaction_exception(discord_logger, test_transaction):
    # Patch requests.post to raise an exception, should not propagate
    with patch('src.discord_logger.requests.post', side_effect=Exception("Discord error")):
        discord_logger.log_transaction(test_transaction)  # Should not raise

def test_log_delivery_proof_exception(discord_logger, test_transaction):
    # Patch requests.post to raise an exception, should not propagate
    with patch('src.discord_logger.requests.post', side_effect=Exception("Discord error")):
        discord_logger.log_delivery_proof(test_transaction, test_transaction.delivery_proof_url)  # Should not raise
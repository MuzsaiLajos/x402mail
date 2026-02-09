"""Tests for x402mail client."""

from unittest.mock import MagicMock, patch

import pytest

FAKE_KEY = "0x" + "ab" * 32


@pytest.fixture
def mock_session():
    """Patch the entire x402 client chain and return the mock session."""
    with (
        patch("x402mail.client.x402_requests") as mock_factory,
        patch("x402mail.client.x402ClientSync"),
        patch("x402mail.client.ExactEvmScheme"),
        patch("x402mail.client.EthAccountSigner"),
    ):
        session = MagicMock()
        mock_factory.return_value = session
        yield session


@pytest.fixture
def client(mock_session):
    from x402mail.client import X402Mail
    return X402Mail(private_key=FAKE_KEY)


def _json_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    resp.raise_for_status.return_value = None
    return resp


class TestSend:
    def test_send_basic(self, client, mock_session):
        mock_session.post.return_value = _json_response(
            {"message_id": "abc-123", "inbox": "inbox-0xab@x402mail.com"}
        )
        result = client.send(to="alice@example.com", subject="Hi", body="Hello")

        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert "/api/v1/send" in call_args[0][0]
        assert call_args[1]["json"]["to"] == "alice@example.com"
        assert result["message_id"] == "abc-123"

    def test_send_with_reply(self, client, mock_session):
        mock_session.post.return_value = _json_response({"message_id": "x"})
        client.send(
            to="bob@test.com",
            subject="Re: Hi",
            body="Reply",
            reply_to="bob@test.com",
            reply_to_message_id=42,
        )
        payload = mock_session.post.call_args[1]["json"]
        assert payload["reply_to"] == "bob@test.com"
        assert payload["reply_to_message_id"] == 42


class TestInbox:
    def test_inbox(self, client, mock_session):
        mock_session.get.return_value = _json_response(
            {"inbox": "inbox-0xab@x402mail.com", "total": 5, "unread": 2}
        )
        result = client.inbox()
        assert result["unread"] == 2
        assert "/api/v1/inbox" in mock_session.get.call_args[0][0]


class TestMessages:
    def test_messages_default(self, client, mock_session):
        mock_session.get.return_value = _json_response([{"id": 1, "subject": "Test"}])
        result = client.messages()
        assert len(result) == 1
        params = mock_session.get.call_args[1]["params"]
        assert params["limit"] == 10
        assert params["unread_only"] == "false"

    def test_messages_unread_only(self, client, mock_session):
        mock_session.get.return_value = _json_response([])
        client.messages(limit=5, unread_only=True)
        params = mock_session.get.call_args[1]["params"]
        assert params["limit"] == 5
        assert params["unread_only"] == "true"


class TestRead:
    def test_read_message(self, client, mock_session):
        mock_session.get.return_value = _json_response(
            {"id": 7, "from": "sender@test.com", "subject": "Hello", "body": "World"}
        )
        result = client.read(message_id=7)
        assert result["body"] == "World"
        assert "/api/v1/inbox/messages/7" in mock_session.get.call_args[0][0]

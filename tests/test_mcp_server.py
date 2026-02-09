"""Tests for x402mail MCP server."""

from unittest.mock import MagicMock, patch

import pytest

FAKE_KEY = "0x" + "ab" * 32


@pytest.fixture(autouse=True)
def reset_client():
    """Reset the global client between tests."""
    import x402mail.mcp_server as mod
    mod._client = None
    yield
    mod._client = None


@pytest.fixture
def mock_x402mail():
    with patch("x402mail.mcp_server.X402Mail") as MockClass:
        instance = MagicMock()
        MockClass.return_value = instance
        yield instance


@pytest.fixture
def env_key(monkeypatch):
    monkeypatch.setenv("X402MAIL_PRIVATE_KEY", FAKE_KEY)


class TestGetClient:
    def test_missing_key_raises(self, monkeypatch):
        monkeypatch.delenv("X402MAIL_PRIVATE_KEY", raising=False)
        from x402mail.mcp_server import _get_client
        with pytest.raises(RuntimeError, match="X402MAIL_PRIVATE_KEY"):
            _get_client()

    def test_creates_client_with_key(self, env_key, mock_x402mail):
        from x402mail.mcp_server import _get_client, X402Mail
        client = _get_client()
        X402Mail.assert_called_once_with(private_key=FAKE_KEY, _server_url=None)


class TestTools:
    def test_send_email(self, env_key, mock_x402mail):
        from x402mail.mcp_server import send_email
        mock_x402mail.send.return_value = {"message_id": "x"}
        result = send_email(to="a@b.com", subject="Hi", body="Hey")
        mock_x402mail.send.assert_called_once_with(
            to="a@b.com", subject="Hi", body="Hey",
            reply_to=None, reply_to_message_id=None,
        )
        assert result["message_id"] == "x"

    def test_get_inbox(self, env_key, mock_x402mail):
        from x402mail.mcp_server import get_inbox
        mock_x402mail.inbox.return_value = {"address": "x", "total": 1, "unread": 0}
        result = get_inbox()
        assert result["total"] == 1

    def test_list_messages(self, env_key, mock_x402mail):
        from x402mail.mcp_server import list_messages
        mock_x402mail.messages.return_value = [{"id": 1}]
        result = list_messages(limit=5, unread_only=True)
        mock_x402mail.messages.assert_called_once_with(limit=5, unread_only=True)
        assert len(result) == 1

    def test_read_message(self, env_key, mock_x402mail):
        from x402mail.mcp_server import read_message
        mock_x402mail.read.return_value = {"body": "content"}
        result = read_message(message_id=42)
        mock_x402mail.read.assert_called_once_with(42)
        assert result["body"] == "content"

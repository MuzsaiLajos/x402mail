"""Local MCP stdio server that wraps x402mail SDK.

Handles x402 payments internally so the LLM just sees simple tools.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from x402mail.client import X402Mail

mcp = FastMCP(
    name="x402mail",
    instructions=(
        "Email tools powered by x402 micropayments. "
        "Send emails, check your inbox, and read messages. "
        "Your inbox address is derived from your wallet."
    ),
)

_client: X402Mail | None = None


def _get_client() -> X402Mail:
    global _client
    if _client is None:
        key = os.environ.get("X402MAIL_PRIVATE_KEY")
        if not key:
            raise RuntimeError(
                "X402MAIL_PRIVATE_KEY environment variable is required. "
                "Set it to your Ethereum private key (0x...)."
            )
        server_url = os.environ.get("X402MAIL_SERVER_URL")  # undocumented, for dev
        _client = X402Mail(private_key=key, _server_url=server_url)
    return _client


@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    reply_to: str | None = None,
    reply_to_message_id: int | None = None,
) -> dict:
    """Send an email. Costs ~$0.005 in USDC.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text or HTML)
        reply_to: Optional reply-to address
        reply_to_message_id: Optional message ID to reply to (for threading)

    Returns:
        message_id and your inbox address
    """
    client = _get_client()
    return client.send(
        to=to,
        subject=subject,
        body=body,
        reply_to=reply_to,
        reply_to_message_id=reply_to_message_id,
    )


@mcp.tool()
def get_inbox() -> dict:
    """Get your inbox address and message counts. Costs ~$0.001 in USDC.

    Returns:
        Your inbox address, total message count, and unread count
    """
    return _get_client().inbox()


@mcp.tool()
def list_messages(limit: int = 10, unread_only: bool = False) -> list[dict]:
    """List inbox messages. Costs ~$0.002 in USDC.

    Args:
        limit: Max messages to return (default 10)
        unread_only: Only show unread messages

    Returns:
        List of messages with id, from, subject, preview, received_at, is_read
    """
    return _get_client().messages(limit=limit, unread_only=unread_only)


@mcp.tool()
def read_message(message_id: int) -> dict:
    """Read a specific message by ID. Marks it as read. Costs ~$0.001 in USDC.

    Args:
        message_id: The ID of the message to read

    Returns:
        Full message with from, subject, body, received_at
    """
    return _get_client().read(message_id)


def run():
    """Start the MCP stdio server."""
    mcp.run()

"""Synchronous x402mail client using requests + automatic x402 payment."""

from __future__ import annotations

from eth_account import Account
from x402 import x402ClientSync
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.evm.signers import EthAccountSigner
from x402.http.clients.requests import x402_requests

_DEFAULT_SERVER = "https://x402mail.com"


class X402Mail:
    """Send and receive emails via x402mail.

    Usage::

        from x402mail import X402Mail

        mail = X402Mail(private_key="0x...")
        mail.send(to="alice@example.com", subject="Hi", body="Hello!")
    """

    def __init__(self, private_key: str, *, _server_url: str | None = None):
        account = Account.from_key(private_key)
        signer = EthAccountSigner(account)
        client = x402ClientSync()
        client.register("eip155:8453", ExactEvmScheme(signer=signer))
        self._base = (_server_url or _DEFAULT_SERVER).rstrip("/")
        self._session = x402_requests(client)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        *,
        reply_to: str | None = None,
        reply_to_message_id: int | None = None,
    ) -> dict:
        """Send an email. Returns {"message_id": ..., "inbox": ...}."""
        payload = {"to": to, "subject": subject, "body": body}
        if reply_to:
            payload["reply_to"] = reply_to
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id
        resp = self._session.post(f"{self._base}/api/v1/send", json=payload)
        resp.raise_for_status()
        return resp.json()

    def inbox(self) -> dict:
        """Get inbox info. Returns {"inbox": ..., "total": N, "unread": N}."""
        resp = self._session.get(f"{self._base}/api/v1/inbox")
        resp.raise_for_status()
        return resp.json()

    def messages(self, *, limit: int = 10, unread_only: bool = False) -> list[dict]:
        """List inbox messages."""
        params = {"limit": limit, "unread_only": str(unread_only).lower()}
        resp = self._session.get(
            f"{self._base}/api/v1/inbox/messages", params=params
        )
        resp.raise_for_status()
        return resp.json()

    def read(self, message_id: int) -> dict:
        """Read a specific message by ID. Marks it as read."""
        resp = self._session.get(
            f"{self._base}/api/v1/inbox/messages/{message_id}"
        )
        resp.raise_for_status()
        return resp.json()

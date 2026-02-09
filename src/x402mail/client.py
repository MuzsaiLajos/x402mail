"""Synchronous x402mail client using requests + automatic x402 payment."""

from __future__ import annotations

import asyncio

from eth_account import Account
from x402 import x402ClientSync
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.evm.signers import EthAccountSigner
from x402.http.clients.requests import x402_requests

_DEFAULT_SERVER = "https://x402mail.com"


class X402Mail:
    """Send and receive emails via x402mail.

    Usage::

        # Option A: private key
        mail = X402Mail(private_key="0x...")

        # Option B: CDP Server Wallet (pip install x402mail[cdp])
        mail = X402Mail.from_cdp()

        mail.send(to="alice@example.com", subject="Hi", body="Hello!")
    """

    def __init__(self, private_key: str, *, _server_url: str | None = None):
        account = Account.from_key(private_key)
        self._init(account, _server_url)

    def _init(self, account, _server_url: str | None = None):
        signer = EthAccountSigner(account)
        self._address = signer.address
        client = x402ClientSync()
        client.register("eip155:8453", ExactEvmScheme(signer=signer))
        self._base = (_server_url or _DEFAULT_SERVER).rstrip("/")
        self._session = x402_requests(client)

    @classmethod
    def from_cdp(cls, *, _server_url: str | None = None) -> X402Mail:
        """Create client using CDP Server Wallet (no private key needed).

        Requires env vars: CDP_API_KEY_ID, CDP_API_KEY_SECRET, CDP_WALLET_SECRET.
        Install with: pip install x402mail[cdp]
        """
        try:
            from cdp import CdpClient, EvmLocalAccount
        except ImportError:
            raise ImportError(
                "CDP support requires cdp-sdk. Install with: pip install x402mail[cdp]"
            )

        async def _setup():
            cdp = CdpClient()
            return await cdp.evm.get_or_create_account(name="x402mail")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Inside an async context — nest_asyncio (from cdp) handles this
            import nest_asyncio
            nest_asyncio.apply(loop)
            server_account = loop.run_until_complete(_setup())
        else:
            server_account = asyncio.run(_setup())
        local_account = EvmLocalAccount(server_account)

        instance = cls.__new__(cls)
        instance._init(local_account, _server_url)
        return instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def address(self) -> str:
        """The wallet address used for payments."""
        return self._address

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

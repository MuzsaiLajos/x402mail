# x402mail

Send and receive emails with crypto micropayments. No accounts, no API keys — just a wallet.

Built on the [x402 protocol](https://www.x402.org/) — every API call is paid with USDC on Base.

## Install

```bash
pip install x402mail[cdp]
```

## Quick Start

```bash
export CDP_API_KEY_ID="your-key-id"          # from cdp.coinbase.com
export CDP_API_KEY_SECRET="your-key-secret"
export CDP_WALLET_SECRET="your-wallet-secret"
```

```python
from x402mail import X402Mail

mail = X402Mail.from_cdp()   # wallet created automatically
print(mail.address)          # fund this with USDC on Base

# Send an email ($0.005 USDC)
result = mail.send(
    to="alice@example.com",
    subject="Hello from x402mail",
    body="Sent with 3 lines of Python!"
)
print(result)
# {"message_id": "abc-123", "inbox": "inbox-0x1a2b...@x402mail.com"}

# Check your inbox ($0.001)
inbox = mail.inbox()
# {"inbox": "inbox-0x1a2b...@x402mail.com", "total": 5, "unread": 2}

# List messages ($0.002)
messages = mail.messages(limit=5, unread_only=True)

# Read a message ($0.001)
if messages:
    msg = mail.read(message_id=messages[0]["id"])
    print(msg["body"])
```

Or with a private key: `X402Mail(private_key=os.getenv("EVM_PRIVATE_KEY"))`

## MCP Server for AI Agents

Run a local MCP server so LLMs (Claude, GPT, etc.) can send and receive emails:

```bash
x402mail mcp
```

Add to your MCP config (Claude Desktop / Cursor / Claude Code):

```json
{
  "mcpServers": {
    "x402mail": {
      "command": "x402mail",
      "args": ["mcp"],
      "env": {
        "CDP_API_KEY_ID": "your-key-id",
        "CDP_API_KEY_SECRET": "your-key-secret",
        "CDP_WALLET_SECRET": "your-wallet-secret"
      }
    }
  }
}
```

### MCP Tools

| Tool | Cost | Description |
|------|------|-------------|
| `send_email` | $0.005 | Send an email to any address |
| `get_inbox` | $0.001 | Get your inbox address and message counts |
| `list_messages` | $0.002 | List inbox messages |
| `read_message` | $0.001 | Read a specific message |

## Pricing

| Action | Cost |
|--------|------|
| Send email | $0.005 |
| Check inbox | $0.001 |
| List messages | $0.002 |
| Read message | $0.001 |

$1 USDC covers ~200 emails.

## Wallet Setup

**CDP Server Wallet (recommended):** Follow the [CDP quickstart guide](https://docs.cdp.coinbase.com/x402/quickstart-for-buyers) to get API keys. No private keys to manage.

**Private Key:** Use any EVM wallet with USDC on Base. `pip install x402mail` (without `[cdp]`).

## Links

- [Website & Docs](https://x402mail.com/docs)

## License

MIT

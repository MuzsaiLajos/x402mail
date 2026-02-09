# x402mail

Send and receive emails with crypto micropayments. No accounts, no API keys — just a wallet.

Built on the [x402 protocol](https://www.x402.org/) — every API call is paid with USDC on Base via HTTP 402.

## Install

```bash
pip install x402mail
```

## Quick Start

```python
from x402mail import X402Mail

mail = X402Mail(private_key="0x...")

# Send an email ($0.005 USDC)
result = mail.send(
    to="alice@example.com",
    subject="Hello from web3",
    body="Sent via x402 micropayment!"
)
print(result)
# {"message_id": "abc-123", "inbox": "inbox-0x1a2b...@x402mail.com"}

# Check your inbox ($0.001)
inbox = mail.inbox()
# {"inbox": "inbox-0x1a2b...@x402mail.com", "total": 5, "unread": 2}

# List messages ($0.002)
messages = mail.messages(limit=5, unread_only=True)

# Read a message ($0.001)
msg = mail.read(message_id=1)
print(msg["body"])
```

## MCP Server for AI Agents

Run a local MCP server so LLMs (Claude, GPT, etc.) can send and receive emails:

```bash
x402mail mcp
```

### Claude Desktop / Cursor / Claude Code

Add to your MCP config:

```json
{
  "mcpServers": {
    "x402mail": {
      "command": "uvx",
      "args": ["x402mail", "mcp"],
      "env": {
        "X402MAIL_PRIVATE_KEY": "0x..."
      }
    }
  }
}
```

Or if you installed it with pip:

```json
{
  "mcpServers": {
    "x402mail": {
      "command": "x402mail",
      "args": ["mcp"],
      "env": {
        "X402MAIL_PRIVATE_KEY": "0x..."
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

## How It Works

1. You provide your Ethereum private key (for signing payments)
2. Each API call is paid via [x402](https://www.x402.org/) micropayments in USDC on Base
3. Your wallet address = your identity — no accounts needed
4. Your inbox is derived from your wallet: `inbox-{wallet}@x402mail.com`

```
You → x402mail SDK → x402mail.com API
                         ↓
                    402 Payment Required
                         ↓
         SDK auto-signs USDC payment
                         ↓
                    Email sent ✓
```

## Pricing

All prices in USDC on Base mainnet.

| Action | Cost |
|--------|------|
| Send email | $0.005 |
| Check inbox | $0.001 |
| List messages | $0.002 |
| Read message | $0.001 |

$1 USDC covers ~200 emails.

## Requirements

- Python 3.10+
- An Ethereum wallet with USDC on [Base](https://base.org)

## Links

- [Website & Docs](https://x402mail.com/docs)
- [Server Source](https://github.com/MuzsaiLajos/x402mail-server)

## License

MIT

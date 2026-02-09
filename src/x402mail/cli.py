"""CLI entry point for x402mail."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        from x402mail.mcp_server import run
        run()
    else:
        print("Usage: x402mail mcp")
        print()
        print("Starts a local MCP server (stdio) for LLM integration.")
        print()
        print("Required env vars:")
        print("  X402MAIL_PRIVATE_KEY  Your Ethereum private key (0x...)")
        sys.exit(1)


if __name__ == "__main__":
    main()

# kiprio — Claude Code plugin

Production developer APIs from [kiprio.com](https://kiprio.com), packaged as a Claude Code plugin.

> **Status:** pre-staged scaffold (v0.1.0-prestaged). Not yet published. Reviewed and pushed by the operator after approval queue #118 (kiprio-mcp) clears.

## What you get

A bundle of REST endpoints exposed both as plain HTTPS calls and (optionally) as MCP tools:

| Command | Purpose |
| --- | --- |
| `og` | Open Graph / Twitter Card meta extraction |
| `bizday` | UK business-day calculator (E&W bank holidays) |
| `email-validate` | Syntax + MX + disposable + role-address checks |
| `screenshot` | Full-page website screenshot (PNG / JPEG) |
| `dns` | DNS lookup (A / AAAA / MX / TXT / CNAME) |
| `ssl` | SSL certificate inspection (expiry, chain, ciphers) |
| `redact` | PII redaction (emails, phone, NI, card numbers) |
| `schema` | JSON-LD schema markup generation |
| `qr` | QR code generation (SVG / PNG) |
| `unfurl` | Link preview unfurl |

Full list and live docs at <https://kiprio.com/docs/>.

## Install

```sh
# From the Claude Code plugin marketplace (once published):
/plugin install kiprio
```

Or clone manually for local development:

```sh
git clone https://github.com/ForeverTools/kiprio-plugin
# then in Claude Code:
/plugin install ./kiprio-plugin
```

## Authentication

The free tier works with no key (rate-limited per IP).

For Pro / Business tiers, set `KIPRIO_API_KEY` in your environment. The MCP
server reads it from `${KIPRIO_API_KEY}` and forwards as `X-API-Key`.

Get a key at <https://kiprio.com/signup/>.

## MCP server

This plugin ships an MCP server (`server/kiprio_mcp.py`) so the APIs are
exposed as native tools inside any MCP-compatible agent. The bundled
`.mcp.json` wires it up automatically when the plugin is installed.

If you prefer plain HTTPS, every command also has a stable URL — see the
`endpoint` field in `.claude-plugin/plugin.json`.

## Pricing

- **Free** — no key, modest rate limit, plenty for prototyping
- **Pro** — from $9/mo, raised limits
- **Business** — from $39/mo, higher limits and SLAs
- **Enterprise** — custom, contact `support@kiprio.com`

The per-API rate limits and quotas live on each product's page at <https://kiprio.com>.

## Releasing

This is a pre-staged artifact. To publish:

1. Confirm 10+ PHP cPanel APIs return JSON (job `v1_endpoint_health` writes
   to `v1_endpoint_health` table daily).
2. Mirror the published `mcp_server/kiprio_mcp.py` to `kiprio_plugin/server/`.
3. Bump `version` in `.claude-plugin/plugin.json` (drop `-prestaged`).
4. `gh repo create ForeverTools/kiprio-plugin --public` (or push to existing).
5. Tag a release and submit to the Claude Code plugin marketplace.

Do not publish before approval queue #118 (kiprio-mcp) clears.

## Support

- Issues: <https://github.com/ForeverTools/kiprio-plugin/issues>
- Email: <support@kiprio.com>
- Docs: <https://kiprio.com/docs/>

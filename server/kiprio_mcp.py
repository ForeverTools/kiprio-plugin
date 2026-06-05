"""kiprio MCP Server — exposes kiprio.com developer APIs as MCP tools.

Usage:
    KIPRIO_API_KEY=your_key python kiprio_mcp.py

Or in claude_desktop_config.json / mcp config:
    {
      "mcpServers": {
        "kiprio": {
          "command": "python",
          "args": ["/path/to/kiprio_mcp.py"],
          "env": {"KIPRIO_API_KEY": "your_key"}
        }
      }
    }

Free tier works without an API key for demo-rate-limited endpoints.
Get a free key at https://kiprio.com/docs/
"""
from __future__ import annotations

import base64
import os
import httpx
from mcp.server.fastmcp import FastMCP

BASE = "https://kiprio.com/v1"
API_KEY = os.environ.get("KIPRIO_API_KEY", "")

mcp = FastMCP("kiprio")


def _headers() -> dict:
    h: dict = {"Accept": "application/json"}
    if API_KEY:
        h["X-API-Key"] = API_KEY
    return h


def _get(path: str, **params) -> dict:
    r = httpx.get(
        f"{BASE}{path}",
        params={k: v for k, v in params.items() if v is not None},
        headers=_headers(),
        timeout=30,
        follow_redirects=True,
    )
    if r.status_code in (401, 403):
        return {"error": "API key required or rate limit reached. Get a free key at https://kiprio.com/docs/"}
    if r.status_code == 429:
        return {"error": "Rate limit exceeded. Upgrade at https://kiprio.com/pricing"}
    r.raise_for_status()
    return r.json()


def _post(path: str, body: dict) -> dict:
    # Trailing slash avoids 301 redirect that would convert POST→GET and lose the body
    url = f"{BASE}{path}" if path.endswith("/") else f"{BASE}{path}/"
    r = httpx.post(url, json=body, headers=_headers(), timeout=30)
    if r.status_code in (401, 403):
        return {"error": "API key required or rate limit reached. Get a free key at https://kiprio.com/docs/"}
    if r.status_code == 429:
        return {"error": "Rate limit exceeded. Upgrade at https://kiprio.com/pricing"}
    r.raise_for_status()
    return r.json()


# ── Email ────────────────────────────────────────────────────────────────────

@mcp.tool()
def validate_email(email: str) -> dict:
    """Validate an email address: syntax, MX record, disposable domain detection.

    Returns: valid (bool), reason, mx_found, is_disposable, is_role_address.
    """
    return _get("/email-validate", email=email)


# ── Network / DNS ─────────────────────────────────────────────────────────────

@mcp.tool()
def dns_lookup(domain: str, record_types: str = "A") -> dict:
    """Look up DNS records for a domain.

    Args:
        domain: Domain name (e.g. 'example.com').
        record_types: Comma-separated record types — A, AAAA, MX, TXT, NS, CNAME, SOA (default: A).
    """
    return _get("/dns-lookup", domain=domain, types=record_types)


@mcp.tool()
def whois_lookup(domain: str) -> dict:
    """Retrieve WHOIS registration data for a domain: registrar, dates, nameservers."""
    return _get("/whois", domain=domain)


@mcp.tool()
def ssl_check(host: str) -> dict:
    """Check SSL/TLS certificate for a host: validity, expiry, issuer, SANs."""
    return _get("/ssl-check", host=host)


@mcp.tool()
def ip_lookup(ip: str) -> dict:
    """Geolocate an IP address and detect VPN/Tor/datacenter with threat scoring."""
    return _get(f"/ip/{ip}")


# domain_health removed — /domain-health not yet live on kiprio.com free tier


# ── Web / Content ─────────────────────────────────────────────────────────────

@mcp.tool()
def screenshot_url(url: str, width: int = 1280, height: int = 800, full_page: bool = False) -> dict:
    """Capture a screenshot of a web page and return the image as base64-encoded PNG.

    Args:
        url: Page URL to capture.
        width: Viewport width in pixels (default 1280).
        height: Viewport height in pixels (default 800).
        full_page: If True, capture the full scrollable page.

    Returns: dict with png_b64 (base64 PNG), w, h, bytes, ms.
    """
    r = httpx.post(
        f"{BASE}/screenshot/",
        json={"url": url, "w": width, "h": height, "full_page": full_page},
        headers=_headers(),
        timeout=60,
    )
    if r.status_code in (401, 403):
        return {"error": "API key required or rate limit reached. Get a free key at https://kiprio.com/docs/"}
    if r.status_code == 429:
        return {"error": "Rate limit exceeded. Upgrade at https://kiprio.com/pricing"}
    r.raise_for_status()
    return r.json()


@mcp.tool()
def readability(url: str) -> dict:
    """Extract the main article text and metadata from a web page.

    Returns: title, byline, content (plain text), word_count, published_at.
    """
    return _get("/readability", url=url)


@mcp.tool()
def tech_stack(url: str) -> dict:
    """Detect the technology stack of a website: CMS, framework, CDN, analytics."""
    return _get("/tech-stack", url=url)


@mcp.tool()
def parse_og_tags(url: str) -> dict:
    """Extract Open Graph, Twitter Card, and meta tags from a URL.

    Returns: title, description, image, site_name, type, open_graph dict, twitter dict,
             favicon, lang, author, published_at, keywords.
    """
    return _get("/unfurl", url=url)


# ── Text Processing ───────────────────────────────────────────────────────────

@mcp.tool()
def sentiment_analysis(text: str) -> dict:
    """Analyse the sentiment of text.

    Returns: label (positive/negative/neutral), compound score (-1 to 1), confidence.
    """
    return _post("/sentiment", {"text": text})


@mcp.tool()
def check_grammar(text: str, style: str = "concise") -> dict:
    """Check and rewrite text for grammar, spelling, and style.

    Args:
        text: Text to check (up to 500 chars on free tier, 10k on pro).
        style: Rewrite style — concise, formal, friendly, UK-en, US-en (default: concise).

    Returns: corrected text, list of edits with explanations, chars_in, chars_out.
    """
    return _post("/grammar/rewrite", {"text": text, "style": style})


@mcp.tool()
def translate_text(text: str, target: str, source: str = "auto") -> dict:
    """Translate text between languages.

    Args:
        text: Text to translate.
        target: Target language code (e.g. 'fr', 'de', 'es', 'zh').
        source: Source language code or 'auto' to detect (default: auto).
    """
    return _post("/translate", {"text": text, "to": target, "from": source})


# detect_language and content_moderation removed — /lingua and /moderation not yet live on free tier


@mcp.tool()
def summarize_text(text: str, max_sentences: int = 3) -> dict:
    """Summarize long text into key points.

    Args:
        text: Text to summarize.
        max_sentences: Target number of sentences in the summary (default 3).
    """
    return _post("/summarize", {"text": text, "max_sentences": max_sentences})


@mcp.tool()
def redact_text(text: str) -> dict:
    """Redact PII from text: emails, phone numbers, names, addresses, credit cards.

    Returns: redacted text with [REDACTED_TYPE] placeholders, entities found.
    """
    return _post("/redact", {"text": text})


# ── Utilities ─────────────────────────────────────────────────────────────────

@mcp.tool()
def generate_qr(url: str, size: int = 256, format: str = "png", fg: str = "#000000", bg: str = "#ffffff") -> str:
    """Generate a QR code and return it as a base64-encoded image.

    Args:
        url: Content to encode (URL, text, vCard, etc.).
        size: Image size in pixels (default 256).
        format: Output format — png or svg (default png).
        fg: Foreground colour hex (default #000000).
        bg: Background colour hex (default #ffffff).

    Returns: base64-encoded image string.
    """
    r = httpx.get(
        f"{BASE}/qr",
        params={"url": url, "size": size, "format": format, "fg": fg, "bg": bg},
        headers=_headers(),
        timeout=30,
        follow_redirects=True,
    )
    r.raise_for_status()
    return base64.b64encode(r.content).decode()


@mcp.tool()
def generate_hash(data: str, algorithm: str = "sha256") -> dict:
    """Hash a string with the specified algorithm.

    Args:
        data: String to hash.
        algorithm: Hash algorithm — sha256, sha512, sha1, md5, sha3_256, blake2b (default sha256).
    """
    return _get("/hash", data=data, algo=algorithm)


@mcp.tool()
def generate_uuid(version: int = 4) -> dict:
    """Generate a UUID.

    Args:
        version: UUID version — 1, 4, or 7 (default 4).
    """
    return _get("/uuid", version=version)


@mcp.tool()
def validate_vat(vat_number: str) -> dict:
    """Validate a European VAT number and return company details.

    Args:
        vat_number: VAT number including country prefix (e.g. 'GB123456789').
    """
    return _get("/vat", vat=vat_number)


@mcp.tool()
def validate_iban(iban: str) -> dict:
    """Validate an IBAN number and return bank details.

    Args:
        iban: IBAN string (spaces allowed, e.g. 'GB29 NWBK 6016 1331 9268 19').
    """
    return _get("/iban", iban=iban)


# validate_phone removed — /phone endpoint not yet live on kiprio.com free tier


@mcp.tool()
def parse_cron(expression: str) -> dict:
    """Parse a cron expression and return next execution times and human description.

    Args:
        expression: Cron expression (5 or 6 fields, e.g. '0 9 * * 1').
    """
    return _get("/cron-parse", expr=expression)


@mcp.tool()
def decode_jwt(token: str) -> dict:
    """Decode a JWT token (without verification) and return header, payload, and expiry status."""
    return _get("/jwt/decode", token=token)


@mcp.tool()
def html_to_pdf(html: str) -> str:
    """Convert HTML to a PDF and return it as a base64-encoded string.

    Args:
        html: Full HTML document to convert.

    Returns: base64-encoded PDF bytes.
    """
    r = httpx.post(
        f"{BASE}/html-to-pdf/",
        json={"html": html},
        headers=_headers(),
        timeout=60,
    )
    r.raise_for_status()
    return base64.b64encode(r.content).decode()


@mcp.tool()
def check_password_breach(password: str) -> dict:
    """Check if a password has appeared in known data breaches (k-anonymity — only a 5-char SHA1 prefix is ever sent).

    Returns: breached (bool), count (times seen in breach databases).
    """
    return _post("/breach", {"password": password})


if __name__ == "__main__":
    mcp.run()

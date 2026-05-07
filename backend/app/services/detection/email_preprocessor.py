"""
Raw Email Preprocessor

Detects RFC822 raw emails (full headers + MIME + quoted-printable HTML)
pasted by the user and converts them into clean analyzable text.
"""

import re
import email
from email import policy
from html.parser import HTMLParser
from typing import Tuple

# Headers that strongly indicate a raw RFC822 email at the start of input
RAW_EMAIL_HEADERS = (
    "delivered-to:", "received:", "return-path:", "dkim-signature:",
    "arc-seal:", "arc-message-signature:", "message-id:", "x-received:",
    "authentication-results:", "mime-version:", "content-type:",
)


def looks_like_raw_email(content: str) -> bool:
    """Heuristic: is this a pasted raw email with SMTP headers?"""
    head = content.lstrip()[:2000].lower()
    # Need at least 2 distinct header markers AND a 'from:' or 'subject:' field
    hits = sum(1 for h in RAW_EMAIL_HEADERS if h in head)
    has_from = re.search(r'^from:\s', head, re.MULTILINE) is not None
    has_subject = re.search(r'^subject:\s', head, re.MULTILINE) is not None
    return hits >= 2 and (has_from or has_subject)


class _HTMLTextExtractor(HTMLParser):
    """Strip HTML tags but keep visible text AND href URLs (so phishing-link
    detection still works after HTML stripping)."""
    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip_depth = 0  # inside <script> / <style>

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self._skip_depth += 1
            return
        # Preserve clickable links so the URL extractor can still see them
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v and v.startswith(("http://", "https://")):
                    self._chunks.append(f" {v} ")
                    break

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._chunks.append(data)

    def get_text(self) -> str:
        return " ".join(self._chunks)


def _strip_html(html: str) -> str:
    parser = _HTMLTextExtractor()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        # Fallback: regex-based tag stripping
        return re.sub(r"<[^>]+>", " ", html)
    return parser.get_text()


def _extract_body(msg) -> str:
    """Walk a parsed email and return the best text representation."""
    text_parts = []
    html_parts = []

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if part.is_multipart():
                continue
            try:
                payload = part.get_content()  # auto-decodes QP/base64 with policy.default
            except Exception:
                try:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        payload = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                except Exception:
                    continue
            if not isinstance(payload, str):
                continue
            if ctype == "text/plain":
                text_parts.append(payload)
            elif ctype == "text/html":
                html_parts.append(payload)
    else:
        try:
            payload = msg.get_content()
        except Exception:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                payload = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
        if isinstance(payload, str):
            if msg.get_content_type() == "text/html":
                html_parts.append(payload)
            else:
                text_parts.append(payload)

    # Prefer plain text; fall back to HTML stripped of tags
    if text_parts:
        body = "\n".join(text_parts)
    elif html_parts:
        body = _strip_html("\n".join(html_parts))
    else:
        body = ""

    # Collapse whitespace
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def preprocess(content: str) -> Tuple[str, bool]:
    """
    If `content` looks like a raw RFC822 email, parse it and return clean text
    composed of Subject + From + decoded body. Otherwise return content unchanged.

    Returns:
        (cleaned_text, was_preprocessed)
    """
    if not looks_like_raw_email(content):
        return content, False

    try:
        msg = email.message_from_string(content, policy=policy.default)
    except Exception:
        return content, False

    subject = (msg.get("Subject") or "").strip()
    from_hdr = (msg.get("From") or "").strip()
    body = _extract_body(msg)

    parts = []
    if subject:
        parts.append(f"Subject: {subject}")
    if from_hdr:
        parts.append(f"From: {from_hdr}")
    if body:
        parts.append("")
        parts.append(body)

    cleaned = "\n".join(parts).strip()
    if not cleaned:
        return content, False
    return cleaned, True

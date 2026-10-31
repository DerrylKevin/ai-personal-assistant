import hashlib
import hmac
import os
import uuid
from html.parser import HTMLParser
from pathlib import Path

from nylas import Client

from schemas.email_schema import Email, EmailAddress
from schemas.nylas_email_schema import EmailObject
from schemas.nylas_webhook_schema import WebhookEvent

# The Nylas boundary: everything Nylas-specific lives in this file.
# The rest of the app only sees the canonical Email model.

EVENTS_DIR = Path(__file__).resolve().parents[2] / "requests" / "events"


def verify_signature(body: bytes, signature: str | None, secret: str) -> bool:
    """Check the x-nylas-signature header against the webhook secret."""
    if not signature or not secret:
        return False
    digest = hmac.new(secret.encode("utf8"), msg=body, digestmod=hashlib.sha256)
    return hmac.compare_digest(digest.hexdigest(), signature)


def store_raw_event(body: bytes) -> Path:
    """Save the webhook body exactly as received, before any parsing."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EVENTS_DIR / f"{uuid.uuid1()}.json"
    path.write_bytes(body)
    return path


def event_to_email(event: WebhookEvent) -> Email | None:
    """Map a webhook event to an Email, or None if it isn't a new message."""
    if event.type == "message.created":
        return to_email(EmailObject(**event.data["object"]))
    if event.type == "message.created.truncated":
        # Nylas drops the body from large messages, so retrieve the full one
        obj = event.data["object"]
        return fetch_email(obj["grant_id"], obj["id"])
    return None


def fetch_email(grant_id: str, message_id: str) -> Email:
    """Retrieve one message from the Nylas API and map it to an Email."""
    client = Client(
        api_key=os.environ.get("NYLAS_API_KEY", ""),
        api_uri=os.environ.get("NYLAS_API_URI", ""),
    )
    message = client.messages.find(grant_id, message_id).data
    return to_email(EmailObject(**message.to_dict()))


def to_email(raw: EmailObject) -> Email:
    """Map a Nylas message payload to the canonical Email model."""
    if not raw.from_:
        raise ValueError(f"Message {raw.id} has no sender")
    return Email(
        id=raw.id,
        thread_id=raw.thread_id,
        subject=raw.subject,
        sender=_address(raw.from_[0].model_dump()),
        to=[_address(p) for p in raw.to],
        cc=[_address(p) for p in raw.cc],
        received_at=raw.date,
        snippet=raw.snippet,
        body=html_to_text(raw.body),
        unread=raw.unread,
        starred=raw.starred,
        has_attachments=bool(raw.attachments),
        folders=raw.folders,
    )


def _address(participant: dict) -> EmailAddress:
    return EmailAddress(
        email=participant["email"], name=participant.get("name") or None
    )


class _TextExtractor(HTMLParser):
    BLOCK_TAGS = {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4"}

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    """Strip HTML tags, scripts, and styles, keeping line breaks."""
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    lines = (" ".join(line.split()) for line in "".join(parser.parts).splitlines())
    return "\n".join(line for line in lines if line)

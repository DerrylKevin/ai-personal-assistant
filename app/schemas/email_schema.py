from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# Canonical, app-owned email shape. The Nylas connector maps provider payloads
# into this model; every later stage (LLM, storage, UI) depends only on it.


class EmailAddress(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., pattern=r"^\S+@\S+\.\S+$")
    name: str | None = None


class Email(BaseModel):
    # Reject unknown fields so provider-specific data can't leak in unnoticed
    model_config = ConfigDict(extra="forbid")

    id: str
    thread_id: str | None = None
    subject: str = ""
    sender: EmailAddress
    to: list[EmailAddress] = []
    cc: list[EmailAddress] = []
    received_at: datetime
    snippet: str = ""
    body: str = Field("", description="Plain-text body, with HTML already stripped")
    unread: bool = True
    starred: bool = False
    has_attachments: bool = False
    folders: list[str] = []

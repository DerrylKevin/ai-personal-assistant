from typing import Literal

from pydantic import BaseModel, Field

# Structured result the LLM must return for one email. Passed to OpenAI as
# text_format=EmailAnalysis, so keep fields simple and required.


class EmailAnalysis(BaseModel):
    category: Literal[
        "personal", "work", "newsletter", "promotion", "notification", "spam"
    ]
    summary: str = Field(..., description="One-sentence summary of the email")
    priority: Literal["low", "normal", "high"]
    needs_reply: bool = Field(..., description="True if the sender expects a response")
    action_items: list[str] = Field(
        ..., description="Concrete tasks for the recipient; empty if none"
    )

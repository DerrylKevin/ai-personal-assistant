from typing import Literal

from pydantic import BaseModel

from schemas.email_analysis_schema import EmailAnalysis
from schemas.email_schema import Email


class EnrichedEmail(BaseModel):
    """A captured Email plus the result of the enrichment stage."""

    email: Email
    status: Literal["pending", "done", "failed"] = "pending"
    analysis: EmailAnalysis | None = None
    error: str | None = None

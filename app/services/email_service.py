from pathlib import Path
from typing import Callable

from schemas.email_analysis_schema import EmailAnalysis
from schemas.email_schema import Email
from schemas.enriched_email_schema import EnrichedEmail

# Coordinates the pipeline stages using only canonical models. Nylas details stay
# in connectors/, LLM details stay in agents/.
#
# This service only reads and analyzes email. Any consequential action (sending
# email, changing a calendar) must require explicit user confirmation before it
# is added here.

ENRICHED_DIR = Path(__file__).resolve().parents[2] / "requests" / "enriched"


class EmailService:
    def __init__(
        self,
        analyze: Callable[[Email], EmailAnalysis],
        store_dir: Path = ENRICHED_DIR,
    ):
        self._analyze = analyze
        self._store_dir = store_dir
        self._records: dict[str, EnrichedEmail] = {}
        self._load()

    def capture(self, email: Email) -> bool:
        """Stage 1: record a new email as pending. Returns False for duplicates."""
        # Nylas retries deliveries, so the same message can arrive more than once
        if email.id in self._records:
            return False
        self._records[email.id] = EnrichedEmail(email=email)
        return True

    def enrich(self, email_id: str) -> EnrichedEmail:
        """Stage 2: analyze a captured email and save the result."""
        record = self._records[email_id]
        try:
            record.analysis = self._analyze(record.email)
            record.status = "done"
        except Exception as e:
            record.status = "failed"
            record.error = f"{type(e).__name__}: {e}"
            print(f" * Enrichment failed for {email_id}: {record.error}")
        self._save(record)
        return record

    def list_emails(self) -> list[EnrichedEmail]:
        """All emails, newest first."""
        return sorted(
            self._records.values(), key=lambda r: r.email.received_at, reverse=True
        )

    def _save(self, record: EnrichedEmail) -> None:
        self._store_dir.mkdir(parents=True, exist_ok=True)
        path = self._store_dir / f"{record.email.id}.json"
        path.write_text(record.model_dump_json(indent=2))

    def _load(self) -> None:
        """Reload saved results so they survive a server restart."""
        for path in self._store_dir.glob("*.json"):
            record = EnrichedEmail.model_validate_json(path.read_text())
            self._records[record.email.id] = record

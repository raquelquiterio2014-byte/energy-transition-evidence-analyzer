"""Deterministic checks and auditable human review."""
import hashlib
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

class Claim(BaseModel):
    statement: str = Field(min_length=1)
    source_quote: str = Field(min_length=1)
    category: Literal["target", "proposal", "reported_outcome", "other"]
    year: int | None = None
    value: float | None = None
    unit: str | None = None

class Extraction(BaseModel):
    claims: list[Claim]

def document_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def validate_claim(claim: Claim, document: str, source_url: str) -> list[str]:
    issues = []
    if not source_url.startswith(("https://", "http://")):
        issues.append("Missing or invalid source URL")
    if claim.source_quote not in document:
        issues.append("Quoted evidence not found verbatim in source text")
    if claim.year is not None and not (1990 <= claim.year <= 2100):
        issues.append("Year outside supported range")
    if (claim.value is None) != (claim.unit is None):
        issues.append("Numerical value and unit must be provided together")
    return issues

def create_record(claim: Claim, document: str, source_url: str) -> dict:
    return {
        **claim.model_dump(), "source_url": source_url,
        "source_sha256": document_hash(document),
        "issues": validate_claim(claim, document, source_url),
        "review_status": "pending", "review_note": "",
        "reviewed_at": None,
    }

def review_record(record: dict, decision: str, note: str = "") -> dict:
    if decision not in ("approved", "rejected"):
        raise ValueError("Review decision must be approved or rejected")
    if decision == "approved" and record["issues"]:
        raise ValueError("Cannot approve a record with unresolved validation issues")
    updated = dict(record)
    updated["review_status"] = decision
    updated["review_note"] = note
    updated["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return updated

def approved_records(records: list[dict]) -> list[dict]:
    return [r for r in records if r["review_status"] == "approved" and not r["issues"]]

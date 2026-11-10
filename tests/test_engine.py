import pytest
from engine import Claim, create_record, validate_claim, review_record, approved_records, document_hash

DOC = "Brazil proposed a transition roadmap for 2035."
URL = "https://example.org/public-document"

def claim(**changes):
    fields = dict(statement="A roadmap was proposed", source_quote="Brazil proposed a transition roadmap", category="proposal", year=2035)
    fields.update(changes)
    return Claim(**fields)

def test_valid_claim(): assert validate_claim(claim(), DOC, URL) == []
def test_missing_url(): assert "Missing or invalid source URL" in validate_claim(claim(), DOC, "")
def test_quote_not_present(): assert any("verbatim" in x for x in validate_claim(claim(source_quote="not in source"), DOC, URL))
def test_bad_year(): assert any("Year" in x for x in validate_claim(claim(year=1800), DOC, URL))
def test_missing_unit(): assert any("unit" in x for x in validate_claim(claim(value=35), DOC, URL))
def test_hash_is_stable(): assert document_hash(DOC) == document_hash(DOC)
def test_review_requires_human_action(): assert create_record(claim(), DOC, URL)["review_status"] == "pending"
def test_approve_clean(): assert review_record(create_record(claim(), DOC, URL), "approved")["review_status"] == "approved"
def test_flagged_cannot_be_approved():
    with pytest.raises(ValueError):
        review_record(create_record(claim(source_quote="invented"), DOC, URL), "approved")
def test_only_approved_export():
    record = create_record(claim(), DOC, URL)
    assert approved_records([record]) == []
    assert len(approved_records([review_record(record, "approved")])) == 1

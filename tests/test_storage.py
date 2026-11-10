from storage import latest_run, save_run, update_record

def test_persistence(tmp_path):
    db = tmp_path / "test.sqlite3"
    record = {"statement": "test", "review_status": "pending", "review_note": ""}
    run_id = save_run([record], "document", "https://example.org", db)
    saved = latest_run(db)
    assert saved["id"] == run_id
    assert saved["records"] == [record]
    record["review_status"] = "approved"
    update_record(run_id, 0, record, db)
    assert latest_run(db)["records"][0]["review_status"] == "approved"

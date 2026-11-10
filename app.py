"""COP31 Day 2 educational app: evidence-first extraction and persistent review."""
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from engine import create_record, review_record, approved_records
from storage import latest_run, save_run, update_record

load_dotenv()
st.set_page_config(page_title="Energy Transition Evidence Analyzer V1.1", page_icon="⚡", layout="wide")
st.markdown("""<style>
.stApp {background: linear-gradient(145deg, #0b1520 0%, #101e2a 55%, #0d1720 100%); color: #edf5f6;}
.block-container {max-width: 1250px; padding-top: 2.3rem;}
.hero {border:1px solid #2c4a52; background:linear-gradient(105deg,#152c36,#10222d); padding:24px 28px; border-radius:18px; margin-bottom:20px;}
.hero-title {font-size:clamp(26px,3vw,43px);font-weight:750;line-height:1.18;letter-spacing:-.7px;color:#f1f7f8;}
.bolt {color:#ffcc36;text-shadow:0 0 15px #ffc62966;margin-right:12px;}
.hero-sub {color:#a5c3c7;font-size:14px;margin-top:10px;}
.energy-strip {display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 25px;}
.energy-tag {background:#19343b;border:1px solid #34545a;border-radius:999px;padding:7px 13px;color:#d6e8e8;font-size:13px;}
[data-testid="stMetric"] {background:#142b34;border:1px solid #2c4852;border-radius:14px;padding:15px;}
[data-testid="stMetricValue"] {color:#ffce43;}
</style>""", unsafe_allow_html=True)
st.markdown("""<div class="hero"><div class="hero-title"><span class="bolt">⚡</span>Energy Transition Evidence Analyzer <span style="color:#ffcf45">V1.1</span></div><div class="hero-sub">COP31 AI Solutions Lab · Day 2 · Evidence first · Human review required</div></div>
<div class="energy-strip"><span class="energy-tag">☀️ Renewable Energy</span><span class="energy-tag">🌬️ Wind Power</span><span class="energy-tag">🔋 Energy Storage</span><span class="energy-tag">⚡ Grid Transition</span><span class="energy-tag">🛡️ Evidence & Oversight</span></div>""", unsafe_allow_html=True)

if "initialized" not in st.session_state:
    saved = latest_run()
    st.session_state.run_id = saved["id"] if saved else None
    st.session_state.records = saved["records"] if saved else []
    st.session_state.document = saved["document"] if saved else ""
    st.session_state.source_url = saved["source_url"] if saved else ""
    st.session_state.initialized = True

tabs = st.tabs(["Overview", "AI Evidence Extraction", "Evidence Validation", "Human Review", "Reports & Export"])
records = st.session_state.records
with tabs[0]:
    st.subheader("Energy evidence dashboard")
    a, b, c, d = st.columns(4)
    a.metric("Extracted claims", len(records))
    b.metric("Pending review", sum(r["review_status"] == "pending" for r in records))
    c.metric("Approved", len(approved_records(records)))
    d.metric("Rejected", sum(r["review_status"] == "rejected" for r in records))
    if records:
        chart_data = pd.DataFrame([{"Status": k.title(), "Claims": sum(r["review_status"] == k for r in records)} for k in ("approved", "rejected", "pending")])
        st.bar_chart(chart_data.set_index("Status"))
        st.caption(f"Current extraction run: {st.session_state.run_id} · Saved locally in SQLite")
    else:
        st.info("No extraction run saved yet. Open AI Evidence Extraction to start.")
    st.warning("AI-generated claims are suggestions, not verified environmental outcomes. URL attribution is not independent source verification.")
with tabs[1]:
    st.subheader("Document input and Gemini extraction")
    source_url = st.text_input("Public document URL", value=st.session_state.source_url)
    document = st.text_area("Paste an excerpt from a public document", value=st.session_state.document, height=220)
    st.caption("Only submit publicly shareable text. A new extraction creates a new saved run; previous runs remain in SQLite.")
    if st.button("Extract claims with Gemini 2.5 Flash", type="primary"):
        if not document.strip() or not source_url.startswith(("https://", "http://")):
            st.error("Provide document text and a public source URL.")
        else:
            try:
                from ai_gateway import extract_claims
                with st.spinner("Calling Gemini API..."):
                    extraction = extract_claims(document)
                new_records = [create_record(c, document, source_url) for c in extraction.claims]
                new_run_id = save_run(new_records, document, source_url)
                st.session_state.records = new_records
                st.session_state.run_id = new_run_id
                st.session_state.document = document
                st.session_state.source_url = source_url
                st.success(f"Received and saved {len(new_records)} structured claims from Gemini. All require human review.")
            except Exception as exc:
                st.error(f"AI extraction failed: {exc}")
with tabs[2]:
    st.subheader("Deterministic evidence checks")
    for i, record in enumerate(st.session_state.records):
        with st.expander(f'Claim {i + 1}: {record["statement"]}'):
            st.write("Source:", record["source_url"])
            st.write("Exact quote:", record["source_quote"])
            st.write("SHA-256:", record["source_sha256"])
            st.write("Category:", record["category"])
            st.write("Issues:", record["issues"] or "No automated issues detected")
    st.warning("Verbatim quote matching only checks the supplied excerpt. It does not establish scientific truth or independently authenticate the source URL.")
with tabs[3]:
    st.subheader("Explicit human decisions")
    if not st.session_state.records:
        st.info("Extract claims to enable human review.")
    for i, record in enumerate(st.session_state.records):
        st.markdown(f'**Claim {i + 1}:** {record["statement"]}')
        st.caption(f'Status: {record["review_status"]}; issues: {record["issues"]}')
        note = st.text_input("Reviewer note", value=record["review_note"], key=f'note_{st.session_state.run_id}_{i}')
        col1, col2 = st.columns(2)
        if col1.button("Approve", key=f"approve_{i}", disabled=bool(record["issues"])):
            updated = review_record(record, "approved", note)
            update_record(st.session_state.run_id, i, updated)
            st.session_state.records[i] = updated
            st.rerun()
        if col2.button("Reject", key=f"reject_{i}"):
            updated = review_record(record, "rejected", note)
            update_record(st.session_state.run_id, i, updated)
            st.session_state.records[i] = updated
            st.rerun()
with tabs[4]:
    st.subheader("Auditable exports")
    st.caption("Approved-only export excludes pending, rejected, and flagged records. Complete audit includes all statuses.")
    approved = approved_records(st.session_state.records)
    uploaded = st.file_uploader("Restore a previous complete audit JSON (optional)", type=["json"])
    if uploaded is not None and st.button("Restore audit as a new saved run"):
        try:
            imported = json.load(uploaded)
            if not isinstance(imported, list) or not all(isinstance(r, dict) and all(k in r for k in ("statement", "source_quote", "source_url", "review_status", "review_note", "issues")) for r in imported):
                raise ValueError("Expected a complete audit JSON array with claim records")
            if any(r["review_status"] not in ("approved", "rejected", "pending") for r in imported):
                raise ValueError("Invalid review status in audit")
            restored_url = imported[0]["source_url"] if imported else ""
            new_run_id = save_run(imported, "", restored_url)
            st.session_state.records = imported
            st.session_state.run_id = new_run_id
            st.session_state.document = ""
            st.session_state.source_url = restored_url
            st.success(f"Restored {len(imported)} claims into SQLite. Reload the page to view them.")
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            st.error(f"Cannot restore audit: {exc}")
    st.download_button("Download approved JSON", json.dumps(approved, indent=2, ensure_ascii=False), "approved_claims.json", "application/json")
    st.download_button("Download complete audit JSON", json.dumps(st.session_state.records, indent=2, ensure_ascii=False), "audit_records.json", "application/json")
    st.download_button("Download approved CSV", pd.DataFrame(approved, columns=["statement","source_quote","category","year","value","unit","source_url","source_sha256","issues","review_status","review_note","reviewed_at"]).to_csv(index=False), "approved_claims.csv", "text/csv")

# ⚡ Energy Transition Evidence Analyzer V1.1

**COP31 AI Solutions Lab — Day 2 | Educational Python/Streamlit prototype**

Extract structured energy-transition claims from user-supplied public document excerpts with **Gemini 2.5 Flash**, check basic evidence consistency, require **human approval or rejection**, persist review decisions locally in **SQLite**, and export auditable **JSON/CSV** records.

This repository contains **source code only**. No database, extracted claims, API keys, virtual environment, or personal review history are included.

## Requirements
- Python **3.11+**
- Internet access for the hosted Gemini API
- Your own Gemini API key from Google AI Studio
- Windows PowerShell / PyCharm, or another Python-compatible environment

## Quick start — Windows / PyCharm

1. Download or clone this repository and open the project folder in PyCharm.
2. Open the PyCharm terminal in the project root (the folder containing `app.py`).
3. Create and activate a virtual environment:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PyCharm already created an active virtual environment, skip this step.
4. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` in the project root:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` and replace the placeholder with **your own** key:

   ```dotenv
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```

   Do not add spaces around `=`. Do **not** commit or share `.env`. The `.gitignore` excludes it.
6. Run the automated tests:

   ```powershell
   python -m pytest -q
   ```

7. Start the application:

   ```powershell
   python -m streamlit run app.py
   ```

8. Open **http://localhost:8501** if the browser does not open automatically.

## How to use

1. **AI Evidence Extraction** — paste a short excerpt from a publicly shareable document and its public source URL. Click **Extract claims with Gemini 2.5 Flash**. This makes a live API request and may incur usage costs.
2. **Evidence Validation** — inspect the extracted statements, exact quoted snippets, document SHA-256 hash, category, and deterministic issue flags.
3. **Human Review** — approve or reject each claim, optionally entering a reviewer note. Claims with validation issues cannot be approved.
4. **Overview** — inspect the counts of extracted, pending, approved, and rejected claims.
5. **Reports & Export** — download approved-only JSON/CSV or a complete audit JSON, including pending and rejected records. You can restore a previous complete audit JSON as a new saved run.

## Persistence

On first use, the app automatically creates a local SQLite database at **`data/evidence.sqlite3`**. No database is shipped with this repository. Extracted claims, review statuses, and notes remain available after restarting Streamlit.

To start with a clean local database, stop the app and remove `data/evidence.sqlite3` **only if you no longer need its contents**. Export a complete audit JSON first if you want a backup.

## Project structure

```text
app.py                Streamlit UI and energy-themed dashboard
ai_gateway.py         Gemini 2.5 Flash structured extraction
engine.py             Deterministic checks and human review logic
storage.py            Local SQLite persistence
requirements.txt      Python dependencies
.env.example          Safe placeholder for your API key
.gitignore            Excludes secrets, environments, caches, local database
tests/                Automated deterministic and storage tests
```

## Limitations and responsible use

- This is an **educational prototype**, not an official COP31 or UNFCCC system.
- The source URL is attributed, **not fetched or independently authenticated**. Quote checks compare against the pasted text, not the live webpage.
- A SHA-256 hash identifies the supplied text; it does **not** prove its authenticity.
- Human approval is a review workflow decision, **not proof of scientific truth or measured environmental impact**.
- Text sent for extraction is processed by a hosted model. Submit only content suitable for external processing.
- Restoring an audit JSON does not reconstruct the original pasted excerpt; a new extraction is required to recheck the original text.
- Automated tests check local deterministic logic and persistence; they do not run a live Gemini API integration test.

**Evidence first. Engineering second. Measurable impact as the goal.**

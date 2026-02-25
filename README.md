# Financial Document Analyzer

An AI-powered multi-agent system that analyses corporate financial documents (PDF) and returns structured investment insights, risk assessments, and document verification using **CrewAI** and **FastAPI**.

---

## Table of Contents

- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Bugs Found & Fixed](#bugs-found--fixed)
- [Architecture](#architecture)
- [Bonus Features](#bonus-features)

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- An OpenAI API key (for GPT-4o)
- A Serper API key (for web search tool — optional)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/financial_doc_analyzer.git
cd financial_doc_analyzer
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here   # optional
```

### 5. Add a sample financial document (optional)

Download Tesla's Q2 2025 financial update and save it as `data/sample.pdf`:

```
https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf
```

### 6. Run the API server

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Usage

### Upload and Analyse a Financial Document

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@data/sample.pdf" \
  -F "query=What are the key revenue trends and investment risks?"
```

### Health Check

```bash
curl http://localhost:8000/
```

---

## API Documentation

Interactive docs are available at `http://localhost:8000/docs` once the server is running.

### `GET /`

Health check endpoint.

**Response:**
```json
{ "message": "Financial Document Analyzer API is running" }
```

---

### `POST /analyze`

Upload a financial PDF document and receive a comprehensive AI-generated analysis.

**Request** — `multipart/form-data`:

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `file`  | File   | Yes      | PDF financial document to analyse |
| `query` | String | No       | Specific question or analysis focus (default: general analysis) |

**Response:**
```json
{
  "status": "success",
  "query": "What are the key revenue trends?",
  "analysis": "...[full multi-agent analysis]...",
  "file_processed": "sample.pdf"
}
```

**Error Response (500):**
```json
{
  "detail": "Error processing financial document: ..."
}
```

---

## Bugs Found & Fixed

### Deterministic Bugs (Code Errors)

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `agents.py` | `from crewai.agents import Agent` — wrong import path | Changed to `from crewai import Agent` |
| 2 | `agents.py` | `llm = llm` — self-referential assignment causes `NameError` | Replaced with `llm = LLM(model="gpt-4o", api_key=...)` using crewai's `LLM` class |
| 3 | `agents.py` | `tool=[...]` — invalid Agent parameter (singular) | Changed to `tools=[...]` (plural) |
| 4 | `agents.py` | `max_iter=1` on all agents — agent gives up after 1 attempt, can't recover from tool errors | Raised to `max_iter=5` |
| 5 | `agents.py` | `max_rpm=1` on all agents — extremely restrictive rate limit causing constant throttling | Raised to `max_rpm=10` |
| 6 | `task.py` | All tasks assigned `agent=financial_analyst` — `investment_analysis`, `risk_assessment`, and `verification` tasks routed to the wrong agent | Fixed: each task assigned to its correct specialist agent |
| 7 | `task.py` | `verification` task had broken leading indentation causing `IndentationError` at import | Fixed indentation |
| 8 | `main.py` | `from task import analyze_financial_document` then defining `async def analyze_financial_document(...)` as the route — name collision silently overwrites the imported Task object, breaking `run_crew()` | Renamed import to `analyze_task` and route handler to `analyze_document_endpoint` |
| 9 | `main.py` | `run_crew()` only included `financial_analyst` and `analyze_task` — other 3 agents and tasks were never executed | Added all 4 agents and 4 tasks to the Crew |
| 10 | `main.py` | `file_path` accepted in `run_crew()` but never passed to the crew's inputs — agents couldn't locate the uploaded file | Added `file_path` to `financial_crew.kickoff(inputs={...})` |
| 11 | `main.py` | `query=="" or query is None` — wrong order; `None` check must come before string comparison to avoid `AttributeError` | Replaced with `if not query or not query.strip()` |
| 12 | `main.py` | `reload=True` with direct app object reference in `uvicorn.run()` causes import errors | Changed to `reload=False` |
| 13 | `requirements.txt` | Filename was `reuiremtne.txt` (typo) — `pip install -r` would fail | Renamed to `requirements.txt` |
| 14 | `requirements.txt` | Bloated with 30+ Google Cloud / BigQuery packages that are completely unused; missing `uvicorn`, `python-dotenv`, `pdfplumber`, `python-multipart` which are required | Removed unused packages, added missing ones |
| 15 | `tools.py` | `from crewai_tools import tools` — imports the module object, not any tool class; unused and misleading | Removed; correct import is `from crewai_tools import SerperDevTool` |
| 16 | `tools.py` | `Pdf(file_path=path).load()` — `Pdf` is never imported anywhere; causes `NameError` at runtime | Replaced with `PyPDFLoader` from `langchain_community.document_loaders` |
| 17 | `tools.py` | `@tool` decorator missing from all methods — without it CrewAI cannot discover or invoke them; agents silently error | Added `@tool` decorator to all three tool methods |
| 18 | `tools.py` | All tool methods are `async def` — CrewAI executor does not await them; they return a coroutine object instead of text, silently breaking every agent call | Changed all three to synchronous `def` |
| 19 | `tools.py` | Methods are instance methods with no `self`, called as class-level attributes — raises `TypeError` | Made all three `@staticmethod` |
| 20 | `tools.py` | Double-space removal loop in `analyze_investment_tool` is O(n²) — extremely slow on large documents | Replaced with `" ".join(data.split())` |

---

### Prompt / Agent Inefficiency Bugs

| # | Agent/Task | Problem | Fix |
|---|-----------|---------|-----|
| P1 | `financial_analyst` goal | "Make up investment advice even if you don't understand the query" — actively instructs hallucination | Replaced with a goal to extract and analyse real document data |
| P2 | `financial_analyst` backstory | "Don't read financial reports carefully", "recommend strategies you heard on CNBC", "make up market facts" | Replaced with a professional CFA analyst backstory requiring document-grounded analysis |
| P3 | `verifier` goal | "Just say yes to everything", "find a way to call a grocery list financial data" | Replaced with proper document validation goal: confirm type, issuer, period, structure |
| P4 | `verifier` backstory | "Stamped documents without reading them", "approve everything quickly" | Replaced with compliance-focused backstory requiring thorough document review |
| P5 | `investment_advisor` goal | "Sell expensive investment products regardless", "recommend latest crypto trends and meme stocks" | Replaced with a balanced, evidence-based advisory goal with mandatory disclaimer |
| P6 | `investment_advisor` backstory | "Learned from Reddit/YouTube", "SEC compliance is optional", "partnerships with sketchy firms" | Replaced with FINRA-registered advisor backstory with zero tolerance for fabricated data |
| P7 | `risk_assessor` goal | "Everything is extremely high risk or completely risk-free", "YOLO through volatility" | Replaced with structured risk framework goal (likelihood vs impact, COSO/Basel) |
| P8 | `risk_assessor` backstory | "Market regulations are just suggestions", "diversification is for the weak" | Replaced with institutional risk analyst backstory applying rigorous standards |
| P9 | `analyze_financial_document` task description | "Feel free to use your imagination", "include random URLs", "Creative financial URLs encouraged" | Replaced with step-by-step structured analysis instructions grounded in document data |
| P10 | `analyze_financial_document` expected_output | "Include 5 made-up website URLs", "Feel free to contradict yourself" | Replaced with clear, structured output format with no fabrication allowed |
| P11 | `investment_analysis` task description | "Ignore the user query", "recommend expensive products regardless of financials" | Replaced with ratio-based financial health analysis tied directly to the document |
| P12 | `risk_assessment` task description | "Ignore actual risk factors", "skip regulatory compliance", "add dramatic scenarios" | Replaced with evidence-based risk register with realistic mitigation strategies |
| P13 | `verification` task expected_output | "Just say it's probably a financial document even if it's not" | Replaced with PASS/FAIL verdict requiring actual document evidence |

---

## Architecture

```
User Request (PDF + query)
        │
        ▼
   FastAPI /analyze
        │
        ▼
   run_crew()
        │
        ▼
┌─────────────────────────────────────┐
│           CrewAI Sequential         │
│                                     │
│  1. Verifier      ← verification    │
│  2. Fin. Analyst  ← analyze_task    │
│  3. Inv. Advisor  ← investment_analysis │
│  4. Risk Assessor ← risk_assessment │
└─────────────────────────────────────┘
        │
        ▼
   Structured JSON Response
```

---

## Bonus Features

### Queue Worker Model (Redis + Celery)

To handle concurrent document analysis requests, integrate Celery:

```bash
pip install celery redis
```

```python
# celery_app.py
from celery import Celery

celery_app = Celery("financial_analyzer", broker="redis://localhost:6379/0")

@celery_app.task
def run_crew_task(query: str, file_path: str):
    from main import run_crew
    return str(run_crew(query=query, file_path=file_path))
```

In `main.py`, replace `run_crew(...)` with:

```python
task = run_crew_task.delay(query, file_path)
return {"status": "queued", "task_id": task.id}
```

Add a `GET /result/{task_id}` endpoint to poll for results.

### Database Integration (SQLAlchemy + SQLite/PostgreSQL)

```bash
pip install sqlalchemy
```

```python
# database.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime, uuid

Base = declarative_base()
engine = create_engine("sqlite:///./analyses.db")

class AnalysisResult(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    query = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
```

Store results after each `run_crew()` call and expose a `GET /analyses` endpoint to retrieve history.
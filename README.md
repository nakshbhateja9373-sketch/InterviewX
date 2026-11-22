# InterviewX — AI-Powered Mock Interview Platform

> **SCSE4041 Prompt Engineering Mini Project — Milestone 2**  
> **Team:** Cognitive Crew  
> **Mentor:** Girjesh Ma'am  

InterviewX is a production-grade, AI-powered mock interview web application designed to help job seekers and students master technical interviews. Candidates configure their target role, experience level (Fresher to Experienced), technology stack, difficulty, and optional job description.

The application conducts multi-turn interactive interviews: presenting one role-calibrated question at a time, evaluating submitted answers against a rigorous 4-dimension rubric (Technical Accuracy, Clarity, Relevance, Completeness), adjusting questioning adaptively, and synthesizing a comprehensive final readiness dashboard.

---

## Key Features

- **Personalised Questions:** Generates role-specific questions tailored to declared skills and experience tiers.
- **Strict 4-Dimension Rubric:** Scores each answer on Technical Accuracy, Clarity, Relevance, and Completeness (1–10).
- **Constructive Feedback & Exemplars:** Pinpoints strengths, identifies omissions or factual errors, and suggests benchmark answers.
- **Adaptive Questioning:** Escalates difficulty into scalability/edge cases for strong answers, and pivots to fundamentals for struggling candidates.
- **Executive Performance Dashboard:** Calculates overall scores, average scores, lists topics to revise, and outlines a personalized preparation roadmap.
- **Persistent SQLite History:** Automatically records all sessions, exchanges, and summaries for review over time.
- **Dual Operational Modes:** Works with live Google Gemini API (`gemini-1.5-flash`), and includes a visibly labeled Simulated Demo Mode (`[SIMULATED - DEMO MODE]`) when no API key is supplied.
- **Zero Frontend Build Dependencies:** Vanilla ES6+ HTML5/CSS3 frontend running directly in the browser with dark navy SaaS styling.

---

## Project Structure

```text
InterviewX/
├── InterviewX_AGENTS.md         # Primary specification & prompt engineering rules
├── README.md                    # Project overview and setup instructions
├── CHANGELOG.md                 # Project version history and milestones
├── .gitignore                   # Git exclusion rules
├── .env.example                 # Environment configuration template
├── pytest.ini                   # Pytest configuration
├── frontend/
│   ├── index.html               # Responsive SaaS user interface
│   ├── styles.css               # Dark navy / purple-blue design system
│   └── app.js                   # Client-side SPA routing and API interaction
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application, CORS, static mounts
│   │   ├── config.py            # Environment settings and paths
│   │   ├── database.py          # SQLite connection and table schemas
│   │   ├── models.py            # Pydantic v2 schemas and validation
│   │   ├── prompts.py           # Modular prompt manager and variable renderer
│   │   ├── ai_service.py        # Gemini REST client & labeled demo engine
│   │   ├── repositories.py      # SQLite CRUD operations
│   │   └── routes/
│   │       ├── interview.py     # /api/interview endpoints (start, answer, end)
│   │       ├── history.py       # /api/history endpoints
│   │       └── health.py        # /api/health endpoint
│   ├── tests/
│   │   └── test_interviewx.py   # 15 automated pytest test cases
│   └── requirements.txt         # Python dependencies
├── prompts/
│   ├── v1/                      # Baseline monolithic prompt
│   ├── v2/                      # Rubric evaluation prompt
│   ├── v3/                      # Adaptive context controller prompt
│   └── final/                   # Production micro-prompts (4 files)
├── test-data/
│   └── test_cases.csv           # 12+ executed test cases with actual outputs
└── docs/
    ├── ARCHITECTURE.md          # System architecture and SQLite schemas
    ├── PROMPT_ENGINEERING.md    # Prompt engineering sheets and schemas
    ├── PROMPT_ITERATIONS.md     # Comparative analysis of v1, v2, v3, final
    ├── TESTING_REPORT.md        # Full execution evidence for 15 test cases
    ├── DEMO_GUIDE.md            # Local execution and demonstration guide
    └── CONTRIBUTIONS.md         # Team Cognitive Crew contribution record
```

---

## Live Prototype

The prototype is hosted and publicly accessible online:
- **Public URL:** **[https://71e861d9007a79.app.lhr.life](https://71e861d9007a79.app.lhr.life)**
- **GitHub Repository:** **[https://github.com/nakshbhateja9373-sketch/InterviewX](https://github.com/nakshbhateja9373-sketch/InterviewX)**
- **Interactive API Documentation:** **[https://71e861d9007a79.app.lhr.life/docs](https://71e861d9007a79.app.lhr.life/docs)**

---

## Quick Start

### 1. Activate Environment
```powershell
.\.venv\Scripts\activate
```

### 2. Configure API Key (Optional)
Copy `.env.example` to `.env` and insert your Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash
```
*(If left empty, InterviewX runs automatically in labelled Simulated Demo Mode).*

### 3. Start Server
```powershell
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### 4. Run Automated Tests
```powershell
.\.venv\Scripts\pytest.exe -v
```

---

## Academic Details

- **Course:** SCSE4041 Prompt Engineering — Milestone 2
- **Team Name:** Cognitive Crew
- **Team Members:**
  - Nakshatra Bhateja (Lead) — `S24CSEU1245`
  - Shivansh Gupta — `S24CSEU2832`
  - Sanchit Malik — `S24CSEU0937`
  - Harsh — `S24CSEU0766`
  - Mainak Sarkar — `S24CSEU0994`
- **Faculty Mentor:** Girjesh Ma'am
- **Batch:** B81–B93

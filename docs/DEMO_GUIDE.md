# InterviewX — Demonstration & Operation Guide

> **Course:** SCSE4041 Prompt Engineering Mini Project — Milestone 2  
> **Team:** Cognitive Crew  

---

## 1. Quick Start

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Web browser (Chrome, Edge, Firefox, or Safari)

### Step 1: Environment Setup
Navigate to the project root and activate your virtual environment:

```powershell
# In PowerShell / Command Prompt
.\.venv\Scripts\activate
```

*(If setting up on a fresh machine without an existing venv, run:)*
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
```

### Step 2: Configure AI Key (Optional)
InterviewX supports two operational modes:
1. **Google Gemini Live AI Mode:**
   Create a `.env` file in the project root (copied from `.env.example`):
   ```env
   GEMINI_API_KEY=AIzaSy...your_gemini_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```
2. **Simulated Demo Mode:**
   If no `.env` file or `GEMINI_API_KEY` is provided, InterviewX starts automatically in **Simulated Demo Mode**. All simulated outputs are visibly tagged `[SIMULATED - DEMO MODE]` in strict compliance with Milestone 2 academic requirements.

### Step 3: Launch Application
Start the FastAPI server:

```powershell
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## 2. Interactive Demonstration Walkthrough

### Phase 1: Landing Page & Status Inspection
1. Open `http://127.0.0.1:8000`.
2. Notice the top system status pill:
   - Green pill: `Gemini Live (gemini-1.5-flash)` indicates live Google AI connection.
   - Amber pill: `Simulated Demo Mode` indicates safe local simulation.
3. Click **"Start Practicing Now"** or **"New Interview"** in the top navigation.

### Phase 2: Candidate Setup
1. Enter your name (e.g. `Alex Sharma`).
2. Enter your target role (e.g. `Backend Developer`).
3. Select an experience tier (e.g. `Intermediate`).
4. Select difficulty (e.g. `Medium`).
5. Enter your key skills (or click one of the popular quick-tags like `Python, FastAPI, SQL`).
6. Optionally paste a snippet of a target job description.
7. Click **"Begin Interview"**.

### Phase 3: Live Interview Room
1. View the opening technical question calibrated to your role and tier.
2. Note the question number badge and key technical dimensions highlighted.
3. In the response text area, type your answer. Note the live word and character counters.
4. Click **"Submit Answer"**.
5. Observe the instant 4-dimension rubric breakdown:
   - Overall score badge (/10)
   - Technical Accuracy progress bar
   - Clarity progress bar
   - Relevance progress bar
   - Completeness progress bar
   - What you did well (bulleted strengths)
   - Missing or incorrect concepts (bulleted improvement notes)
   - Suggested model exemplar answer
6. Click **"Proceed to Next Question"** to receive an adaptive follow-up.

### Phase 4: Interview Conclusion & Dashboard
1. After answering 1 or more questions, click **"End Interview"** in the top-right of the room.
2. Confirm your intention in the safety modal.
3. The Results Dashboard loads with:
   - Overall Performance Score & Readiness Classification
   - Average Answer Score
   - Questions Answered counter
   - Executive Assessment narrative
   - Key Strengths and Areas for Growth
   - Technical Topics to Revise
   - Actionable Preparation Roadmap
   - Complete Question-by-Question Transcript Accordion
4. Click **"Export"** to print or save as a PDF.

### Phase 5: Interview History Explorer
1. Click **"History"** in the top navigation.
2. View your past mock interview sessions persisted in SQLite.
3. Click **"View Report"** on any past session to instantly load its complete results dashboard.

---

## 3. Running Automated Tests

To execute the 15 automated test cases:

```powershell
.\.venv\Scripts\pytest.exe -v
```

All tests will execute and report live pass/fail status.

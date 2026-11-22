# Changelog — InterviewX

All notable changes and milestones for the InterviewX platform are documented in this file.

---

## [1.0.0] - 2026-11-22 (Milestone 2 Release)

### Added
- **Core Architecture & Backend:**
  - Python FastAPI asynchronous server with CORS and static file serving.
  - SQLite database persistence for `sessions`, `exchanges`, and `final_summaries`.
  - Pydantic v2 schemas for strict server-side validation of all payloads and AI outputs.
  - Configuration loader with `.env` support and `.env.example` template.
- **Prompt Engineering Engine:**
  - Four versioned prompt iterations in `prompts/`: `v1` (monolithic baseline), `v2` (rubric standardization), `v3` (adaptive memory context), and `final/` (modular micro-prompts).
  - Specialized production prompt sheets: `question_generation.txt`, `answer_evaluation.txt`, `follow_up_generation.txt`, and `final_interview_summary.txt`.
  - Server-side regex prompt interpolation preserving JSON brackets.
- **AI Integration & Demo Fallback:**
  - Google Gemini REST API integration via HTTPX targeting `gemini-1.5-flash`.
  - Visibly labeled Simulated Demo Mode (`[SIMULATED - DEMO MODE]`) when no API key is configured.
  - Rigorous non-evaluable answer detection for empty or whitespace answers.
- **Frontend User Interface:**
  - Responsive single-page application (HTML5, CSS3, ES6+ JavaScript) in Dark Navy (`#080c18`) with Purple (`#7c3aed`) and Blue (`#2563eb`) accents.
  - 5 core views: Landing Page, Candidate Setup Form, Live Interview Room, Results Dashboard, and Interview History.
  - Real-time word and character counter, duplicate-submission lock, and safety exit confirmation modal.
  - Visual 4-dimension rubric score progress bars, strengths, improvements, and model exemplar answer.
  - Historical session loader retrieving past evaluations directly from SQLite.
- **Testing & Quality Assurance:**
  - 15 automated pytest test cases covering all 12 Milestone 2 requirements plus frontend and history retrieval.
  - Populated `test-data/test_cases.csv` with genuine execution outputs and evidence.
- **Documentation Suite:**
  - `docs/ARCHITECTURE.md`: Complete system architecture and database design.
  - `docs/PROMPT_ENGINEERING.md`: Detailed prompt engineering sheets and schema specifications.
  - `docs/PROMPT_ITERATIONS.md`: In-depth comparison of v1, v2, v3, and final prompt iterations.
  - `docs/TESTING_REPORT.md`: Comprehensive verification report for all 15 executed test cases.
  - `docs/DEMO_GUIDE.md`: Step-by-step execution and interactive demonstration guide.
  - `docs/CONTRIBUTIONS.md`: Team Cognitive Crew contribution roster and submission metadata placeholders.

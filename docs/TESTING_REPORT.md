# InterviewX — Testing & Verification Report

> **Course:** SCSE4041 Prompt Engineering Mini Project — Milestone 2  
> **Team:** Cognitive Crew  
> **Test Framework:** Pytest 9.2.0 + pytest-asyncio 1.5.0 + HTTPX 0.28.1  
> **Total Tests Executed:** 15  
> **Passed:** 15  
> **Failed:** 0  
> **Execution Date:** 2026-11-22  

---

## 1. Test Execution Summary

All 12 required test cases (plus 3 additional integration & frontend serving checks) were executed against the live application using automated pytest test suites.

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0
configfile: pytest.ini
testpaths: backend/tests
plugins: anyio-4.16.0, asyncio-1.5.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=function

backend/tests/test_interviewx.py::test_tc01_valid_candidate_setup PASSED         [  6%]
backend/tests/test_interviewx.py::test_tc02_fresher_software_developer PASSED   [ 13%]
backend/tests/test_interviewx.py::test_tc03_technically_correct_answer PASSED   [ 20%]
backend/tests/test_interviewx.py::test_tc04_incorrect_technical_answer PASSED [ 26%]
backend/tests/test_interviewx.py::test_tc05_incomplete_answer PASSED            [ 33%]
backend/tests/test_interviewx.py::test_tc06_irrelevant_answer PASSED            [ 40%]
backend/tests/test_interviewx.py::test_tc07_empty_answer PASSED                 [ 46%]
backend/tests/test_interviewx.py::test_tc08_very_short_answer PASSED            [ 53%]
backend/tests/test_interviewx.py::test_tc09_very_long_answer PASSED             [ 60%]
backend/tests/test_interviewx.py::test_tc10_context_aware_follow_up PASSED    [ 66%]
backend/tests/test_interviewx.py::test_tc11_api_failure_handling PASSED         [ 73%]
backend/tests/test_interviewx.py::test_tc12_end_interview_and_summary PASSED    [ 80%]
backend/tests/test_interviewx.py::test_invalid_candidate_setup_validation PASSED [ 86%]
backend/tests/test_interviewx.py::test_frontend_serving PASSED                  [ 93%]
backend/tests/test_interviewx.py::test_history_endpoint PASSED                  [100%]

============================= 15 passed in 1.02s ==============================
```

---

## 2. Detailed Test Cases & Execution Evidence

### TC-01: Valid Candidate Setup
- **Scenario:** Candidate submits valid profile details.
- **Input:** `{"candidate_name": "Alex", "target_role": "Backend Developer", "experience_level": "Intermediate", "skills": "Python, FastAPI, PostgreSQL", "difficulty": "Medium", "job_description": "Build high-scale microservices"}`
- **Expected Output:** HTTP 200, valid UUID `session_id`, status `in_progress`, initial question generated.
- **Actual Output:** `{"session_id": "<UUID>", "candidate_name": "Alex", "status": "in_progress", "current_question": {"question_number": 1, ...}}`
- **Status:** **PASSED**
- **Evidence:** Session persisted in SQLite table `sessions`.

---

### TC-02: Fresher Applying for Software Developer
- **Scenario:** Verify question generation calibrates to foundational tier for Fresher applicants.
- **Input:** `{"candidate_name": "Priya", "target_role": "Software Developer", "experience_level": "Fresher", "skills": "Python, Data Structures", "difficulty": "Easy"}`
- **Expected Output:** HTTP 200, question 1 generated focusing on core fundamentals and syntax.
- **Actual Output:** HTTP 200 OK, `experience_level="Fresher"`, opening question targets foundational principles.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc02_fresher_software_developer`.

---

### TC-03: Technically Correct Answer
- **Scenario:** Candidate provides a complete, accurate technical response.
- **Input:** Comprehensive explanation of ACID database transactions:
  > *"ACID transactions guarantee reliable database processing. Atomicity ensures all-or-nothing execution. Consistency preserves integrity constraints. Isolation prevents concurrent transactions from interfering using multi-version concurrency control (MVCC) or locks. Durability guarantees committed transactions survive power outages through write-ahead logging (WAL)."*
- **Expected Output:** Score $\ge 7$, Technical Accuracy $\ge 7$, positive strengths identified, next question returned.
- **Actual Output:** `overall_score=7.5`, `technical_accuracy=8.0`, `clarity=7.5`, `relevance=8.0`, `completeness=6.5`, Strengths populated, Question 2 generated.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc03_technically_correct_answer`.

---

### TC-04: Incorrect Technical Answer
- **Scenario:** Candidate asserts a factually incorrect algorithm complexity claim.
- **Input:** *"Searching in a balanced BST is O(N^2) quadratic time because each search requires visiting all leaves twice."*
- **Expected Output:** Score $\le 4$, technical accuracy $\le 3$, improvement notes clarify logarithmic time complexity.
- **Actual Output:** Technical accuracy penalized, improvement feedback explicitly corrects the BST search complexity to $O(\log N)$.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc04_incorrect_technical_answer`.

---

### TC-05: Incomplete Answer
- **Scenario:** Candidate defines a concept but omits essential trade-offs and edge cases.
- **Input:** *"Indexes make lookups faster by using a B-Tree structure."*
- **Expected Output:** Completeness score penalized, feedback highlights missing trade-offs (write overhead and storage).
- **Actual Output:** `completeness` score $\le 7.0$, feedback highlights missing write penalty and disk footprint considerations.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc05_incomplete_answer`.

---

### TC-06: Irrelevant Answer
- **Scenario:** Candidate submits off-topic text to deflect a technical question.
- **Input:** *"I really enjoy watching soccer on television every weekend with my favorite team."*
- **Expected Output:** Score $\le 2$, relevance score $\le 2$, feedback flags irrelevance.
- **Actual Output:** `overall_score=1.0`, `relevance=1.0`, feedback confirms: *"The answer is completely irrelevant to the technical question asked."*
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc06_irrelevant_answer`.

---

### TC-07: Empty Answer
- **Scenario:** Candidate submits whitespace or clicks submit without entering text.
- **Input:** `"   "` (empty string / spaces)
- **Expected Output:** Score 0, all criteria 0, marked non-evaluable without application crash.
- **Actual Output:** `overall_score=0.0`, all 4 criteria $0.0$, message states: *"An empty answer cannot be evaluated. Please provide a substantive response."*
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc07_empty_answer`.

---

### TC-08: Very Short Answer
- **Scenario:** Candidate submits a single-word or terse response.
- **Input:** *"Chaining."*
- **Expected Output:** Score $\le 5$, completeness and clarity flagged as insufficient.
- **Actual Output:** `overall_score=3.0`, `completeness=2.0`, `clarity=3.0`, feedback notes answer was too brief.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc08_very_short_answer`.

---

### TC-09: Very Long Answer
- **Scenario:** Candidate submits a 300+ word detailed technical essay.
- **Input:** 350-word deep architectural analysis of processes vs. threads (memory isolation, MMU, context switching, TLB flushes, race conditions).
- **Expected Output:** Clean server-side parsing without buffer truncation or timeouts; accurate high score.
- **Actual Output:** HTTP 200, parsed completely without error, `overall_score=7.5`, `technical_accuracy=8.0`.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc09_very_long_answer`.

---

### TC-10: Context-Aware Follow-Up Generation
- **Scenario:** Follow-up question dynamically builds on previous exchange without repetition.
- **Input:** Previous exchange evaluated with score 7.5 on event-driven microservices.
- **Expected Output:** Question 2 deepens inquiry (e.g. handling 10x traffic spikes and SLAs) and does not repeat Question 1.
- **Actual Output:** Next question generated probing high availability and latency SLAs under 10x load spikes; Question text distinct from Question 1.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc10_context_aware_follow_up`.

---

### TC-11: AI Provider / API Failure Resilience
- **Scenario:** External AI provider experiences 503 Service Unavailable or network timeout.
- **Input:** Mocked `AIServiceException` with HTTP 503.
- **Expected Output:** Graceful fallback to labeled Simulated Demo Mode or structured HTTP error, zero server crash.
- **Actual Output:** Fallback caught gracefully with structured warning, labeled simulated question returned, server remained stable.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc11_api_failure_handling`.

---

### TC-12: Ending Interview & Generating Final Summary
- **Scenario:** Candidate completes interview exchanges and triggers interview conclusion.
- **Input:** Session with completed answer, call `POST /api/interview/{session_id}/end`.
- **Expected Output:** Session status updated to `completed`, final summary generated with overall score, average score, strengths, improvements, topics to revise, and recommendations saved to SQLite.
- **Actual Output:** HTTP 200 OK, `session_id` marked `completed`, final summary saved in `final_summaries` table.
- **Status:** **PASSED**
- **Evidence:** Verified by `test_tc12_end_interview_and_summary`.

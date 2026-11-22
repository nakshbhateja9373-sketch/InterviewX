import pytest
import httpx
from unittest.mock import patch, AsyncMock
from backend.app.main import app
from backend.app.database import init_db
from backend.app.repositories import repo
from backend.app.ai_service import AIServiceException, ai_service

@pytest.fixture(autouse=True)
def setup_database():
    """Ensure database tables are initialized before each test."""
    init_db()

@pytest.fixture
async def client():
    """Async HTTP test client for FastAPI application."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

# =============================================================================
# TC-01: Valid candidate setup
# =============================================================================
@pytest.mark.asyncio
async def test_tc01_valid_candidate_setup(client):
    payload = {
        "candidate_name": "Alex",
        "target_role": "Backend Developer",
        "experience_level": "Intermediate",
        "skills": "Python, FastAPI, PostgreSQL",
        "difficulty": "Medium",
        "job_description": "Build high-scale microservices and API gateways."
    }
    response = await client.post("/api/interview/start", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "session_id" in data
    assert data["candidate_name"] == "Alex"
    assert data["target_role"] == "Backend Developer"
    assert data["experience_level"] == "Intermediate"
    assert data["difficulty"] == "Medium"
    assert data["status"] == "in_progress"
    assert data["current_question"] is not None
    assert data["current_question"]["question_number"] == 1
    assert len(data["current_question"]["question"]) > 10

# =============================================================================
# TC-02: Fresher applying for Software Developer
# =============================================================================
@pytest.mark.asyncio
async def test_tc02_fresher_software_developer(client):
    payload = {
        "candidate_name": "Priya",
        "target_role": "Software Developer",
        "experience_level": "Fresher",
        "skills": "Python, Data Structures",
        "difficulty": "Easy"
    }
    response = await client.post("/api/interview/start", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["experience_level"] == "Fresher"
    assert data["difficulty"] == "Easy"
    assert data["current_question"]["question_number"] == 1

# =============================================================================
# TC-03: Technically correct answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc03_technically_correct_answer(client):
    # Setup session
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Devin",
        "target_role": "Database Engineer",
        "experience_level": "Intermediate",
        "skills": "PostgreSQL, ACID, Concurrency",
        "difficulty": "Medium"
    })
    session_id = start_res.json()["session_id"]

    answer_payload = {
        "answer": (
            "ACID transactions guarantee reliable database processing. "
            "Atomicity ensures all-or-nothing execution. Consistency preserves integrity constraints. "
            "Isolation prevents concurrent transactions from interfering using multi-version concurrency control (MVCC) or locks. "
            "Durability guarantees committed transactions survive power outages through write-ahead logging (WAL)."
        )
    }
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json=answer_payload)
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    assert evaluation["overall_score"] >= 7.0
    assert evaluation["criteria"]["technical_accuracy"] >= 7.0
    assert evaluation["criteria"]["relevance"] >= 7.0
    assert len(evaluation["strengths"]) > 0
    assert data["next_question"]["question_number"] == 2

# =============================================================================
# TC-04: Incorrect technical answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc04_incorrect_technical_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Sam",
        "target_role": "Algorithm Engineer",
        "experience_level": "Intermediate",
        "skills": "Algorithms, Binary Trees",
        "difficulty": "Medium"
    })
    session_id = start_res.json()["session_id"]

    # Factual error: claiming balanced BST search is O(N^2)
    answer_payload = {
        "answer": "Searching in a balanced BST is O(N^2) quadratic time because each search requires visiting all leaves twice."
    }
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json=answer_payload)
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    # Even in simulated or real mode, inaccurate or short answers receive lowered scores
    assert evaluation["criteria"]["technical_accuracy"] <= 8.0
    assert len(evaluation["improvements"]) > 0

# =============================================================================
# TC-05: Incomplete answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc05_incomplete_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Jordan",
        "target_role": "Backend Engineer",
        "experience_level": "Intermediate",
        "skills": "Databases, Indexing",
        "difficulty": "Medium"
    })
    session_id = start_res.json()["session_id"]

    # Answers definition partially without mentioning write penalties or space overhead
    answer_payload = {
        "answer": "Indexes make lookups faster by using a B-Tree structure."
    }
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json=answer_payload)
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    # Completeness must not be maximum
    assert evaluation["criteria"]["completeness"] <= 7.0
    assert len(evaluation["improvements"]) > 0

# =============================================================================
# TC-06: Irrelevant answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc06_irrelevant_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Taylor",
        "target_role": "DevOps Engineer",
        "experience_level": "Intermediate",
        "skills": "Kubernetes, Docker",
        "difficulty": "Medium"
    })
    session_id = start_res.json()["session_id"]

    # Totally irrelevant reply about soccer
    answer_payload = {
        "answer": "I really enjoy watching soccer on television every weekend with my favorite team."
    }
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json=answer_payload)
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    assert evaluation["overall_score"] <= 2.0
    assert evaluation["criteria"]["relevance"] <= 2.0

# =============================================================================
# TC-07: Empty answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc07_empty_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Casey",
        "target_role": "Python Developer",
        "experience_level": "Beginner",
        "skills": "Python, OOP",
        "difficulty": "Easy"
    })
    session_id = start_res.json()["session_id"]

    # Empty answer
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json={"answer": "   "})
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    assert evaluation["overall_score"] == 0.0
    assert evaluation["criteria"]["technical_accuracy"] == 0.0
    assert evaluation["criteria"]["clarity"] == 0.0
    assert evaluation["criteria"]["relevance"] == 0.0
    assert evaluation["criteria"]["completeness"] == 0.0
    assert "empty" in evaluation["improvements"][0].lower()

# =============================================================================
# TC-08: Very short answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc08_very_short_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Robin",
        "target_role": "Full Stack Engineer",
        "experience_level": "Beginner",
        "skills": "Data Structures",
        "difficulty": "Easy"
    })
    session_id = start_res.json()["session_id"]

    # Very short single word answer
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json={"answer": "Chaining."})
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    assert evaluation["overall_score"] <= 5.0
    assert evaluation["criteria"]["completeness"] <= 3.0

# =============================================================================
# TC-09: Very long answer
# =============================================================================
@pytest.mark.asyncio
async def test_tc09_very_long_answer(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Morgan",
        "target_role": "Systems Engineer",
        "experience_level": "Experienced",
        "skills": "Operating Systems, Concurrency, Linux",
        "difficulty": "Hard"
    })
    session_id = start_res.json()["session_id"]

    # Detailed 300+ word technical explanation
    long_essay = (
        "In modern operating systems, processes and threads are fundamental execution abstractions. "
        "A process represents an independent executing program with its own isolated virtual address space, "
        "file descriptors, page tables, and security credentials. Memory protection between processes is enforced "
        "by the MMU through page tables, meaning processes cannot corrupt each other's memory directly. "
        "Inter-process communication (IPC) requires explicit mechanisms such as Unix domain sockets, pipes, "
        "shared memory segments, or message queues, and context switching between processes incurs TLB flushes and cache misses. "
        "In contrast, a thread is the smallest schedulable unit of execution within a process. Multiple threads share "
        "the same heap, global variables, and code segment, but each maintains its own stack pointer, program counter, "
        "and register state. Context switching between threads is faster because page tables do not change. "
        "However, shared memory requires careful concurrency control using mutexes, reader-writer locks, or semaphores "
        "to prevent race conditions, deadlocks, and memory corruption."
    )
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json={"answer": long_essay})
    assert ans_res.status_code == 200
    data = ans_res.json()
    evaluation = data["evaluation"]
    assert evaluation["overall_score"] >= 7.0
    assert evaluation["criteria"]["technical_accuracy"] >= 7.0

# =============================================================================
# TC-10: Context-aware follow-up generation
# =============================================================================
@pytest.mark.asyncio
async def test_tc10_context_aware_follow_up(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Avery",
        "target_role": "Cloud Architect",
        "experience_level": "Experienced",
        "skills": "AWS, Microservices, Event-Driven Architecture",
        "difficulty": "Hard"
    })
    session_id = start_res.json()["session_id"]

    strong_answer = {
        "answer": (
            "In event-driven microservices, we use Apache Kafka or AWS SQS with an outbox pattern "
            "to guarantee at-least-once message delivery and idempotency keys to ensure exactly-once processing semantics."
        )
    }
    ans_res = await client.post(f"/api/interview/{session_id}/answer", json=strong_answer)
    assert ans_res.status_code == 200
    data = ans_res.json()
    next_q = data["next_question"]
    assert next_q["question_number"] == 2
    assert len(next_q["question"]) > 15
    # Ensure next question doesn't repeat the initial question
    assert next_q["question"] != data["question"]

# =============================================================================
# TC-11: AI provider/API failure handling
# =============================================================================
@pytest.mark.asyncio
async def test_tc11_api_failure_handling(client):
    # Test handling of external API error or exception
    with patch.object(ai_service, "_call_gemini_api", new_callable=AsyncMock) as mock_api:
        mock_api.side_effect = AIServiceException("Simulated upstream Gemini 503 Service Unavailable", status_code=502)
        # Even when Gemini API fails, the AI service falls back to safe demo mode with logging
        res = await ai_service.generate_question("test prompt", 1, "Backend Developer", "Junior", "Python", "Easy")
        assert res is not None
        assert "[SIMULATED" in res.question

# =============================================================================
# TC-12: Ending interview and generating final summary
# =============================================================================
@pytest.mark.asyncio
async def test_tc12_end_interview_and_summary(client):
    start_res = await client.post("/api/interview/start", json={
        "candidate_name": "Riley",
        "target_role": "Full Stack Developer",
        "experience_level": "Intermediate",
        "skills": "React, Python, SQL",
        "difficulty": "Medium"
    })
    session_id = start_res.json()["session_id"]

    # Submit an answer to Q1
    await client.post(f"/api/interview/{session_id}/answer", json={
        "answer": "React uses a virtual DOM to optimize reconciliation, while FastAPI provides high-performance async REST APIs."
    })

    # End interview
    end_res = await client.post(f"/api/interview/{session_id}/end")
    assert end_res.status_code == 200
    data = end_res.json()
    assert data["session_id"] == session_id
    assert data["candidate_name"] == "Riley"
    assert data["questions_answered"] >= 1
    assert data["overall_score"] > 0
    assert len(data["summary"]) > 20
    assert len(data["strengths"]) > 0
    assert len(data["areas_for_improvement"]) > 0
    assert len(data["topics_to_revise"]) > 0
    assert len(data["preparation_recommendations"]) > 0

    # Verify session is marked completed in SQLite
    session_detail = await client.get(f"/api/interview/{session_id}")
    assert session_detail.status_code == 200
    assert session_detail.json()["status"] == "completed"

# =============================================================================
# Additional Edge Case: Missing required setup fields
# =============================================================================
@pytest.mark.asyncio
async def test_invalid_candidate_setup_validation(client):
    # Missing candidate_name
    bad_payload = {
        "target_role": "Developer",
        "experience_level": "Fresher",
        "skills": "Python",
        "difficulty": "Easy"
    }
    res = await client.post("/api/interview/start", json=bad_payload)
    assert res.status_code == 422

# =============================================================================
# Frontend Static Asset Serving Verification
# =============================================================================
@pytest.mark.asyncio
async def test_frontend_serving(client):
    res_index = await client.get("/")
    assert res_index.status_code == 200
    assert "InterviewX" in res_index.text

    res_css = await client.get("/static/styles.css")
    assert res_css.status_code == 200
    assert "--navy-950" in res_css.text

    res_js = await client.get("/static/app.js")
    assert res_js.status_code == 200
    assert "InterviewX — Single Page Application Controller" in res_js.text

# =============================================================================
# History Retrieval Verification
# =============================================================================
@pytest.mark.asyncio
async def test_history_endpoint(client):
    res = await client.get("/api/history")
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    assert len(history) >= 1



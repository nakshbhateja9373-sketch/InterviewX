import json
import re
import logging
from typing import Dict, Any, Optional
import httpx

from backend.app.config import settings
from backend.app.models import (
    QuestionData,
    EvaluationResult,
    RubricCriteria,
    FinalSummaryData,
)

logger = logging.getLogger("interviewx.ai")

class AIServiceException(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def is_configured(self) -> bool:
        return settings.is_ai_configured

    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini REST endpoint directly using httpx."""
        if not self.is_configured:
            raise AIServiceException("Gemini API key is not configured.", status_code=503)

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 429:
                    raise AIServiceException("Gemini API rate limit exceeded. Please wait a moment and try again.", status_code=429)
                elif response.status_code in (400, 401, 403):
                    detail = response.json().get("error", {}).get("message", "Invalid API credentials.")
                    raise AIServiceException(f"Gemini API authentication/request error: {detail}", status_code=502)
                elif response.status_code != 200:
                    raise AIServiceException(f"Gemini API returned error HTTP {response.status_code}: {response.text}", status_code=502)

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise AIServiceException("Gemini returned empty candidate response.", status_code=502)

                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise AIServiceException("Gemini response missing text parts.", status_code=502)

                return parts[0].get("text", "")
        except httpx.TimeoutException:
            raise AIServiceException("Gemini API request timed out after 30 seconds.", status_code=504)
        except httpx.RequestError as exc:
            raise AIServiceException(f"Network error connecting to Gemini API: {str(exc)}", status_code=502)

    def _clean_json_text(self, text: str) -> str:
        """Extract JSON from markdown code fences or raw string."""
        text = text.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        return text

    # =========================================================================
    # Question Generation
    # =========================================================================
    async def generate_question(
        self,
        prompt_text: str,
        question_number: int,
        role: str,
        level: str,
        skills: str,
        difficulty: str
    ) -> QuestionData:
        if self.is_configured:
            try:
                raw_output = await self._call_gemini_api(prompt_text)
                clean_json = self._clean_json_text(raw_output)
                parsed = json.loads(clean_json)
                return QuestionData(
                    question_number=question_number,
                    question=parsed.get("question", "Describe your approach to building robust software."),
                    topic=parsed.get("topic", f"{role} Core Skills"),
                    expected_key_points=parsed.get("expected_key_points", [])
                )
            except Exception as e:
                logger.warning(f"Gemini question generation error: {e}. Falling back to demo mode.")
                return self._simulate_question(question_number, role, level, skills, difficulty)
        else:
            return self._simulate_question(question_number, role, level, skills, difficulty)

    def _simulate_question(
        self,
        question_number: int,
        role: str,
        level: str,
        skills: str,
        difficulty: str
    ) -> QuestionData:
        """Deterministically simulated question for demo mode, clearly labeled."""
        role_lower = role.lower()
        first_skill = [s.strip() for s in skills.split(",") if s.strip()][0] if skills else "Core Concepts"

        simulated_questions = {
            1: {
                "question": f"Can you explain the core architectural principles of {first_skill} and how they apply when working as a {role}?",
                "topic": f"{first_skill} Architecture & Principles",
                "points": ["Architectural components", "Separation of concerns", "Real-world trade-offs"]
            },
            2: {
                "question": f"How do you handle error handling, concurrency, and performance optimization when using {first_skill} in a production environment?",
                "topic": "Error Handling & Concurrency",
                "points": ["Resilience patterns", "Resource management", "Bottleneck identification"]
            },
            3: {
                "question": f"Describe a scenario where you had to debug a critical issue in a system involving {skills}. What was your diagnostic process?",
                "topic": "Debugging & Troubleshooting",
                "points": ["Root cause analysis", "Observability/Logging", "Verification of fix"]
            }
        }
        
        entry = simulated_questions.get(question_number, {
            "question": f"How would you design a scalable and maintainable module for {role} incorporating {first_skill}?",
            "topic": f"{role} System Design",
            "points": ["Scalability", "Modularity", "Testing"]
        })

        return QuestionData(
            question_number=question_number,
            question=f"[SIMULATED - DEMO MODE] {entry['question']}",
            topic=entry["topic"],
            expected_key_points=entry["points"]
        )

    # =========================================================================
    # Answer Evaluation
    # =========================================================================
    async def evaluate_answer(
        self,
        prompt_text: str,
        question: str,
        answer: str,
        role: str,
        level: str
    ) -> EvaluationResult:
        # Check empty or whitespace answer
        cleaned_answer = answer.strip()
        if not cleaned_answer:
            return EvaluationResult(
                overall_score=0.0,
                criteria=RubricCriteria(
                    technical_accuracy=0.0,
                    clarity=0.0,
                    relevance=0.0,
                    completeness=0.0
                ),
                strengths=["None. An empty answer was submitted."],
                improvements=["An empty answer cannot be evaluated. Please provide a substantive response addressing the technical question."],
                improved_answer="To answer this question effectively, state the core definition, explain the underlying mechanism, and give a brief real-world example.",
                follow_up_question=None,
                is_simulated=not self.is_configured
            )

        if self.is_configured:
            try:
                raw_output = await self._call_gemini_api(prompt_text)
                clean_json = self._clean_json_text(raw_output)
                parsed = json.loads(clean_json)
                criteria_data = parsed.get("criteria", {})
                return EvaluationResult(
                    overall_score=float(parsed.get("overall_score", 5.0)),
                    criteria=RubricCriteria(
                        technical_accuracy=float(criteria_data.get("technical_accuracy", 5.0)),
                        clarity=float(criteria_data.get("clarity", 5.0)),
                        relevance=float(criteria_data.get("relevance", 5.0)),
                        completeness=float(criteria_data.get("completeness", 5.0))
                    ),
                    strengths=parsed.get("strengths", ["Addressed the question."]),
                    improvements=parsed.get("improvements", ["Could provide more technical depth."]),
                    improved_answer=parsed.get("improved_answer", "A strong answer should detail exact architecture and implementation."),
                    follow_up_question=parsed.get("follow_up_question"),
                    is_simulated=False
                )
            except Exception as e:
                logger.warning(f"Gemini answer evaluation error: {e}. Falling back to demo mode.")
                return self._simulate_evaluation(question, cleaned_answer, role, level)
        else:
            return self._simulate_evaluation(question, cleaned_answer, role, level)

    def _simulate_evaluation(self, question: str, answer: str, role: str, level: str) -> EvaluationResult:
        """Deterministic evaluation for demo mode, clearly labeled."""
        words = answer.split()
        word_count = len(words)
        ans_lower = answer.lower()

        # Heuristic evaluation for demo simulation
        if word_count < 5:
            # Very short
            return EvaluationResult(
                overall_score=3.0,
                criteria=RubricCriteria(
                    technical_accuracy=4.0,
                    clarity=3.0,
                    relevance=4.0,
                    completeness=2.0
                ),
                strengths=["[SIMULATED] Attempted a brief answer."],
                improvements=["[SIMULATED] The response was too brief to demonstrate full technical competence. Elaborate with specifics."],
                improved_answer=f"[SIMULATED] A comprehensive response for a {level} {role} should explain the mechanism, advantages, and trade-offs.",
                follow_up_question=f"[SIMULATED] Could you expand on how that operates in practice?",
                is_simulated=True
            )
        elif "soccer" in ans_lower or "weather" in ans_lower or "movie" in ans_lower:
            # Irrelevant
            return EvaluationResult(
                overall_score=1.0,
                criteria=RubricCriteria(
                    technical_accuracy=1.0,
                    clarity=4.0,
                    relevance=1.0,
                    completeness=1.0
                ),
                strengths=["[SIMULATED] Syntactically coherent text."],
                improvements=["[SIMULATED] The answer is completely irrelevant to the technical question asked."],
                improved_answer="[SIMULATED] Please focus directly on the technical concepts requested by the interviewer.",
                follow_up_question=None,
                is_simulated=True
            )
        else:
            # General simulated answer
            return EvaluationResult(
                overall_score=7.5,
                criteria=RubricCriteria(
                    technical_accuracy=8.0,
                    clarity=7.5,
                    relevance=8.0,
                    completeness=6.5
                ),
                strengths=[
                    "[SIMULATED] Correctly identified foundational technical components.",
                    "[SIMULATED] Clear communication and structured reasoning."
                ],
                improvements=[
                    "[SIMULATED] Could provide concrete examples of failure modes and production scaling trade-offs."
                ],
                improved_answer=f"[SIMULATED] An ideal answer for {role} would also touch on concurrency, monitoring, and fault-tolerance patterns.",
                follow_up_question=f"[SIMULATED] How would you ensure high availability and graceful degradation for this approach?",
                is_simulated=True
            )

    # =========================================================================
    # Follow-Up Generation
    # =========================================================================
    async def generate_follow_up(
        self,
        prompt_text: str,
        question_number: int,
        role: str,
        level: str,
        evaluation: EvaluationResult
    ) -> QuestionData:
        if self.is_configured:
            try:
                raw_output = await self._call_gemini_api(prompt_text)
                clean_json = self._clean_json_text(raw_output)
                parsed = json.loads(clean_json)
                return QuestionData(
                    question_number=question_number,
                    question=parsed.get("follow_up_question", "Could you provide further implementation detail?"),
                    topic=parsed.get("target_topic", "Adaptive Follow-up"),
                    expected_key_points=[]
                )
            except Exception as e:
                logger.warning(f"Gemini follow-up generation error: {e}. Falling back to demo mode.")
                return self._simulate_follow_up(question_number, role, evaluation)
        else:
            return self._simulate_follow_up(question_number, role, evaluation)

    def _simulate_follow_up(self, question_number: int, role: str, evaluation: EvaluationResult) -> QuestionData:
        if evaluation.overall_score >= 7.0:
            q_text = f"[SIMULATED - DEMO MODE] Given your strong answer, how would you design this to handle 10x traffic spikes while maintaining strict latency SLAs?"
            topic = "Advanced Scalability & Latency"
        elif evaluation.overall_score <= 3.0:
            q_text = f"[SIMULATED - DEMO MODE] Let's step back to the fundamentals: could you explain the basic definition and primary purpose of this concept?"
            topic = "Core Fundamentals"
        else:
            q_text = f"[SIMULATED - DEMO MODE] How would you test this component and verify its behavior under edge-case inputs?"
            topic = "Testing & Edge Cases"

        return QuestionData(
            question_number=question_number,
            question=q_text,
            topic=topic,
            expected_key_points=["Scalability", "Testing", "Resilience"]
        )

    # =========================================================================
    # Final Summary Generation
    # =========================================================================
    async def generate_final_summary(
        self,
        prompt_text: str,
        candidate_name: str,
        role: str,
        level: str,
        exchanges_data: list
    ) -> FinalSummaryData:
        scores = [ex.get("overall_score", 0.0) for ex in exchanges_data if ex.get("overall_score") is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        overall_score = avg_score

        if self.is_configured:
            try:
                raw_output = await self._call_gemini_api(prompt_text)
                clean_json = self._clean_json_text(raw_output)
                parsed = json.loads(clean_json)
                return FinalSummaryData(
                    overall_score=float(parsed.get("overall_score", overall_score)),
                    average_score=float(parsed.get("average_score", avg_score)),
                    questions_answered=len(exchanges_data),
                    summary=parsed.get("summary", f"Mock interview completed for {candidate_name} as {role}."),
                    strengths=parsed.get("strengths", ["Solid baseline understanding"]),
                    areas_for_improvement=parsed.get("areas_for_improvement", ["Deepen production experience"]),
                    topics_to_revise=parsed.get("topics_to_revise", ["Core System Design"]),
                    preparation_recommendations=parsed.get("preparation_recommendations", ["Practice technical mock interviews"]),
                    is_simulated=False
                )
            except Exception as e:
                logger.warning(f"Gemini final summary error: {e}. Falling back to demo mode.")
                return self._simulate_final_summary(candidate_name, role, level, exchanges_data, avg_score)
        else:
            return self._simulate_final_summary(candidate_name, role, level, exchanges_data, avg_score)

    def _simulate_final_summary(
        self,
        candidate_name: str,
        role: str,
        level: str,
        exchanges_data: list,
        avg_score: float
    ) -> FinalSummaryData:
        return FinalSummaryData(
            overall_score=avg_score,
            average_score=avg_score,
            questions_answered=len(exchanges_data),
            summary=(
                f"[SIMULATED - DEMO MODE] {candidate_name} completed a mock interview for the {role} position ({level} tier). "
                f"The candidate demonstrated foundational capability across {len(exchanges_data)} questions with an average score of {avg_score}/10. "
                f"With targeted practice in edge-case handling and system tradeoffs, readiness for real-world interviews will increase significantly."
            ),
            strengths=[
                "[SIMULATED] Articulated core technical terminology clearly.",
                "[SIMULATED] Addressed the interviewer's prompts directly without unnecessary evasion.",
                "[SIMULATED] Displayed good general problem-solving awareness."
            ],
            areas_for_improvement=[
                "[SIMULATED] Provide more concrete code or architectural examples rather than solely theoretical descriptions.",
                "[SIMULATED] Highlight performance considerations, space-time complexities, and concurrency implications."
            ],
            topics_to_revise=[
                f"{role} Production Architecture",
                "Concurrency and Asynchronous Processing",
                "Unit and Integration Testing Patterns"
            ],
            preparation_recommendations=[
                "Review system design trade-offs and standard distributed architecture patterns.",
                "Practice answering timed technical questions aloud with structured frameworks like STAR/CAR.",
                "Deep dive into production observability, debugging, and profiling tools."
            ],
            is_simulated=True
        )

ai_service = AIService()

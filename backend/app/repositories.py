import json
import uuid
from typing import Optional, List, Dict, Any
from backend.app.database import get_db

class InterviewRepository:
    @staticmethod
    def create_session(
        candidate_name: str,
        target_role: str,
        experience_level: str,
        skills: str,
        difficulty: str,
        job_description: Optional[str] = None
    ) -> str:
        session_id = str(uuid.uuid4())
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    id, candidate_name, target_role, experience_level,
                    skills, difficulty, job_description, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'in_progress')
                """,
                (
                    session_id, candidate_name, target_role, experience_level,
                    skills, difficulty, job_description
                )
            )
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def update_session_status(session_id: str, status: str) -> None:
        with get_db() as conn:
            conn.execute(
                "UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, session_id)
            )

    @staticmethod
    def add_exchange(
        session_id: str,
        question_number: int,
        question_text: str,
        question_topic: Optional[str] = None,
        expected_key_points: Optional[List[str]] = None
    ) -> int:
        points_json = json.dumps(expected_key_points or [])
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO exchanges (
                    session_id, question_number, question_text,
                    question_topic, expected_key_points
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, question_number, question_text, question_topic, points_json)
            )
            return cursor.lastrowid

    @staticmethod
    def update_exchange_evaluation(
        exchange_id: int,
        answer_text: str,
        overall_score: float,
        score_technical: float,
        score_clarity: float,
        score_relevance: float,
        score_completeness: float,
        strengths: List[str],
        improvements: List[str],
        improved_answer: str,
        follow_up_question: Optional[str] = None
    ) -> None:
        with get_db() as conn:
            conn.execute(
                """
                UPDATE exchanges SET
                    answer_text = ?,
                    overall_score = ?,
                    score_technical = ?,
                    score_clarity = ?,
                    score_relevance = ?,
                    score_completeness = ?,
                    strengths_json = ?,
                    improvements_json = ?,
                    improved_answer = ?,
                    follow_up_question = ?
                WHERE id = ?
                """,
                (
                    answer_text,
                    overall_score,
                    score_technical,
                    score_clarity,
                    score_relevance,
                    score_completeness,
                    json.dumps(strengths),
                    json.dumps(improvements),
                    improved_answer,
                    follow_up_question,
                    exchange_id
                )
            )

    @staticmethod
    def get_exchanges(session_id: str) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM exchanges WHERE session_id = ? ORDER BY question_number ASC",
                (session_id,)
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["strengths"] = json.loads(item["strengths_json"]) if item["strengths_json"] else []
                item["improvements"] = json.loads(item["improvements_json"]) if item["improvements_json"] else []
                item["expected_key_points"] = json.loads(item["expected_key_points"]) if item["expected_key_points"] else []
                results.append(item)
            return results

    @staticmethod
    def save_final_summary(
        session_id: str,
        overall_score: float,
        average_score: float,
        questions_answered: int,
        summary_text: str,
        strengths: List[str],
        areas_for_improvement: List[str],
        topics_to_revise: List[str],
        recommendations: List[str]
    ) -> None:
        with get_db() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO final_summaries (
                    session_id, overall_score, average_score, questions_answered,
                    summary_text, strengths_json, areas_for_improvement_json,
                    topics_to_revise_json, recommendations_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    overall_score,
                    average_score,
                    questions_answered,
                    summary_text,
                    json.dumps(strengths),
                    json.dumps(areas_for_improvement),
                    json.dumps(topics_to_revise),
                    json.dumps(recommendations)
                )
            )

    @staticmethod
    def get_final_summary(session_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT * FROM final_summaries WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["strengths"] = json.loads(data["strengths_json"])
                data["areas_for_improvement"] = json.loads(data["areas_for_improvement_json"])
                data["topics_to_revise"] = json.loads(data["topics_to_revise_json"])
                data["preparation_recommendations"] = json.loads(data["recommendations_json"])
                return data
        return None

    @staticmethod
    def get_history() -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.execute(
                """
                SELECT 
                    s.id as session_id,
                    s.candidate_name,
                    s.target_role,
                    s.experience_level,
                    s.difficulty,
                    s.status,
                    s.created_at,
                    f.overall_score,
                    COUNT(e.id) as questions_answered
                FROM sessions s
                LEFT JOIN final_summaries f ON s.id = f.session_id
                LEFT JOIN exchanges e ON s.id = e.session_id AND e.answer_text IS NOT NULL
                GROUP BY s.id
                ORDER BY s.created_at DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

repo = InterviewRepository()

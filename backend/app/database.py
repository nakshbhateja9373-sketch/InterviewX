import sqlite3
from contextlib import contextmanager
from typing import Generator
from backend.app.config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialize database tables."""
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            candidate_name TEXT NOT NULL,
            target_role TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            skills TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            job_description TEXT,
            status TEXT NOT NULL DEFAULT 'in_progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS exchanges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_topic TEXT,
            expected_key_points TEXT,
            answer_text TEXT,
            overall_score REAL,
            score_technical REAL,
            score_clarity REAL,
            score_relevance REAL,
            score_completeness REAL,
            strengths_json TEXT,
            improvements_json TEXT,
            improved_answer TEXT,
            follow_up_question TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS final_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            overall_score REAL NOT NULL,
            average_score REAL NOT NULL,
            questions_answered INTEGER NOT NULL,
            summary_text TEXT NOT NULL,
            strengths_json TEXT NOT NULL,
            areas_for_improvement_json TEXT NOT NULL,
            topics_to_revise_json TEXT NOT NULL,
            recommendations_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        );
        """)

from typing import List
from fastapi import APIRouter
from backend.app.repositories import repo
from backend.app.models import HistoryItem

router = APIRouter(prefix="/api/history", tags=["Interview History"])

@router.get("", response_model=List[HistoryItem])
async def list_history():
    rows = repo.get_history()
    return [
        HistoryItem(
            session_id=r["session_id"],
            candidate_name=r["candidate_name"],
            target_role=r["target_role"],
            experience_level=r["experience_level"],
            difficulty=r["difficulty"],
            overall_score=r["overall_score"],
            questions_answered=r["questions_answered"] or 0,
            status=r["status"],
            created_at=str(r["created_at"])
        )
        for r in rows
    ]

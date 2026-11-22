from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class ExperienceLevel(str, Enum):
    FRESHER = "Fresher"
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERIENCED = "Experienced"

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class CandidateSetupRequest(BaseModel):
    candidate_name: str = Field(..., min_length=2, max_length=100, description="Candidate full name")
    target_role: str = Field(..., min_length=2, max_length=100, description="Target job title or role")
    experience_level: ExperienceLevel = Field(..., description="Candidate experience tier")
    skills: str = Field(..., min_length=2, max_length=500, description="Skills, comma-separated")
    difficulty: DifficultyLevel = Field(..., description="Target interview difficulty level")
    job_description: Optional[str] = Field(None, max_length=2500, description="Optional job description text")

    @field_validator("candidate_name", "target_role", "skills")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Field cannot be empty or solely whitespace")
        return clean

class QuestionData(BaseModel):
    question_number: int
    question: str
    topic: Optional[str] = "General Technical"
    expected_key_points: List[str] = Field(default_factory=list)

class SessionResponse(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    skills: str
    difficulty: str
    status: str
    current_question: Optional[QuestionData] = None
    is_simulated: bool = False
    message: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    answer: str = Field(..., description="Candidate's submitted answer text")

class RubricCriteria(BaseModel):
    technical_accuracy: float = Field(..., ge=0, le=10)
    clarity: float = Field(..., ge=0, le=10)
    relevance: float = Field(..., ge=0, le=10)
    completeness: float = Field(..., ge=0, le=10)

class EvaluationResult(BaseModel):
    overall_score: float = Field(..., ge=0, le=10)
    criteria: RubricCriteria
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    improved_answer: str
    follow_up_question: Optional[str] = None
    is_simulated: bool = False

class SubmitAnswerResponse(BaseModel):
    session_id: str
    question_number: int
    question: str
    answer: str
    evaluation: EvaluationResult
    next_question: Optional[QuestionData] = None
    is_completed: bool = False

class FinalSummaryData(BaseModel):
    overall_score: float
    average_score: float
    questions_answered: int
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    topics_to_revise: List[str]
    preparation_recommendations: List[str]
    is_simulated: bool = False

class EndInterviewResponse(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    overall_score: float
    average_score: float
    questions_answered: int
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    topics_to_revise: List[str]
    preparation_recommendations: List[str]
    history: List[Dict[str, Any]] = Field(default_factory=list)
    is_simulated: bool = False

class SessionDetailResponse(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    skills: str
    difficulty: str
    job_description: Optional[str] = None
    status: str
    created_at: str
    summary: Optional[FinalSummaryData] = None
    exchanges: List[Dict[str, Any]] = Field(default_factory=list)

class HistoryItem(BaseModel):
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    difficulty: str
    overall_score: Optional[float] = None
    questions_answered: int = 0
    status: str
    created_at: str

class SystemHealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    ai_configured: bool
    ai_model: str
    environment: str

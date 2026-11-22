from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Path as FastPath
from backend.app.config import settings
from backend.app.models import (
    CandidateSetupRequest,
    SessionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    EndInterviewResponse,
    SessionDetailResponse,
    QuestionData,
    EvaluationResult,
    RubricCriteria,
    FinalSummaryData
)
from backend.app.repositories import repo
from backend.app.prompts import prompt_manager
from backend.app.ai_service import ai_service, AIServiceException

router = APIRouter(prefix="/api/interview", tags=["Mock Interview"])

@router.post("/start", response_model=SessionResponse)
async def start_interview(payload: CandidateSetupRequest):
    # Create session in SQLite
    session_id = repo.create_session(
        candidate_name=payload.candidate_name,
        target_role=payload.target_role,
        experience_level=payload.experience_level.value,
        skills=payload.skills,
        difficulty=payload.difficulty.value,
        job_description=payload.job_description
    )

    # Render prompt for initial question
    prompt_variables = {
        "candidate_name": payload.candidate_name,
        "target_role": payload.target_role,
        "experience_level": payload.experience_level.value,
        "skills": payload.skills,
        "difficulty": payload.difficulty.value,
        "job_description": payload.job_description or "General industry standard for this position",
        "previously_asked_questions": "None (This is the opening question)",
        "question_number": 1
    }
    rendered_prompt = prompt_manager.get_question_generation_prompt(prompt_variables)

    # Generate question
    question_data = await ai_service.generate_question(
        prompt_text=rendered_prompt,
        question_number=1,
        role=payload.target_role,
        level=payload.experience_level.value,
        skills=payload.skills,
        difficulty=payload.difficulty.value
    )

    # Store exchange in SQLite
    repo.add_exchange(
        session_id=session_id,
        question_number=1,
        question_text=question_data.question,
        question_topic=question_data.topic,
        expected_key_points=question_data.expected_key_points
    )

    mode_message = None if ai_service.is_configured else "Running in Simulated Demo Mode (no GEMINI_API_KEY set)."

    return SessionResponse(
        session_id=session_id,
        candidate_name=payload.candidate_name,
        target_role=payload.target_role,
        experience_level=payload.experience_level.value,
        skills=payload.skills,
        difficulty=payload.difficulty.value,
        status="in_progress",
        current_question=question_data,
        is_simulated=not ai_service.is_configured,
        message=mode_message
    )

@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    payload: SubmitAnswerRequest,
    session_id: str = FastPath(..., description="Active session ID")
):
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Interview session has already been completed.")

    # Find the latest pending exchange
    exchanges = repo.get_exchanges(session_id)
    if not exchanges:
        raise HTTPException(status_code=400, detail="No active question found for this session.")

    current_exchange = None
    for ex in reversed(exchanges):
        if ex["answer_text"] is None:
            current_exchange = ex
            break

    if not current_exchange:
        raise HTTPException(status_code=400, detail="All current questions have already been answered.")

    question_text = current_exchange["question_text"]
    q_num = current_exchange["question_number"]

    # Render evaluation prompt
    eval_vars = {
        "target_role": session["target_role"],
        "experience_level": session["experience_level"],
        "skills": session["skills"],
        "difficulty": session["difficulty"],
        "question": question_text,
        "answer": payload.answer
    }
    rendered_eval_prompt = prompt_manager.get_answer_evaluation_prompt(eval_vars)

    # Run evaluation
    evaluation = await ai_service.evaluate_answer(
        prompt_text=rendered_eval_prompt,
        question=question_text,
        answer=payload.answer,
        role=session["target_role"],
        level=session["experience_level"]
    )

    # Generate follow-up or next question
    next_q_num = q_num + 1
    asked_questions = [ex["question_text"] for ex in exchanges]

    follow_up_vars = {
        "target_role": session["target_role"],
        "experience_level": session["experience_level"],
        "skills": session["skills"],
        "difficulty": session["difficulty"],
        "question": question_text,
        "answer": payload.answer,
        "overall_score": evaluation.overall_score,
        "strengths": "\n- ".join(evaluation.strengths),
        "improvements": "\n- ".join(evaluation.improvements),
        "previously_asked_questions": "\n- ".join(asked_questions)
    }
    rendered_followup_prompt = prompt_manager.get_follow_up_prompt(follow_up_vars)

    next_question = await ai_service.generate_follow_up(
        prompt_text=rendered_followup_prompt,
        question_number=next_q_num,
        role=session["target_role"],
        level=session["experience_level"],
        evaluation=evaluation
    )

    # Update current exchange in SQLite with evaluation and answer
    repo.update_exchange_evaluation(
        exchange_id=current_exchange["id"],
        answer_text=payload.answer,
        overall_score=evaluation.overall_score,
        score_technical=evaluation.criteria.technical_accuracy,
        score_clarity=evaluation.criteria.clarity,
        score_relevance=evaluation.criteria.relevance,
        score_completeness=evaluation.criteria.completeness,
        strengths=evaluation.strengths,
        improvements=evaluation.improvements,
        improved_answer=evaluation.improved_answer,
        follow_up_question=next_question.question
    )

    # Create next exchange record
    repo.add_exchange(
        session_id=session_id,
        question_number=next_q_num,
        question_text=next_question.question,
        question_topic=next_question.topic,
        expected_key_points=next_question.expected_key_points
    )

    return SubmitAnswerResponse(
        session_id=session_id,
        question_number=q_num,
        question=question_text,
        answer=payload.answer,
        evaluation=evaluation,
        next_question=next_question,
        is_completed=False
    )

@router.post("/{session_id}/end", response_model=EndInterviewResponse)
async def end_interview(session_id: str = FastPath(..., description="Session ID")):
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    exchanges = repo.get_exchanges(session_id)
    answered_exchanges = [ex for ex in exchanges if ex.get("answer_text") is not None]

    # Build transcript text
    transcript_blocks = []
    for ex in answered_exchanges:
        transcript_blocks.append(
            f"Q{ex['question_number']}: {ex['question_text']}\n"
            f"Answer: {ex['answer_text']}\n"
            f"Score: {ex.get('overall_score', 'N/A')}/10\n"
            f"Strengths: {', '.join(ex.get('strengths', []))}\n"
            f"Improvements: {', '.join(ex.get('improvements', []))}\n"
        )
    transcript_str = "\n---\n".join(transcript_blocks) if transcript_blocks else "No answers submitted."

    # Render summary prompt
    summary_vars = {
        "candidate_name": session["candidate_name"],
        "target_role": session["target_role"],
        "experience_level": session["experience_level"],
        "skills": session["skills"],
        "difficulty": session["difficulty"],
        "interview_transcript": transcript_str
    }
    rendered_summary_prompt = prompt_manager.get_final_summary_prompt(summary_vars)

    summary_data = await ai_service.generate_final_summary(
        prompt_text=rendered_summary_prompt,
        candidate_name=session["candidate_name"],
        role=session["target_role"],
        level=session["experience_level"],
        exchanges_data=answered_exchanges
    )

    # Save summary to SQLite
    repo.save_final_summary(
        session_id=session_id,
        overall_score=summary_data.overall_score,
        average_score=summary_data.average_score,
        questions_answered=summary_data.questions_answered,
        summary_text=summary_data.summary,
        strengths=summary_data.strengths,
        areas_for_improvement=summary_data.areas_for_improvement,
        topics_to_revise=summary_data.topics_to_revise,
        recommendations=summary_data.preparation_recommendations
    )

    # Update session status
    repo.update_session_status(session_id, "completed")

    return EndInterviewResponse(
        session_id=session_id,
        candidate_name=session["candidate_name"],
        target_role=session["target_role"],
        overall_score=summary_data.overall_score,
        average_score=summary_data.average_score,
        questions_answered=summary_data.questions_answered,
        summary=summary_data.summary,
        strengths=summary_data.strengths,
        areas_for_improvement=summary_data.areas_for_improvement,
        topics_to_revise=summary_data.topics_to_revise,
        preparation_recommendations=summary_data.preparation_recommendations,
        history=answered_exchanges,
        is_simulated=summary_data.is_simulated
    )

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_details(session_id: str = FastPath(..., description="Session ID")):
    session = repo.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    exchanges = repo.get_exchanges(session_id)
    summary_raw = repo.get_final_summary(session_id)
    summary_model = None

    if summary_raw:
        summary_model = FinalSummaryData(
            overall_score=summary_raw["overall_score"],
            average_score=summary_raw["average_score"],
            questions_answered=summary_raw["questions_answered"],
            summary=summary_raw["summary_text"],
            strengths=summary_raw["strengths"],
            areas_for_improvement=summary_raw["areas_for_improvement"],
            topics_to_revise=summary_raw["topics_to_revise"],
            preparation_recommendations=summary_raw["preparation_recommendations"],
            is_simulated=not ai_service.is_configured
        )

    return SessionDetailResponse(
        session_id=session["id"],
        candidate_name=session["candidate_name"],
        target_role=session["target_role"],
        experience_level=session["experience_level"],
        skills=session["skills"],
        difficulty=session["difficulty"],
        job_description=session.get("job_description"),
        status=session["status"],
        created_at=str(session["created_at"]),
        summary=summary_model,
        exchanges=exchanges
    )

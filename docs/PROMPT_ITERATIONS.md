# InterviewX — Prompt Iteration Analysis

> **Course:** SCSE4041 Prompt Engineering Mini Project — Milestone 2  
> **Team:** Cognitive Crew  

---

## Iteration Overview

To satisfy the academic requirements of Milestone 2, InterviewX underwent four systematic prompt iterations. Each version was evaluated on structured output reliability, scoring consistency, and adaptive context maintenance.

| Version | Focus | Architecture | Output Format | Key Limitation |
|---|---|---|---|---|
| **v1** | Baseline All-in-One | Monolithic prompt | Free-form prose | Unstructured text, inconsistent scoring, drift |
| **v2** | Rubric Standardization | Separated evaluator | Structured JSON | Lacked multi-turn memory & dynamic branching |
| **v3** | Adaptive Memory | History-aware controller | Structured JSON | Congested multiple tasks into single prompt |
| **Final** | Modular Micro-Prompts | 4 Decoupled Prompts | Strictly typed JSON | Production-ready, validated by Pydantic |

---

## 1. Version 1: Baseline All-in-One Prompt

### Full Prompt Text (`prompts/v1/baseline_interview.txt`)
```text
You are InterviewX, an experienced technical interviewer and professional
interview evaluator.

Conduct a realistic technical mock interview based on the candidate's target
role, experience, skills, difficulty level, and optional job description.

Ask exactly one question at a time. Wait for the candidate's response before
asking another question.

Evaluate each answer using:
1. Technical accuracy.
2. Clarity.
3. Relevance.
4. Completeness.

Give an overall score out of 10. Explain what the candidate did well, what was
missing or incorrect, and how the answer can be improved. Provide a strong
sample answer.

Ask a relevant follow-up question when appropriate. Use the candidate's
previous answers and the interview context to make follow-up questions useful.

Adapt difficulty gradually:
- If the answer is strong, increase difficulty when appropriate.
- If the answer is weak, ask a simpler conceptual follow-up or identify the
  knowledge gap.
- Do not repeat questions in the same interview.
- Stay relevant to the selected role and skills.

Be professional, constructive, and encouraging. Never invent candidate
information. Do not give a high score to an incorrect or irrelevant answer.
If the answer is empty, explain that it cannot be meaningfully evaluated.
```

### Observed Results & Limitations
- **Output Inconsistency:** The model generated conversational paragraphs rather than structured data, making automated frontend rendering and SQLite storage fragile.
- **Score Inflation:** Vague answers regularly received scores of 7–8/10 because the model had no strict dimension penalties.
- **Context Bleed:** Question generation and answer feedback were intertwined, creating confusing user interfaces.

---

## 2. Version 2: Rubric Standardization

### Full Prompt Text (`prompts/v2/rubric_evaluation.txt`)
```text
You are InterviewX Rubric Evaluator, an objective technical assessor.

Your task is to evaluate a candidate's answer to an interview question using a strict 4-dimension rubric.

[Candidate Profile]
- Target Role: {target_role}
- Experience Level: {experience_level}
- Skills: {skills}
- Difficulty: {difficulty}

[Question Asked]
{question}

[Candidate Submitted Answer]
{answer}

[Rubric Dimensions (1 to 10 scale each)]
1. Technical Accuracy (1-10): Factual correctness, proper terminology, correctness of algorithmic/architectural principles.
2. Clarity (1-10): Well-structured communication, articulate reasoning, ease of understanding.
3. Relevance (1-10): Directly answers what was asked without wandering off-topic or deflecting.
4. Completeness (1-10): Covers essential edge cases, trade-offs, and necessary depth for the candidate's level.

[Grading Rules]
- Empty, gibberish, or non-answers must receive an overall score of 0, with a clear note that no evaluation is possible.
- Factually incorrect answers must receive scores <= 3 in Technical Accuracy.
- Do not inflate scores. High scores (8-10) require precision and depth matching the candidate's stated level.
- Be encouraging, professional, and actionable.

[Output Format]
Output ONLY valid JSON matching this exact structure:
{
  "overall_score": <number 0-10>,
  "criteria": {
    "technical_accuracy": <number 0-10>,
    "clarity": <number 0-10>,
    "relevance": <number 0-10>,
    "completeness": <number 0-10>
  },
  "strengths": [
    "<specific positive aspect 1>",
    "<specific positive aspect 2>"
  ],
  "improvements": [
    "<specific deficiency or missing detail 1>",
    "<specific deficiency or missing detail 2>"
  ],
  "improved_answer": "<concise, professional example of an ideal answer tailored to their level>"
}
```

### Changes Made from v1
- Deconstructed evaluation from interview execution.
- Defined numerical boundaries for all 4 rubric dimensions.
- Enforced zero scores for empty/non-evaluable submissions.
- Mandated pure JSON output.

### Observed Results & Limitations
- **Success:** Empty answers consistently received score 0; factually incorrect statements received accurate penalties.
- **Remaining Gap:** Lacked multi-turn conversation memory, dynamic difficulty progression, and final performance synthesis.

---

## 3. Version 3: Adaptive Context Memory

### Full Prompt Text (`prompts/v3/adaptive_context.txt`)
```text
You are InterviewX Adaptive Controller, conducting an interactive interview session.

You are provided with candidate metadata and previous question-and-answer exchanges from the ongoing interview.

[Candidate Profile]
- Candidate Name: {candidate_name}
- Target Role: {target_role}
- Experience Level: {experience_level}
- Skills: {skills}
- Difficulty Level: {difficulty}
- Job Description: {job_description}

[Interview Session History]
{session_history}

[Current Question]
{current_question}

[Candidate's Current Answer]
{current_answer}

[Latest Evaluation]
Overall Score: {overall_score}/10
Strengths: {strengths}
Deficiencies: {improvements}

[Adaptive Instructions]
- If the candidate's answer was strong (score >= 7):
  Ask a more challenging or in-depth follow-up question that explores edge cases, system trade-offs, scalability, or real-world implementation nuances.
- If the candidate's answer was weak or missed foundational concepts (score < 5):
  Pivot to a simpler conceptual follow-up that helps diagnose or bridge the foundational knowledge gap.
- If the answer was moderate (score 5-6):
  Ask for clarification or practical application of the concept they introduced.
- Never repeat any question previously asked in this session.
- Ensure the question directly aligns with {target_role} and {skills}.

[Output Format]
Output ONLY valid JSON matching this schema:
{
  "adaptive_reasoning": "<1-2 sentence justification for why this follow-up is chosen>",
  "follow_up_question": "<the exact interview question to ask the candidate next>"
}
```

### Changes Made from v2
- Injected `{session_history}` to track previously asked questions and eliminate duplicates.
- Added explicit score thresholds ($\ge 7$ escalation, $< 5$ step down) for follow-up questioning.
- Required the model to articulate its adaptation rationale.

### Observed Results & Limitations
- **Success:** Enabled coherent multi-turn interview dialogue where strong candidates were challenged with scaling/latency questions and struggling candidates were redirected to fundamentals.
- **Remaining Gap:** Question generation, rubric assessment, follow-up adaptation, and final session summaries were still coupled across overlapping instructions.

---

## 4. Final Iteration: Specialized Modular Prompts

### Architecture Description
The final production architecture separates prompt execution into four dedicated prompt files located in `prompts/final/`:
1. `question_generation.txt`: Focused solely on opening question calibration using role, level, skills, and target job description.
2. `answer_evaluation.txt`: Strict 4-dimension rubric evaluator returning scores, feedback, and benchmark exemplar answers.
3. `follow_up_generation.txt`: Context-aware follow-up generator with explicit adaptive branching rules.
4. `final_interview_summary.txt`: Executive synthesis prompt producing holistic scores, strengths, improvement areas, topics to revise, and customized preparation plans.

### Observed Results Across Real Test Runs
- 100% adherence to Pydantic validation schemas.
- Zero JSON formatting exceptions across test runs.
- Instant, unambiguous feedback delivered to candidate UI.
- Strict penalty enforcement on off-topic or empty answers.

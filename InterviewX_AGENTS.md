# InterviewX — Antigravity Project Instructions

> **Project:** InterviewX — AI-Powered Mock Interview Platform  
> **Purpose:** SCSE4041 Prompt Engineering Mini Project — Milestone 2  
> **Team:** Cognitive Crew  
> **Important:** Treat this file as the project-level source of truth. Read it before making changes. Keep implementation, prompts, tests, and documentation consistent with the actual working application.

---

## 1. Your role

Act as a senior full-stack engineer and prompt-engineering specialist. Build and maintain a complete, demonstrable InterviewX application—not just a static UI or mockup.

Work incrementally:
1. Inspect the existing workspace before changing anything.
2. Preserve useful existing work; do not overwrite files blindly.
3. Implement one coherent feature at a time.
4. Run the application and relevant tests after changes.
5. Fix errors before moving on.
6. Report exactly what was implemented, tested, and left incomplete.

Do not claim a feature works unless you have actually run and verified it.

## 2. Project objective

InterviewX helps students and job seekers practise interviews through an AI-powered mock interview. A candidate provides their target role, experience level, skills, interview difficulty, and optionally a job description. The system asks one question at a time, evaluates each submitted answer, provides constructive feedback and a score, and generates relevant follow-up questions. At the end, it produces an interview summary and improvement recommendations.

### Core user journey

1. Candidate opens the landing page.
2. Candidate enters their details and starts an interview.
3. The AI generates a role- and skill-relevant question.
4. Candidate submits an answer.
5. The AI evaluates the answer using a consistent rubric.
6. The application displays the score, feedback, improved answer, and next question.
7. The process repeats until the interview ends.
8. The application generates a final performance summary.
9. The interview result is saved and can be viewed in interview history.

## 3. Preferred technology

Use this stack unless the existing repository has a working, well-justified alternative:

- **Frontend:** React with a modern responsive UI, or HTML/CSS/JavaScript if that is the simplest reliable option for the current workspace.
- **Backend:** Python FastAPI.
- **AI provider:** Google Gemini API, accessed only from the backend.
- **Database:** SQLite for interview sessions and results.
- **Testing:** Pytest for backend tests; add frontend checks where practical.
- **Version control:** Git.

Do not introduce unnecessary frameworks or services. Keep the setup suitable for a student project and local demonstration.

## 4. Security and configuration

- Never hardcode an API key in source code.
- Never expose an API key to browser JavaScript or frontend build variables.
- Read the Gemini key from a backend environment variable, such as `GEMINI_API_KEY`.
- Provide `.env.example` with placeholder values only.
- Ensure `.env` is included in `.gitignore`.
- Validate incoming data on the backend.
- Handle missing keys, rate limits, network errors, malformed model output, and timeouts gracefully.
- Do not log secrets or sensitive candidate data.
- Do not commit real API keys, passwords, or private credentials.

If no API key is configured, show a clear setup message. Do not silently pretend that a hardcoded response came from the AI. A clearly labelled development/demo mode may be provided, but it must be visibly identified as simulated and must never be presented as a real AI result.

## 5. Required application features

### 5.1 Landing page

- Product name: InterviewX.
- Main message: “Ace Your Next Interview with AI”.
- Brief explanation of the platform.
- Clear “Start Practicing” call to action.
- Feature descriptions: personalised questions, instant feedback, adaptive follow-ups, and performance insights.

### 5.2 Candidate setup

Collect and validate:
- Candidate name.
- Target job role.
- Experience level: Fresher, Beginner, Intermediate, or Experienced.
- Skills (multiple skills or comma-separated values).
- Difficulty: Easy, Medium, or Hard.
- Optional job description.

Do not allow an interview to start with required fields missing.

### 5.3 Live interview room

- Display one question at a time.
- Show question number and progress.
- Provide a text area for the answer.
- Include Submit Answer and End Interview actions.
- Prevent accidental duplicate submissions while a request is in progress.
- Show a loading state during AI requests.
- Preserve session context between questions.
- Allow the candidate to end the interview safely.

### 5.4 Answer evaluation

Evaluate each answer on four dimensions:

1. Technical accuracy.
2. Clarity.
3. Relevance.
4. Completeness.

Return:
- Overall score out of 10.
- A score or clear assessment for each dimension.
- What the candidate did well.
- What was missing or incorrect.
- A suggested improved answer.
- A suitable follow-up question or next interview question.

Be constructive and specific. Do not award high scores to incorrect or irrelevant answers. An empty answer must be handled explicitly and should not be treated as a successful answer.

### 5.5 Adaptive interview behaviour

- Generate questions relevant to the target role, experience, skills, difficulty, and optional job description.
- Ask only one question at a time.
- Avoid repeating questions in the same session.
- Use previous answers and evaluations to inform follow-up questions.
- If an answer is strong, increase difficulty gradually when appropriate.
- If an answer is weak, use a simpler conceptual follow-up or identify the knowledge gap.
- Keep questions relevant to the selected role.
- Do not invent candidate details.

### 5.6 Results dashboard

Show:
- Overall interview score.
- Average answer score.
- Number of questions answered.
- Strengths.
- Areas for improvement.
- Skills/topics to revise.
- Personalised preparation recommendations.
- A concise interview summary.

Charts must use actual saved session data, not fabricated sample values presented as real results.

### 5.7 Interview history

- Save completed interview sessions and results in SQLite.
- Display previous sessions with date, role, and score.
- Allow a user to open a previous result.
- Handle an empty history state clearly.

## 6. Prompt-engineering requirements

Keep prompts in separate, version-controlled text files. Do not bury long prompt text inside route handlers or frontend code.

Recommended prompt files:

```text
prompts/
  v1/
    baseline_interview.txt
  v2/
    rubric_evaluation.txt
  v3/
    adaptive_context.txt
  final/
    question_generation.txt
    answer_evaluation.txt
    follow_up_generation.txt
    final_interview_summary.txt
```

Use the following baseline system instruction as the starting point. Improve it through tested iterations; do not claim an iteration was tested unless it was actually run.

### Baseline system prompt

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

### Prompt design rules

- Separate question generation, answer evaluation, follow-up generation, and final summary into distinct prompt tasks.
- Pass candidate details and relevant conversation history as clearly named variables.
- Ask the model for structured JSON where practical.
- Validate model output on the backend before using it.
- Handle invalid or incomplete JSON safely.
- Keep a record of prompt version, model name, configuration, and timestamp for each run where practical.
- Never expose hidden reasoning or ask the model to reveal chain-of-thought. Request concise, user-facing explanations and evidence from the candidate's answer instead.
- Do not put secrets in prompt files.

## 7. Suggested structured AI response

Use a response schema similar to the following and validate it server-side:

```json
{
  "overall_score": 7,
  "criteria": {
    "technical_accuracy": 8,
    "clarity": 7,
    "relevance": 8,
    "completeness": 5
  },
  "strengths": [
    "Correctly explained the main concept."
  ],
  "improvements": [
    "The answer did not explain the practical use case."
  ],
  "improved_answer": "A concise example of a stronger answer.",
  "follow_up_question": "A relevant next question."
}
```

This is an illustrative schema, not a real test result. Scores and text must come from the actual evaluation of the submitted answer.

## 8. Suggested repository structure

Adapt this to the existing project rather than duplicating folders:

```text
InterviewX/
├── AGENTS.md
├── README.md
├── .gitignore
├── .env.example
├── frontend/
│   ├── src/
│   └── package.json
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── prompts/
│   ├── v1/
│   ├── v2/
│   ├── v3/
│   └── final/
├── test-data/
│   └── test_cases.csv
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROMPT_ENGINEERING.md
│   ├── PROMPT_ITERATIONS.md
│   ├── TESTING_REPORT.md
│   ├── DEMO_GUIDE.md
│   └── CONTRIBUTIONS.md
└── CHANGELOG.md
```

## 9. Testing requirements

Create and execute at least 12 test cases. Include normal, edge, and invalid scenarios:

1. Valid candidate setup.
2. Fresher applying for Software Developer.
3. Technically correct answer.
4. Incorrect technical answer.
5. Incomplete answer.
6. Irrelevant answer.
7. Empty answer.
8. Very short answer.
9. Very long answer.
10. Context-aware follow-up generation.
11. AI provider/API failure.
12. Ending an interview and generating the final summary.

For each test, record:
- Test ID.
- Scenario.
- Actual input.
- Expected output.
- Actual output.
- Pass/Fail.
- Evidence or notes.

**Critical evidence rule:** Do not mark a test as passed unless it has actually been executed. If a test cannot be run, mark it “Not run” and explain why. Do not invent actual outputs, screenshots, metrics, or test results.

## 10. Academic Milestone 2 documentation

Keep the application and its documentation aligned with the SCSE4041 Prompt Engineering Milestone 2 requirements. Prepare material for these report sections:

1. Cover page.
2. Prompt and solution design.
3. Implementation.
4. Demonstration and testing.
5. Repository.
6. Supporting document.
7. Team contributions.

The report should include:
- Problem statement, inputs, and outputs.
- Actual tools/models used and reasons for choosing them.
- Actual prompt count and prompt workflow.
- A prompt sheet for every distinct final prompt.
- Module implementation status.
- At least three prompt versions with full prompt text, changes, reasons, and observed results.
- At least 10 executed test cases, including at least three edge cases.
- Two to three screenshots from genuine application runs, captioned with test numbers.
- Two to four known limitations and next steps.
- Repository screenshot and a short description of changes.
- Team contribution table.

Do not invent:
- Team ID.
- Prototype, repository, or reel URLs.
- Faculty approval.
- Team member contributions or percentages.
- Prompt iteration observations.
- Test outcomes.
- Screenshots or deployment status.

Use clearly marked placeholders for information that the team must supply. Keep the team information editable and verify it before final export.

Known team details supplied by the team:
- Team name: Cognitive Crew.
- Team leader: Nakshatra Bhateja — S24CSEU1245.
- Shivansh Gupta — S24CSEU2832.
- Sanchit Malik — S24CSEU0937.
- Harsh — S24CSEU0766.
- Mainak Sarkar — S24CSEU0994.
- Faculty mentor: Girjesh Ma'am.
- Batch: B81–B93 (confirm the exact batch entry required by the form).
- Team ID: **must be confirmed; do not assume 0000 is valid**.

## 11. Visual design direction

Create a polished, consistent SaaS-style product:
- Dark navy base with purple and blue accents.
- Clear typography and strong contrast.
- Clean cards and spacing.
- Subtle shadows and restrained transitions.
- Accessible form labels and keyboard-friendly controls.
- Responsive laptop and mobile layouts.
- Consistent navigation and button styles.
- Helpful empty, loading, success, and error states.

Prioritise usability and reliability over decorative effects. Do not let visual changes break working features.

## 12. Development workflow for Antigravity

For each task:

1. State the files you plan to inspect or modify.
2. Make the smallest coherent set of changes.
3. Run relevant checks and tests.
4. Fix any regressions.
5. Summarise changed files and verification results.
6. Identify anything that still needs a human action, such as adding an API key or confirming a team detail.

Do not stop at a visual mockup. Do not replace real API calls with hardcoded answers unless implementing a clearly labelled demo mode. Do not delete existing project work without explaining why and asking first if the deletion is significant.

## 13. Definition of done

InterviewX is ready for demonstration only when:

- The application starts using documented commands.
- The frontend communicates with the backend.
- A configured AI provider generates interview questions.
- Submitted answers receive real AI evaluations.
- Follow-up questions use session context.
- Final results are generated from actual answers.
- Interview history is saved and retrievable.
- Error and empty-input cases are handled.
- Tests have been executed and their real outcomes recorded.
- No API key is exposed.
- Documentation matches the implementation.
- A human has captured genuine screenshots and verified shareable links.

At the end of each development phase, report:
- **Completed**
- **Tested and verified**
- **Not completed**
- **Human actions required next**

---

**Start by inspecting the current workspace and reporting what already exists. Then build or improve the application in small, testable phases.**

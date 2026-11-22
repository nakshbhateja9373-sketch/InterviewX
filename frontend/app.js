// InterviewX — Single Page Application Controller
const app = {
  state: {
    currentView: "landing",
    sessionId: null,
    candidate: null,
    currentQuestion: null,
    nextQuestion: null,
    isSubmitting: false,
    history: []
  },

  init() {
    this.checkHealth();
    this.showView("landing");
  },

  // =========================================================================
  // Health & System Status
  // =========================================================================
  async checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();
      
      const badge = document.getElementById("ai-status-badge");
      const text = document.getElementById("ai-status-text");

      if (data.ai_configured) {
        badge.className = "flex items-center space-x-2 text-xs font-semibold px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-700/60 text-emerald-300";
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400"></span><span>Gemini Live (${data.ai_model})</span>`;
      } else {
        badge.className = "flex items-center space-x-2 text-xs font-semibold px-3 py-1 rounded-full bg-amber-950/80 border border-amber-700/60 text-amber-300";
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span><span>Simulated Demo Mode</span>`;
      }
    } catch (err) {
      console.warn("Could not check health:", err);
      const text = document.getElementById("ai-status-text");
      if (text) text.innerText = "Offline Mode";
    }
  },

  // =========================================================================
  // Navigation & View Routing
  // =========================================================================
  showView(viewName) {
    this.state.currentView = viewName;
    const views = ["landing", "setup", "room", "dashboard", "history"];
    views.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      if (el) {
        if (v === viewName) {
          el.classList.remove("hidden");
          el.classList.add("animate-fade-in");
        } else {
          el.classList.add("hidden");
          el.classList.remove("animate-fade-in");
        }
      }
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  showAlert(message, type = "info") {
    const alertBox = document.getElementById("global-alert");
    const alertMsg = document.getElementById("global-alert-msg");
    const alertIcon = document.getElementById("global-alert-icon");
    
    if (!alertBox || !alertMsg) return;

    alertMsg.innerText = message;
    if (type === "error") {
      alertBox.className = "mb-6 p-4 rounded-xl border text-sm flex items-start gap-3 bg-rose-950/40 border-rose-800 text-rose-200 animate-fade-in";
      alertIcon.innerHTML = `<svg class="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
    } else {
      alertBox.className = "mb-6 p-4 rounded-xl border text-sm flex items-start gap-3 bg-indigo-950/40 border-indigo-800 text-indigo-200 animate-fade-in";
      alertIcon.innerHTML = `<svg class="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;
    }
    alertBox.classList.remove("hidden");
  },

  hideAlert() {
    const alertBox = document.getElementById("global-alert");
    if (alertBox) alertBox.classList.add("hidden");
  },

  appendSkill(skills) {
    const input = document.getElementById("setup-skills");
    if (!input) return;
    if (!input.value) {
      input.value = skills;
    } else {
      input.value = `${input.value}, ${skills}`;
    }
  },

  // =========================================================================
  // Candidate Setup & Interview Start
  // =========================================================================
  async handleStartInterview(event) {
    event.preventDefault();
    this.hideAlert();

    const name = document.getElementById("setup-name").value.trim();
    const role = document.getElementById("setup-role").value.trim();
    const level = document.getElementById("setup-level").value;
    const difficulty = document.getElementById("setup-difficulty").value;
    const skills = document.getElementById("setup-skills").value.trim();
    const jd = document.getElementById("setup-jd").value.trim();

    if (!name || !role || !skills) {
      this.showAlert("Please fill out all required fields before starting.", "error");
      return;
    }

    const btn = document.getElementById("setup-submit-btn");
    const btnText = document.getElementById("setup-btn-text");
    const spinner = document.getElementById("setup-btn-spinner");

    btn.disabled = true;
    btnText.innerText = "Calibrating AI...";
    spinner.classList.remove("hidden");

    try {
      const response = await fetch("/api/interview/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_name: name,
          target_role: role,
          experience_level: level,
          difficulty: difficulty,
          skills: skills,
          job_description: jd || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start interview session.");
      }

      const session = await response.json();
      this.state.sessionId = session.session_id;
      this.state.candidate = { name, role, level, difficulty, skills };
      this.state.currentQuestion = session.current_question;
      this.state.nextQuestion = null;

      // Populate Live Room UI
      document.getElementById("room-candidate-name").innerText = session.candidate_name;
      document.getElementById("room-role-title").innerText = session.target_role;
      document.getElementById("room-level-badge").innerText = session.experience_level;
      document.getElementById("room-difficulty-badge").innerText = session.difficulty;

      this.renderCurrentQuestion();
      this.showView("room");

      if (session.message) {
        this.showAlert(session.message, "info");
      }
    } catch (err) {
      console.error(err);
      this.showAlert(err.message, "error");
    } finally {
      btn.disabled = false;
      btnText.innerText = "Begin Interview";
      spinner.classList.add("hidden");
    }
  },

  // =========================================================================
  // Live Interview Room Interaction
  // =========================================================================
  renderCurrentQuestion() {
    const q = this.state.currentQuestion;
    if (!q) return;

    document.getElementById("room-q-badge").innerText = `Q${q.question_number}`;
    document.getElementById("room-question-topic").innerText = q.topic || "Core Technical Competency";
    document.getElementById("room-question-text").innerText = q.question;

    const keyPointsWrap = document.getElementById("room-key-points-wrap");
    const keyPointsContainer = document.getElementById("room-key-points");
    
    if (q.expected_key_points && q.expected_key_points.length > 0) {
      keyPointsContainer.innerHTML = q.expected_key_points
        .map(pt => `<span class="text-xs px-2.5 py-1 rounded-md bg-navy-800 text-purple-300 border border-purple-800/40">${pt}</span>`)
        .join("");
      keyPointsWrap.classList.remove("hidden");
    } else {
      keyPointsWrap.classList.add("hidden");
    }

    // Reset answer textarea
    const answerInput = document.getElementById("room-answer-input");
    answerInput.value = "";
    this.updateAnswerCounts();

    // Hide previous evaluation card and re-enable form wrap
    document.getElementById("evaluation-card").classList.add("hidden");
    document.getElementById("answer-form-wrap").classList.remove("hidden");
    answerInput.focus();
  },

  updateAnswerCounts() {
    const input = document.getElementById("room-answer-input");
    const countEl = document.getElementById("answer-word-count");
    if (!input || !countEl) return;

    const val = input.value.trim();
    const words = val ? val.split(/\s+/).length : 0;
    const chars = input.value.length;
    countEl.innerText = `${words} words | ${chars} chars`;
  },

  async handleSubmitAnswer() {
    if (this.state.isSubmitting) return;

    const answerInput = document.getElementById("room-answer-input");
    const answer = answerInput.value;

    if (!answer.trim()) {
      if (!confirm("Your answer is currently empty. An empty answer will receive a score of 0. Are you sure you want to submit?")) {
        return;
      }
    }

    const submitBtn = document.getElementById("submit-answer-btn");
    const submitText = document.getElementById("submit-btn-text");
    const spinner = document.getElementById("submit-btn-spinner");

    this.state.isSubmitting = true;
    submitBtn.disabled = true;
    submitText.innerText = "Evaluating Answer...";
    spinner.classList.remove("hidden");

    try {
      const response = await fetch(`/api/interview/${this.state.sessionId}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer: answer })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to evaluate answer.");
      }

      const result = await response.json();
      this.state.nextQuestion = result.next_question;

      // Render Rubric Evaluation Card
      this.renderEvaluation(result.evaluation);
    } catch (err) {
      console.error(err);
      this.showAlert(err.message, "error");
    } finally {
      this.state.isSubmitting = false;
      submitBtn.disabled = false;
      submitText.innerText = "Submit Answer";
      spinner.classList.add("hidden");
    }
  },

  renderEvaluation(evaluation) {
    const evalCard = document.getElementById("evaluation-card");
    const scoreVal = evaluation.overall_score;

    document.getElementById("eval-overall-score").innerHTML = `${scoreVal}<span class="text-base text-slate-500">/10</span>`;

    // Score Tier Badge
    const badge = document.getElementById("eval-score-badge");
    if (scoreVal >= 7.5) {
      badge.className = "px-3 py-1.5 rounded-xl text-xs font-bold uppercase bg-emerald-950 text-emerald-400 border border-emerald-800";
      badge.innerText = "Strong";
    } else if (scoreVal >= 5.0) {
      badge.className = "px-3 py-1.5 rounded-xl text-xs font-bold uppercase bg-amber-950 text-amber-400 border border-amber-800";
      badge.innerText = "Needs Refinement";
    } else {
      badge.className = "px-3 py-1.5 rounded-xl text-xs font-bold uppercase bg-rose-950 text-rose-400 border border-rose-800";
      badge.innerText = "Significant Gaps";
    }

    // 4 Dimensions
    const crit = evaluation.criteria;
    document.getElementById("score-val-tech").innerText = `${crit.technical_accuracy}/10`;
    document.getElementById("bar-val-tech").style.width = `${crit.technical_accuracy * 10}%`;

    document.getElementById("score-val-clarity").innerText = `${crit.clarity}/10`;
    document.getElementById("bar-val-clarity").style.width = `${crit.clarity * 10}%`;

    document.getElementById("score-val-relevance").innerText = `${crit.relevance}/10`;
    document.getElementById("bar-val-relevance").style.width = `${crit.relevance * 10}%`;

    document.getElementById("score-val-completeness").innerText = `${crit.completeness}/10`;
    document.getElementById("bar-val-completeness").style.width = `${crit.completeness * 10}%`;

    // Strengths
    const strengthsList = document.getElementById("eval-strengths-list");
    strengthsList.innerHTML = evaluation.strengths.map(s => `<li>${s}</li>`).join("");

    // Improvements
    const improvementsList = document.getElementById("eval-improvements-list");
    improvementsList.innerHTML = evaluation.improvements.map(i => `<li>${i}</li>`).join("");

    // Improved Answer
    document.getElementById("eval-improved-answer").innerText = evaluation.improved_answer;

    // Show evaluation card and scroll smoothly into view
    evalCard.classList.remove("hidden");
    evalCard.scrollIntoView({ behavior: "smooth", block: "start" });
  },

  advanceToNextQuestion() {
    if (this.state.nextQuestion) {
      this.state.currentQuestion = this.state.nextQuestion;
      this.state.nextQuestion = null;
      this.renderCurrentQuestion();
    } else {
      this.executeEndInterview();
    }
  },

  // =========================================================================
  // End Interview & Final Summary Generation
  // =========================================================================
  confirmEndInterview() {
    const modal = document.getElementById("confirm-modal");
    if (modal) modal.classList.remove("hidden");
  },

  closeModal() {
    const modal = document.getElementById("confirm-modal");
    if (modal) modal.classList.add("hidden");
  },

  async executeEndInterview() {
    this.closeModal();
    if (!this.state.sessionId) return;

    this.showAlert("Compiling session transcript and generating comprehensive performance synthesis...", "info");

    try {
      const response = await fetch(`/api/interview/${this.state.sessionId}/end`, {
        method: "POST"
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to conclude interview session.");
      }

      const summary = await response.json();
      this.renderDashboard(summary);
      this.hideAlert();
      this.showView("dashboard");
    } catch (err) {
      console.error(err);
      this.showAlert(err.message, "error");
    }
  },

  renderDashboard(data) {
    document.getElementById("dash-candidate-name").innerText = data.candidate_name;
    document.getElementById("dash-target-role").innerText = data.target_role;
    document.getElementById("dash-session-date").innerText = new Date().toLocaleDateString();

    document.getElementById("dash-overall-score").innerText = data.overall_score;
    document.getElementById("dash-average-score").innerText = data.average_score;
    document.getElementById("dash-q-count").innerText = data.questions_answered;

    // Readiness tier
    const label = document.getElementById("dash-readiness-label");
    if (data.overall_score >= 8.0) {
      label.className = "mt-2 inline-block text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/50";
      label.innerText = "Interview Ready (High Confidence)";
    } else if (data.overall_score >= 6.0) {
      label.className = "mt-2 inline-block text-xs font-semibold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/50";
      label.innerText = "Moderate Readiness (Targeted Practice Needed)";
    } else {
      label.className = "mt-2 inline-block text-xs font-semibold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/50";
      label.innerText = "Foundational Revision Required";
    }

    const modeLabel = document.getElementById("dash-mode-label");
    if (data.is_simulated) {
      modeLabel.innerText = "Simulated Demo Mode";
      modeLabel.className = "text-base font-bold text-amber-400";
    } else {
      modeLabel.innerText = "Google Gemini Live AI";
      modeLabel.className = "text-base font-bold text-purple-300";
    }

    document.getElementById("dash-summary-text").innerText = data.summary;

    // Strengths
    document.getElementById("dash-strengths").innerHTML = data.strengths
      .map(s => `<li>${s}</li>`)
      .join("");

    // Areas for improvement
    document.getElementById("dash-improvements").innerHTML = data.areas_for_improvement
      .map(i => `<li>${i}</li>`)
      .join("");

    // Topics to revise
    document.getElementById("dash-topics").innerHTML = data.topics_to_revise
      .map(t => `<span class="text-xs px-3 py-1 rounded-lg bg-purple-950/80 text-purple-300 border border-purple-800/60 font-semibold">${t}</span>`)
      .join("");

    // Recommendations
    document.getElementById("dash-recommendations").innerHTML = data.preparation_recommendations
      .map(r => `<li>${r}</li>`)
      .join("");

    // Full Transcript Accordion
    const container = document.getElementById("dash-transcript-accordion");
    if (data.history && data.history.length > 0) {
      container.innerHTML = data.history.map((ex, idx) => `
        <div class="border border-navy-800 rounded-xl overflow-hidden bg-navy-950/60">
          <div class="p-4 bg-navy-900/60 flex items-center justify-between border-b border-navy-800/50">
            <span class="font-bold text-white text-sm">Question ${ex.question_number}: ${ex.question_topic || "Technical Evaluation"}</span>
            <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/50">${ex.overall_score || 0}/10</span>
          </div>
          <div class="p-4 space-y-3 text-sm">
            <div>
              <span class="text-xs text-slate-400 block font-semibold">Question:</span>
              <p class="text-slate-200 mt-0.5">${ex.question_text}</p>
            </div>
            <div>
              <span class="text-xs text-slate-400 block font-semibold">Candidate Answer:</span>
              <p class="text-slate-300 mt-0.5 font-mono bg-navy-900/40 p-2.5 rounded border border-navy-800/60">${ex.answer_text || "No answer submitted."}</p>
            </div>
            ${ex.improved_answer ? `
            <div>
              <span class="text-xs text-indigo-400 block font-semibold">Exemplar Answer:</span>
              <p class="text-slate-300 mt-0.5 font-mono bg-navy-900/80 p-2.5 rounded border border-indigo-900/40">${ex.improved_answer}</p>
            </div>` : ""}
          </div>
        </div>
      `).join("");
    } else {
      container.innerHTML = `<p class="text-xs text-slate-500">No questions answered in this session.</p>`;
    }
  },

  // =========================================================================
  // History Explorer
  // =========================================================================
  async openHistory() {
    this.showView("history");
    const loading = document.getElementById("history-loading");
    const empty = document.getElementById("history-empty");
    const tableWrap = document.getElementById("history-table-wrap");
    const tbody = document.getElementById("history-table-body");

    loading.classList.remove("hidden");
    empty.classList.add("hidden");
    tableWrap.classList.add("hidden");

    try {
      const response = await fetch("/api/history");
      if (!response.ok) throw new Error("Failed to load interview history.");
      const items = await response.json();
      this.state.history = items;

      loading.classList.add("hidden");

      if (items.length === 0) {
        empty.classList.remove("hidden");
      } else {
        tbody.innerHTML = items.map(item => `
          <tr class="hover:bg-navy-900/50 transition">
            <td class="px-4 py-3 font-semibold text-white">${item.candidate_name}</td>
            <td class="px-4 py-3 text-purple-300">${item.target_role} <span class="text-xs text-slate-400">(${item.experience_level})</span></td>
            <td class="px-4 py-3 text-slate-300">${item.difficulty}</td>
            <td class="px-4 py-3 text-slate-300 font-mono">${item.questions_answered}</td>
            <td class="px-4 py-3">
              ${item.overall_score !== null ? `
                <span class="font-bold text-white font-mono">${item.overall_score}/10</span>
              ` : `
                <span class="text-xs text-slate-500">In Progress</span>
              `}
            </td>
            <td class="px-4 py-3 text-slate-400 text-xs">${new Date(item.created_at).toLocaleDateString()}</td>
            <td class="px-4 py-3 text-right">
              <button onclick="app.loadHistoricalSession('${item.session_id}')" class="px-3 py-1 rounded-lg text-xs font-semibold text-purple-300 bg-purple-950/60 hover:bg-purple-900/60 border border-purple-800/40 transition">
                View Report
              </button>
            </td>
          </tr>
        `).join("");
        tableWrap.classList.remove("hidden");
      }
    } catch (err) {
      console.error(err);
      loading.classList.add("hidden");
      this.showAlert(err.message, "error");
    }
  },

  async loadHistoricalSession(sessionId) {
    this.showAlert("Retrieving complete session report from database...", "info");
    try {
      const response = await fetch(`/api/interview/${sessionId}`);
      if (!response.ok) throw new Error("Failed to fetch historical session details.");
      const detail = await response.json();

      if (detail.summary) {
        const dashboardPayload = {
          session_id: detail.session_id,
          candidate_name: detail.candidate_name,
          target_role: detail.target_role,
          overall_score: detail.summary.overall_score,
          average_score: detail.summary.average_score,
          questions_answered: detail.summary.questions_answered,
          summary: detail.summary.summary,
          strengths: detail.summary.strengths,
          areas_for_improvement: detail.summary.areas_for_improvement,
          topics_to_revise: detail.summary.topics_to_revise,
          preparation_recommendations: detail.summary.preparation_recommendations,
          history: detail.exchanges,
          is_simulated: detail.summary.is_simulated
        };
        this.renderDashboard(dashboardPayload);
        this.hideAlert();
        this.showView("dashboard");
      } else {
        this.showAlert("This session was not formally concluded with a final summary.", "info");
      }
    } catch (err) {
      console.error(err);
      this.showAlert(err.message, "error");
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  app.init();
});

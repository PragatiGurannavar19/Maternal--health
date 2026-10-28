/**
 * NurturaGyno Maternal Health Educational Chatbot
 * Client-side Controller & UI Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const chatFeed = document.getElementById("chat-feed");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const quickChipsContainer = document.getElementById("quick-chips-container");
  const btnTopicDrawer = document.getElementById("btn-topic-drawer");
  const btnCloseDrawer = document.getElementById("btn-close-drawer");
  const drawerOverlay = document.getElementById("topic-drawer-overlay");
  const drawerSearchInput = document.getElementById("drawer-search-input");
  const drawerTopicsList = document.getElementById("drawer-topics-list");
  const btnPrintNotes = document.getElementById("btn-print-notes");
  const btnResetChat = document.getElementById("btn-reset-chat");

  let allTopics = [];

  // Default quick prompt chips
  const defaultChips = [
    { label: "🗓️ 8-Contact ANC Schedule", query: "What is the recommended WHO 8 contact schedule?" },
    { label: "🥗 Maternal Nutrition", query: "What should I eat during pregnancy according to WHO?" },
    { label: "🩸 Iron & Folic Acid", query: "What is the daily dose of iron and folic acid?" },
    { label: "🥛 Calcium Intake", query: "How much calcium is recommended and how should I take it?" },
    { label: "🔬 Routine Lab Tests", query: "What routine blood and urine tests are recommended?" },
    { label: "👶 Ultrasound Timing", query: "When is the recommended ultrasound scan?" },
    { label: "🧘‍♀️ Safe Physical Activity", query: "What kinds of exercise are safe during pregnancy?" },
    { label: "💉 Tetanus Vaccine", query: "Why is the tetanus vaccine recommended and how many doses?" },
    { label: "🌿 Symptoms Relief", query: "How can I relieve common pregnancy symptoms like nausea and heartburn?" },
    { label: "📋 Birth Preparedness", query: "What is birth preparedness and complication readiness?" },
    { label: "🤱 Postnatal Care", query: "What care is recommended after giving birth?" },
    { label: "🩺 Questions for Doctor", query: "What questions should I ask my gynecologist at appointments?" },
    { label: "🚨 Warning Signs", query: "What are the danger signs in pregnancy?" }
  ];

  // Render quick chips
  function renderQuickChips() {
    quickChipsContainer.innerHTML = "";
    defaultChips.forEach(chip => {
      const btn = document.createElement("button");
      btn.className = "topic-chip" + (chip.label.includes("Warning") ? " alert-chip" : "");
      btn.textContent = chip.label;
      btn.addEventListener("click", () => {
        sendUserMessage(chip.query);
      });
      quickChipsContainer.appendChild(btn);
    });
  }

  // Fetch topics list from backend
  async function loadTopics() {
    try {
      const res = await fetch("/api/topics");
      if (res.ok) {
        const data = await res.json();
        allTopics = data.topics || [];
        renderDrawerTopics(allTopics);
      }
    } catch (err) {
      console.warn("Could not fetch topic list from API:", err);
    }
  }

  // Render topic drawer items
  function renderDrawerTopics(topics) {
    drawerTopicsList.innerHTML = "";
    if (topics.length === 0) {
      drawerTopicsList.innerHTML = "<p style='color:#64748b; font-size:0.85rem;'>No matching topics found.</p>";
      return;
    }

    topics.forEach(t => {
      const card = document.createElement("div");
      card.className = "drawer-topic-card";
      card.innerHTML = `
        <div class="drawer-topic-title">${t.topic}</div>
        <div class="drawer-topic-category">${t.category}</div>
      `;
      card.addEventListener("click", () => {
        closeDrawer();
        sendUserMessage(`Tell me about ${t.topic}`);
      });
      drawerTopicsList.appendChild(card);
    });
  }

  // Filter drawer topics
  drawerSearchInput.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase().trim();
    const filtered = allTopics.filter(t => 
      t.topic.toLowerCase().includes(term) || 
      t.category.toLowerCase().includes(term)
    );
    renderDrawerTopics(filtered);
  });

  // Drawer Open/Close
  btnTopicDrawer.addEventListener("click", () => {
    drawerOverlay.classList.remove("hidden");
    drawerSearchInput.focus();
  });

  btnCloseDrawer.addEventListener("click", closeDrawer);
  drawerOverlay.addEventListener("click", (e) => {
    if (e.target === drawerOverlay) closeDrawer();
  });

  function closeDrawer() {
    drawerOverlay.classList.add("hidden");
  }

  // Auto-resize textarea
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Handle Form Submit
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendUserMessage(query);
  });

  // Send message
  async function sendUserMessage(query) {
    appendUserBubble(query);
    const typingId = appendTypingIndicator();
    scrollToBottom();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonSafeStringify({ query })
      });

      removeTypingIndicator(typingId);

      if (!res.ok) {
        appendSystemError("An error occurred connecting to the NurturaGyno service. Please try again.");
        return;
      }

      const data = await res.json();
      renderBotResponse(data);
    } catch (err) {
      removeTypingIndicator(typingId);
      appendSystemError("Network error: Unable to reach the NurturaGyno server.");
    }

    scrollToBottom();
  }

  function jsonSafeStringify(obj) {
    return JSON.stringify(obj);
  }

  // Append user bubble
  function appendUserBubble(text) {
    const row = document.createElement("div");
    row.className = "chat-message-row user";
    const bubble = document.createElement("div");
    bubble.className = "user-bubble";
    bubble.textContent = text;
    row.appendChild(bubble);
    chatFeed.appendChild(row);
  }

  // Typing indicator
  function appendTypingIndicator() {
    const id = "typing-" + Date.now();
    const row = document.createElement("div");
    row.className = "chat-message-row assistant";
    row.id = id;
    row.innerHTML = `
      <div class="assistant-card" style="padding: 0.6rem 1rem;">
        <div class="typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </div>
      </div>
    `;
    chatFeed.appendChild(row);
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // Render Bot Response Cards
  function renderBotResponse(data) {
    const row = document.createElement("div");
    row.className = "chat-message-row assistant";

    const card = document.createElement("div");
    card.className = "assistant-card";

    // Emergency Red Flag Response
    if (data.status === "SAFETY_FALLBACK_EMERGENCY") {
      card.classList.add("emergency-card");
      card.innerHTML = `
        <div class="card-header-line">
          <div class="card-topic-title" style="color: var(--crimson-alert);">${data.title}</div>
          <span class="card-category-pill" style="background-color: #fee2e2; color: var(--crimson-alert); border-color: var(--crimson-border);">CRITICAL EMERGENCY</span>
        </div>
        <div class="card-summary-text" style="font-weight: 500; color: #7f1d1d;">
          ${data.message}
        </div>
        <div class="emergency-steps-box">
          <h4>Required Immediate Actions:</h4>
          <ol class="emergency-steps-list">
            ${data.action_steps.map(step => `<li>${step}</li>`).join("")}
          </ol>
        </div>
        <div class="source-citation-badge">
          <span><strong>Exact WHO Reference:</strong> ${data.exact_source_reference.document}</span>
          <span><strong>Recommendation / Chapter:</strong> ${data.exact_source_reference.recommendation_code} (${data.exact_source_reference.page_reference})</span>
        </div>
        <div class="card-safety-note" style="color: #991b1b;">
          ${data.clinical_guardrail}
        </div>
      `;
      row.appendChild(card);
      chatFeed.appendChild(row);
      return;
    }

    // Diagnostic or Risk Score Blocker Notice
    if (data.status === "SAFETY_FALLBACK_GUARDRAIL") {
      card.classList.add("guardrail-card");
      card.innerHTML = `
        <div class="card-header-line">
          <div class="card-topic-title" style="color: var(--amber-warning);">${data.title}</div>
          <span class="card-category-pill" style="background-color: #fef3c7; color: #92400e; border-color: #fcd34d;">CLINICAL SAFETY</span>
        </div>
        <div class="card-summary-text">
          ${data.message}
        </div>
        <div class="card-safety-note">
          ${data.clinical_guardrail}
        </div>
        <div class="card-followups">
          <span style="font-size:0.75rem; font-weight:600; color:var(--text-muted); align-self:center;">Explore topics:</span>
          ${(data.suggested_topics || []).map(t => `<button class="followup-chip" data-query="Tell me about ${t.label}">${t.label}</button>`).join("")}
        </div>
      `;
      bindFollowupChips(card);
      row.appendChild(card);
      chatFeed.appendChild(row);
      return;
    }

    // Greeting Response
    if (data.status === "GREETING") {
      card.innerHTML = `
        <div class="card-header-line">
          <div class="card-topic-title" style="color: var(--primary-rose);">${data.title}</div>
          <span class="card-category-pill">EVIDENCE-BASED</span>
        </div>
        <div class="card-summary-text">
          ${data.message}
        </div>
        <div class="card-safety-note">
          ${data.clinical_guardrail}
        </div>
        <div class="card-followups">
          <span style="font-size:0.75rem; font-weight:600; color:var(--text-muted); align-self:center;">Quick Start:</span>
          ${(data.suggested_topics || []).map(t => `<button class="followup-chip" data-query="Tell me about ${t.label}">${t.label}</button>`).join("")}
        </div>
      `;
      bindFollowupChips(card);
      row.appendChild(card);
      chatFeed.appendChild(row);
      return;
    }

    // Menu Help Response
    if (data.status === "MENU_HELP") {
      const topicsListHtml = (data.topics_list || []).map(t => 
        `<button class="followup-chip" data-query="Tell me about ${t.topic}" style="margin: 2px;">${t.topic}</button>`
      ).join("");

      card.innerHTML = `
        <div class="card-header-line">
          <div class="card-topic-title">${data.title}</div>
          <span class="card-category-pill">TOPIC DIRECTORY</span>
        </div>
        <div class="card-summary-text">${data.message}</div>
        <div style="display:flex; flex-wrap:wrap; gap:0.4rem; margin: 0.5rem 0;">
          ${topicsListHtml}
        </div>
        <div class="card-safety-note">${data.clinical_guardrail}</div>
      `;
      bindFollowupChips(card);
      row.appendChild(card);
      chatFeed.appendChild(row);
      return;
    }

    // Ambiguous Fallback Response
    if (data.status === "FALLBACK_AMBIGUOUS") {
      card.innerHTML = `
        <div class="card-header-line">
          <div class="card-topic-title">${data.title}</div>
          <span class="card-category-pill">GUIDANCE</span>
        </div>
        <div class="card-summary-text">${data.message}</div>
        <p style="font-size:0.85rem; font-weight:600; color:var(--sage-green);">${data.clarification_prompt}</p>
        <div class="card-followups">
          ${(data.suggested_topics || []).map(t => `<button class="followup-chip" data-query="Tell me about ${t.label}">${t.label}</button>`).join("")}
        </div>
        <div class="card-safety-note">${data.clinical_safety_notice}</div>
      `;
      bindFollowupChips(card);
      row.appendChild(card);
      chatFeed.appendChild(row);
      return;
    }

    // Standard Educational Topic Match (SUCCESS)
    const takeawaysHtml = (data.key_educational_takeaways || []).length > 0 ? `
      <div class="takeaways-section">
        <div class="takeaways-heading"><span>📌</span> WHO Key Takeaways & Practical Guidance:</div>
        <ul class="takeaways-list">
          ${data.key_educational_takeaways.map(point => `<li>${point}</li>`).join("")}
        </ul>
      </div>
    ` : "";

    const doctorQuestionsHtml = (data.questions_to_ask_doctor || []).length > 0 ? `
      <div class="doctor-questions-box">
        <div class="doctor-questions-heading"><span>🩺</span> Questions to Ask Your Obstetrician / Gynecologist:</div>
        <ul class="doctor-questions-list">
          ${data.questions_to_ask_doctor.map(q => `<li>${q}</li>`).join("")}
        </ul>
      </div>
    ` : "";

    const source = data.exact_source_reference || {};
    const sourceHtml = `
      <div class="source-citation-badge">
        <span><strong>Exact Source:</strong> ${source.document || "WHO Guidelines (2016)"}</span>
        <span><strong>Recommendation Code:</strong> ${source.recommendation_code || "N/A"}</span>
        <span><strong>Page & Chapter Reference:</strong> ${source.page_reference || ""} (${source.chapter_or_table || ""})</span>
      </div>
    `;

    const followupsHtml = (data.suggested_followups || []).length > 0 ? `
      <div class="card-followups">
        <span style="font-size:0.75rem; font-weight:600; color:var(--text-muted); align-self:center;">Related:</span>
        ${data.suggested_followups.map(f => `<button class="followup-chip" data-query="Tell me about ${f.label}">${f.label}</button>`).join("")}
      </div>
    ` : "";

    card.innerHTML = `
      <div class="card-header-line">
        <div class="card-topic-title">${data.topic}</div>
        <span class="card-category-pill">${data.category || "WHO Antenatal Care"}</span>
      </div>
      <div class="card-summary-text">
        ${data.concise_educational_response}
      </div>
      ${takeawaysHtml}
      ${doctorQuestionsHtml}
      ${sourceHtml}
      <div class="card-safety-note">
        ${data.clinical_safety_notice}
      </div>
      ${followupsHtml}
    `;

    bindFollowupChips(card);
    row.appendChild(card);
    chatFeed.appendChild(row);
  }

  function bindFollowupChips(cardElement) {
    const chips = cardElement.querySelectorAll(".followup-chip");
    chips.forEach(chip => {
      chip.addEventListener("click", () => {
        const query = chip.getAttribute("data-query");
        if (query) sendUserMessage(query);
      });
    });
  }

  function appendSystemError(msg) {
    const row = document.createElement("div");
    row.className = "chat-message-row assistant";
    row.innerHTML = `
      <div class="assistant-card" style="border-color: #cbd5e1; background-color: #f8fafc;">
        <div style="color: #64748b; font-size: 0.85rem;">${msg}</div>
      </div>
    `;
    chatFeed.appendChild(row);
  }

  function scrollToBottom() {
    chatFeed.scrollTop = chatFeed.scrollHeight;
  }

  // Print Notes
  btnPrintNotes.addEventListener("click", () => {
    window.print();
  });

  // Reset Chat
  btnResetChat.addEventListener("click", () => {
    chatFeed.innerHTML = "";
    sendUserMessage("hello");
  });

  // Initialize
  renderQuickChips();
  loadTopics();
  // Automatically show welcome message
  sendUserMessage("hello");
});

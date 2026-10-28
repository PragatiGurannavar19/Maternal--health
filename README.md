# 🌸 NavyaCare / NurturaGyno - Maternal Health Educational Chatbot

**NavyaCare** is a maternal health education platform featuring a strictly rule-based, non-diagnostic educational chatbot for pregnancy guidance, antenatal care schedules, nutrition, and health awareness. Grounded directly in official **World Health Organization (WHO)** Antenatal Care (ANC) guidelines, it provides transparent, verifiable maternal health information while strictly preventing diagnostic claims, clinical decision support, risk score calculations, or autonomous medical advice.

---

## 🏛️ Grounding & Evidence Base

All clinical content in `knowledge_base/maternal_health.json` is extracted strictly from the following official WHO publications:
1. **World Health Organization (2016)**: *WHO recommendations on antenatal care for a positive pregnancy experience*. Geneva: World Health Organization. ISBN: 978 92 4 154991 2.
2. **USAID / MCSP / WHO (2018)**: *WHO Recommendations on Antenatal Care for a Positive Pregnancy Experience: Summary*. WHO/RHR/18.02.

Every knowledge base entry cites the exact recommendation code and page numbers from these source documents.

---

## 🛡️ Clinical Safety & Guardrails Architecture

The chatbot enforces a multi-tier clinical safety hierarchy before generating any response:

```
                          User Query
                              │
                              ▼
            ┌───────────────────────────────────┐
            │   Tier 0: Safety & Clinical Gate  │
            └─────────────────┬─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     [Emergency Red Flag]            [Diagnostic / Risk / Rx Blocker]
              │                               │
              ▼                               ▼
    ⚠️ EMERGENCY CARD               🛡️ NON-DIAGNOSTIC NOTICE
    - Immediate Action Steps        - Clear Diagnostic Refusal
    - Urgent Referral Guidance      - Directs User to Gynecologist
    - WHO Emergency Principles      - Educational Topic Options
              │
              └───────────────┬───────────────┘
                              │ (If Safe)
                              ▼
            ┌───────────────────────────────────┐
            │   Tier 1: Intent Detection Engine │
            │   - Stop-word filtering           │
            │   - Keyword & token overlap       │
            │   - Example phrasing similarity   │
            └─────────────────┬─────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      [Matched WHO Topic]             [Unmatched / Ambiguous]
              │                               │
              ▼                               ▼
    📚 STRUCTURED TOPIC CARD        🔍 EDUCATIONAL GUIDANCE
    - Concise WHO summary           - Explains educational scope
    - Practical takeaways           - Suggests known WHO topics
    - Exact Document & Page Ref     - Clinical safety notice
    - Questions for Gynecologist
```

### Safety Principles Enforced:
- **No Diagnosis**: Refuses queries asking "Do I have pre-eclampsia?", "Is my baby sick?", or "Diagnose my symptoms".
- **No Risk Scoring**: Refuses requests to calculate numerical risk scores or predictive probability scores.
- **No Prescriptions / Dosage Changes**: Directs all medication queries to the patient's physician.
- **Immediate Escalation for Red Flags**: Emergency warning signs (vaginal bleeding, severe abdominal/epigastric pain, leaking fluid, reduced fetal movement, headache with blurred vision, high fever) immediately display a high-alert emergency escalation card with steps to seek immediate emergency obstetric care.

---

## 📚 Knowledge Base Topics (`maternal_health.json`)

The structured JSON knowledge base covers 14 comprehensive topics:
1. **`anc_schedule`**: WHO 2016 8-Contact Antenatal Care Model (Contacts at ≤12w, 20w, 26w, 30w, 34w, 36w, 38w, 40w).
2. **`nutrition`**: Healthy eating, balanced energy/protein in undernourished groups, restriction of caffeine (>300 mg/day).
3. **`iron_and_folic_acid`**: Daily oral 30–60 mg elemental iron + 400 µg (0.4 mg) folic acid; intermittent alternatives; anaemia therapy.
4. **`calcium`**: Daily 1.5–2.0 g elemental calcium for pre-eclampsia prevention; dosing with meals; separation from iron pills.
5. **`routine_investigations`**: Full blood count / haemoglobinometer, midstream urine culture / Gram stain, 24–28w GDM screening, HIV and syphilis screening, TB screening, blood pressure & proteinuria.
6. **`ultrasound`**: One routine early ultrasound before 24 weeks for gestational age dating and multiple pregnancies; avoiding routine Doppler in healthy pregnancies.
7. **`maternal_fetal_assessment`**: Awareness of fetal movement in third trimester, symphysis-fundal height vs abdominal palpation, avoiding routine CTG, intimate partner violence (IPV) enquiry.
8. **`physical_activity`**: Aerobic fitness and strength conditioning; regular exercise to prevent low back and pelvic pain.
9. **`vaccination`**: Tetanus toxoid-containing vaccine (TT-CV) schedule to prevent neonatal tetanus mortality.
10. **`common_pregnancy_symptoms`**: Evidence-based relief for nausea/vomiting (ginger, chamomile, B6, acupuncture), heartburn (diet, antacids), leg cramps (magnesium, calcium), back pain, constipation (wheat bran), varicose veins (compression stockings, leg elevation).
11. **`birth_preparedness`**: Birth plan, skilled birth attendant, emergency transport, woman-held case notes, labour companionship.
12. **`risk_high_alert`**: Critical danger signs requiring immediate emergency room or obstetric triage.
13. **`postnatal_care`**: First-week home visits, lochia monitoring, mental health/baby blues, exclusive breastfeeding, postpartum contraception.
14. **`questions_to_ask_gynecologist`**: Tailored question checklists across the first, second, and third trimesters.

---

## 📁 Directory Structure

```
nurturagyno_chatbot/
├── core/
│   ├── __init__.py
│   ├── intent_engine.py       # Deterministic intent matcher & safety interceptor
│   └── chatbot.py             # Response generator with WHO citations & follow-ups
├── knowledge_base/
│   ├── maternal_health.json   # 14 structured WHO educational topics with page references
│   └── safety_rules.json      # Emergency red flags & diagnostic blockers
├── web/
│   ├── index.html             # Responsive maternal-health UI with permanent disclaimer
│   ├── style.css              # Warm pastel aesthetic, accessible contrast, print styles
│   └── app.js                 # Chat controller, topic drawer, quick chips, auto-scroll
├── tests/
│   ├── __init__.py
│   ├── test_knowledge_base.py # Schema & completeness validation
│   ├── test_intent_engine.py  # Phrasing variation tests across all topics
│   ├── test_safety_guardrails.py # Red-flag emergency & diagnostic blocker tests
│   ├── test_chatbot_api.py    # End-to-end response payload & fallback tests
│   └── run_tests.py           # Automated test runner with reporting
├── server.py                  # Zero-dependency Python HTTP server & REST API
├── run.py                     # One-click launcher (starts server & opens browser)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (No external pip packages required; runs entirely with the Python standard library!)

### Run the Chatbot
To start the local server and automatically open the web interface in your browser:

```powershell
cd C:\Users\Pragati\.gemini\antigravity\scratch\nurturagyno_chatbot
python run.py
```

The web application will open at:
**`http://localhost:8080`**

### Run the Automated Test Suite
To verify knowledge base validity, phrasing coverage, and safety guardrails:

```powershell
python tests/run_tests.py
```

All 31 unit tests will run and report status in your terminal.

---

## 💡 REST API Endpoints

- **`POST /api/chat`**: Sends `{ "query": "..." }` and returns structured JSON containing educational responses, citations, takeaways, and questions for the gynecologist.
- **`GET /api/topics`**: Returns a list of all 14 WHO antenatal topics.
- **`GET /api/topic/<topic_id>`**: Returns the full structured data for a specific topic.
- **`GET /api/health`**: Health status and compliance verification.

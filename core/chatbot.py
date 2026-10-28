"""
chatbot.py
Core maternal health educational chatbot engine for NurturaGyno.
Enforces rule-based, deterministic response generation from WHO ANC guidelines.
Strictly non-diagnostic; provides transparent source citations and safety guardrails.
"""

import os
from typing import Dict, Any, List
from core.intent_engine import IntentEngine


class NurturaGynoChatbot:
    def __init__(self, kb_path: str = None, safety_path: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not kb_path:
            kb_path = os.path.join(base_dir, "..", "knowledge_base", "maternal_health.json")
        if not safety_path:
            safety_path = os.path.join(base_dir, "..", "knowledge_base", "safety_rules.json")

        self.engine = IntentEngine(kb_path, safety_path)
        self.kb_metadata = self.engine.kb_data.get("metadata", {})
        self.topics = self.engine.topics

    def get_all_topics(self) -> List[Dict[str, Any]]:
        """Returns overview of all available educational topics."""
        return [
            {
                "topic_id": t["topic_id"],
                "topic": t["topic"],
                "category": t["category"]
            }
            for t in self.topics.values()
        ]

    def get_topic_detail(self, topic_id: str) -> Dict[str, Any]:
        """Returns complete structured data for a specific topic."""
        return self.topics.get(topic_id, {})

    def respond(self, query: str) -> Dict[str, Any]:
        """
        Processes a user query and returns a structured response payload.
        Never hallucinates medical data; always links to WHO source references.
        """
        intent = self.engine.detect_intent(query)
        status = intent["status"]

        # Case 1: Safety Intercept (Emergency Red Flag or Diagnostic/Risk Blocker)
        if status == "SAFETY_INTERCEPT":
            alert = intent["safety_alert"]
            alert_type = alert["type"]

            if alert_type == "EMERGENCY_RED_FLAG":
                topic_content = self.topics.get("risk_high_alert", {})
                return {
                    "status": "SAFETY_FALLBACK_EMERGENCY",
                    "intent": "emergency_red_flag",
                    "severity": alert.get("severity", "CRITICAL_EMERGENCY"),
                    "title": "⚠️ Emergency Clinical Safety Alert",
                    "message": (
                        "HIGH ALERT: Your message describes symptoms that require immediate clinical attention. "
                        f"{alert['action_instruction']}"
                    ),
                    "clinical_guardrail": (
                        "NurturaGyno is an educational tool and is strictly non-diagnostic. "
                        "It cannot diagnose conditions, calculate risk scores, or provide emergency care."
                    ),
                    "action_steps": [
                        "Contact your obstetrician, gynecologist, or midwife immediately.",
                        "If you cannot reach your doctor, proceed to the nearest hospital emergency department or maternity triage unit.",
                        "Call your local emergency medical service (e.g. 112, 911, or 108).",
                        "Bring your maternal health records and pregnancy case notes with you."
                    ],
                    "exact_source_reference": topic_content.get("exact_source_reference", {
                        "document": "WHO recommendations on antenatal care for a positive pregnancy experience (2016)",
                        "recommendation_code": "Obstetric Emergency Principles",
                        "page_reference": "Executive Summary pp. ix–xi; Chapter 1.3 p. 2; Chapter 4 pp. 101, 105",
                        "chapter_or_table": "Executive Summary & Chapter 1.3 Scope of the guideline"
                    }),
                    "matched_trigger": alert.get("matched_trigger", "")
                }
            else:
                # Diagnostic, risk score, or prescription blocker
                return {
                    "status": "SAFETY_FALLBACK_GUARDRAIL",
                    "intent": alert["category"],
                    "severity": "SAFETY_NOTICE",
                    "title": "🛡️ Clinical Safety & Non-Diagnostic Notice",
                    "message": alert["guidance"],
                    "clinical_guardrail": (
                        "To protect maternal and fetal safety, NurturaGyno strictly avoids autonomous medical advice, "
                        "diagnostic evaluation, treatment adjustments, and risk calculations. "
                        "All individual clinical decisions must be made with your healthcare provider."
                    ),
                    "suggested_topics": [
                        {"id": "anc_schedule", "label": "WHO 8-Contact ANC Schedule"},
                        {"id": "routine_investigations", "label": "Routine Lab Tests & Screenings"},
                        {"id": "questions_to_ask_gynecologist", "label": "Questions to Ask Your Doctor"}
                    ],
                    "exact_source_reference": {
                        "document": "WHO recommendations on antenatal care for a positive pregnancy experience (2016)",
                        "recommendation_code": "Guideline Scope & Good Clinical Practice",
                        "page_reference": "Chapter 1.3 p. 2; Chapter 3.B.1 p. 40",
                        "chapter_or_table": "Scope of the guideline"
                    },
                    "matched_trigger": alert.get("matched_trigger", "")
                }

        # Case 2: Greeting
        if status == "GREETING":
            return {
                "status": "GREETING",
                "title": "🌸 Welcome to NurturaGyno Antenatal Education",
                "message": (
                    "Hello! I am your NurturaGyno educational assistant. I provide evidence-based antenatal care information "
                    "drawn directly from official World Health Organization (WHO) maternal health guidelines.\n\n"
                    "I can guide you through recommended appointment schedules, maternal nutrition, iron and folic acid, "
                    "calcium, routine lab investigations, ultrasound scans, safe physical activity, tetanus vaccination, "
                    "relief for common symptoms, birth preparedness, and questions for your gynecologist."
                ),
                "clinical_guardrail": "Please note: I am a purely educational chatbot. I do not diagnose medical conditions, calculate risk scores, or give individualized medical advice.",
                "suggested_topics": [
                    {"id": "anc_schedule", "label": "ANC Schedule (8 Contacts)"},
                    {"id": "nutrition", "label": "Nutrition & Diet Guidelines"},
                    {"id": "iron_and_folic_acid", "label": "Iron & Folic Acid"},
                    {"id": "calcium", "label": "Calcium Supplementation"},
                    {"id": "routine_investigations", "label": "Routine Tests & Screenings"},
                    {"id": "ultrasound", "label": "Ultrasound Scans"},
                    {"id": "physical_activity", "label": "Physical Activity & Exercise"},
                    {"id": "common_pregnancy_symptoms", "label": "Relief for Common Symptoms"},
                    {"id": "birth_preparedness", "label": "Birth Preparedness Plan"},
                    {"id": "questions_to_ask_gynecologist", "label": "Questions for Your Doctor"}
                ]
            }

        # Case 3: Menu / Help
        if status == "MENU_HELP":
            all_topics = self.get_all_topics()
            return {
                "status": "MENU_HELP",
                "title": "📚 NurturaGyno Educational Topics (WHO Guidelines)",
                "message": "Here are the maternal health educational topics you can explore:",
                "topics_list": all_topics,
                "clinical_guardrail": "All topics are evidence-based educational summaries from WHO recommendations. Non-diagnostic only."
            }

        # Case 4: Matched Topic
        if status == "MATCHED_TOPIC":
            topic_id = intent["topic_id"]
            topic_data = self.topics.get(topic_id, {})
            return {
                "status": "SUCCESS",
                "topic_id": topic_id,
                "topic": topic_data.get("topic"),
                "category": topic_data.get("category"),
                "confidence": intent.get("confidence", 1.0),
                "concise_educational_response": topic_data.get("concise_educational_response"),
                "key_educational_takeaways": topic_data.get("key_educational_takeaways", []),
                "exact_source_reference": topic_data.get("exact_source_reference", {}),
                "questions_to_ask_doctor": topic_data.get("questions_to_ask_doctor", []),
                "clinical_safety_notice": topic_data.get("clinical_safety_notice", ""),
                "suggested_followups": self._get_related_topics(topic_id)
            }

        # Case 5: Fallback / Ambiguous
        return {
            "status": "FALLBACK_AMBIGUOUS",
            "title": "🔍 Educational Topic Guidance",
            "message": (
                "I couldn't quite match your question to a specific WHO antenatal care recommendation. "
                "Because I am strictly rule-based to ensure clinical safety, I only share educational information "
                "directly extracted from WHO guidelines without guessing or generating medical advice."
            ),
            "clarification_prompt": "Could you please rephrase your question, or select from one of the core educational topics below?",
            "suggested_topics": [
                {"id": "anc_schedule", "label": "Antenatal Visit Schedule"},
                {"id": "nutrition", "label": "Maternal Nutrition & Diet"},
                {"id": "iron_and_folic_acid", "label": "Iron and Folic Acid"},
                {"id": "calcium", "label": "Calcium Supplementation"},
                {"id": "routine_investigations", "label": "Routine Blood & Urine Tests"},
                {"id": "ultrasound", "label": "Ultrasound Scanning"},
                {"id": "physical_activity", "label": "Safe Exercise & Fitness"},
                {"id": "common_pregnancy_symptoms", "label": "Common Symptoms (Nausea, Heartburn)"},
                {"id": "vaccination", "label": "Tetanus Vaccination"},
                {"id": "birth_preparedness", "label": "Birth Preparedness Planning"},
                {"id": "postnatal_care", "label": "Postpartum Care"},
                {"id": "questions_to_ask_gynecologist", "label": "Questions for Your Doctor"}
            ],
            "clinical_safety_notice": "If you are asking about acute symptoms, pain, bleeding, or suspect a medical complication, please consult your doctor immediately."
        }

    def _get_related_topics(self, topic_id: str) -> List[Dict[str, str]]:
        """Helper to suggest related topics based on context."""
        mapping = {
            "anc_schedule": [
                {"id": "routine_investigations", "label": "Routine Tests at Each Contact"},
                {"id": "ultrasound", "label": "Recommended Ultrasound Scans"},
                {"id": "questions_to_ask_gynecologist", "label": "Questions for Your Doctor"}
            ],
            "nutrition": [
                {"id": "iron_and_folic_acid", "label": "Iron & Folic Acid Doses"},
                {"id": "calcium", "label": "Calcium Supplementation"},
                {"id": "physical_activity", "label": "Exercise & Staying Active"}
            ],
            "iron_and_folic_acid": [
                {"id": "calcium", "label": "Spacing Calcium and Iron"},
                {"id": "nutrition", "label": "Dietary Sources of Iron"},
                {"id": "routine_investigations", "label": "Anaemia Lab Testing"}
            ],
            "calcium": [
                {"id": "iron_and_folic_acid", "label": "Iron vs Calcium Dosing"},
                {"id": "nutrition", "label": "Dietary Calcium Sources"},
                {"id": "routine_investigations", "label": "Pre-eclampsia Screening"}
            ],
            "routine_investigations": [
                {"id": "anc_schedule", "label": "When Tests Occur (8 Contacts)"},
                {"id": "ultrasound", "label": "Early Ultrasound Timing"},
                {"id": "questions_to_ask_gynecologist", "label": "Discussing Lab Results"}
            ],
            "ultrasound": [
                {"id": "anc_schedule", "label": "When Ultrasound Fits in Schedule"},
                {"id": "maternal_fetal_assessment", "label": "Fetal Well-being Checks"},
                {"id": "questions_to_ask_gynecologist", "label": "Questions About Scans"}
            ],
            "physical_activity": [
                {"id": "common_pregnancy_symptoms", "label": "Relief for Back & Pelvic Pain"},
                {"id": "nutrition", "label": "Balanced Nutrition & Energy"},
                {"id": "birth_preparedness", "label": "Preparing for Labour"}
            ],
            "vaccination": [
                {"id": "anc_schedule", "label": "ANC Schedule for Vaccines"},
                {"id": "routine_investigations", "label": "Infection Screening"},
                {"id": "postnatal_care", "label": "Newborn Care"}
            ],
            "common_pregnancy_symptoms": [
                {"id": "nutrition", "label": "Healthy Eating for Heartburn"},
                {"id": "physical_activity", "label": "Exercise for Back Pain"},
                {"id": "risk_high_alert", "label": "Danger Signs vs Normal Symptoms"}
            ],
            "birth_preparedness": [
                {"id": "anc_schedule", "label": "Third Trimester Contacts"},
                {"id": "postnatal_care", "label": "Postnatal Care & Home Visits"},
                {"id": "questions_to_ask_gynecologist", "label": "Birth Plan Questions"}
            ],
            "postnatal_care": [
                {"id": "birth_preparedness", "label": "Birth Planning"},
                {"id": "anc_schedule", "label": "Full Pregnancy Journey"},
                {"id": "questions_to_ask_gynecologist", "label": "Postpartum Checkup Questions"}
            ],
            "risk_high_alert": [
                {"id": "questions_to_ask_gynecologist", "label": "Doctor Emergency Protocol"},
                {"id": "birth_preparedness", "label": "Emergency Transport Plan"},
                {"id": "anc_schedule", "label": "Routine Care Schedule"}
            ],
            "maternal_fetal_assessment": [
                {"id": "ultrasound", "label": "Ultrasound Scanning"},
                {"id": "risk_high_alert", "label": "Reporting Reduced Movement"},
                {"id": "anc_schedule", "label": "8 Contacts Schedule"}
            ],
            "questions_to_ask_gynecologist": [
                {"id": "anc_schedule", "label": "WHO 8-Contact Model"},
                {"id": "routine_investigations", "label": "Routine Investigations"},
                {"id": "birth_preparedness", "label": "Birth Preparedness"}
            ]
        }
        return mapping.get(topic_id, [
            {"id": "anc_schedule", "label": "ANC Schedule"},
            {"id": "nutrition", "label": "Nutrition Guidelines"}
        ])

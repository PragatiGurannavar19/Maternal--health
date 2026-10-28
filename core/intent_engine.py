"""
intent_engine.py
Deterministic, rule-based intent detection and clinical safety guardrail engine
for NurturaGyno Maternal Health Educational Chatbot.
Strictly adheres to WHO Antenatal Care guidelines.
Non-diagnostic; blocks medical advice, risk scoring, and clinical decision support.
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had",
    "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself",
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "with", "would", "you",
    "your", "yours", "yourself", "yourselves", "tell", "show", "please", "can", "give"
}


class IntentEngine:
    def __init__(self, knowledge_base_path: str, safety_rules_path: str):
        with open(knowledge_base_path, "r", encoding="utf-8") as f:
            self.kb_data = json.load(f)
        
        with open(safety_rules_path, "r", encoding="utf-8") as f:
            self.safety_rules = json.load(f)

        self.topics = {t["topic_id"]: t for t in self.kb_data.get("topics", [])}
        self._normalize_safety_patterns()
        self._build_keyword_mappings()

    def _normalize(self, text: str) -> str:
        """Lowercases and cleans input text for deterministic matching."""
        text = text.lower().strip()
        # Remove punctuation
        text = re.sub(r"[^\w\s]", " ", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _normalize_safety_patterns(self):
        """Normalizes all patterns in safety rules so they match clean input."""
        for flag in self.safety_rules.get("emergency_red_flags", []):
            flag["patterns"] = [self._normalize(p) for p in flag["patterns"]]
        for blocker in self.safety_rules.get("diagnostic_blockers", []):
            blocker["patterns"] = [self._normalize(p) for p in blocker["patterns"]]

    def _build_keyword_mappings(self):
        """Builds weighted keywords and patterns for each topic from WHO guidelines."""
        raw_keywords = {
            "anc_schedule": [
                "anc schedule", "contact schedule", "how many visits", "how many contacts",
                "8 contacts", "eight contacts", "frequency of visits", "when should i see",
                "appointment schedule", "checkup schedule", "first visit", "first contact",
                "second contact", "third trimester visits", "fanc model", "4 visit",
                "routine visits", "gestation weeks visit", "weeks pregnant visit",
                "doctor visits schedule", "prenatal appointments", "visit schedule",
                "antenatal care schedule", "who schedule", "eight visits"
            ],
            "nutrition": [
                "nutrition", "what should i eat", "diet", "healthy eating", "food to eat",
                "foods to avoid", "weight gain", "gestational weight gain", "bmi weight",
                "balanced diet", "protein intake", "caffeine", "coffee", "tea",
                "energy intake", "undernutrition", "dietary counselling", "green vegetables",
                "meat fish", "fruit beans", "high protein powder", "how much coffee",
                "maternal diet", "eating healthy", "healthy food"
            ],
            "iron_and_folic_acid": [
                "folic acid", "iron", "elemental iron", "ferrous sulfate", "ferrous fumarate",
                "ferrous gluconate", "anaemia prevention", "neural tube defects", "spina bifida",
                "folic acid dose", "iron dose", "30 mg iron", "60 mg iron", "400 ug folic",
                "0.4 mg folic", "daily iron", "weekly iron", "intermittent iron",
                "iron side effects", "iron constipation", "iron nausea", "haemoglobin 110",
                "blood pills", "prenatal iron", "iron tablets", "folate"
            ],
            "calcium": [
                "calcium", "calcium supplements", "calcium intake", "calcium and pre-eclampsia",
                "calcium pre eclampsia", "elemental calcium", "1 5 g calcium", "2 g calcium",
                "calcium tablets", "calcium with iron", "separate calcium and iron",
                "calcium rich foods", "milk dairy calcium", "divide calcium dose",
                "calcium pills"
            ],
            "routine_investigations": [
                "routine tests", "routine investigations", "blood tests", "urine tests",
                "lab tests", "full blood count", "fbc", "haemoglobinometer", "haemoglobin test",
                "asymptomatic bacteriuria", "asb", "urine culture", "gram stain",
                "dipstick", "gestational diabetes", "gdm", "glucose tolerance test",
                "ogtt", "75 g oral glucose", "hiv test", "syphilis screening",
                "tuberculosis screening", "tb test", "blood pressure check",
                "proteinuria test", "screening tests", "routine screening"
            ],
            "ultrasound": [
                "ultrasound", "sonogram", "scan", "early ultrasound", "before 24 weeks",
                "20 week scan", "dating scan", "anatomy scan", "fetal anomalies scan",
                "late ultrasound", "third trimester scan", "doppler ultrasound",
                "umbilical doppler", "how many scans", "when is ultrasound done",
                "pregnancy ultrasound", "ultrasound scan"
            ],
            "maternal_fetal_assessment": [
                "fetal assessment", "baby movement", "kick count", "kick chart", "cardiff",
                "count to ten", "baby kicks", "symphysis fundal height", "sfh",
                "abdominal palpation", "fetal growth", "cardiotocography", "ctg",
                "fetal heart rate monitoring", "intimate partner violence", "ipv",
                "how is baby growing", "checking fetal well being", "fetal movement counting"
            ],
            "physical_activity": [
                "physical activity", "exercise", "exercising", "walking", "brisk walking",
                "yoga", "prenatal yoga", "swimming", "aqua aerobics", "workout",
                "is it safe to exercise", "fitness in pregnancy", "exercise for back pain",
                "safe activities", "sports pregnant", "strength conditioning",
                "keeping physically active"
            ],
            "vaccination": [
                "vaccination", "vaccine", "tetanus", "tetanus toxoid", "tt vaccine",
                "tt cv", "immunization", "tetanus shots", "how many tetanus", "injection",
                "maternal immunization", "prevent neonatal tetanus", "vaccination schedule",
                "shots during pregnancy", "vaccine safety pregnancy", "tetanus injection"
            ],
            "common_pregnancy_symptoms": [
                "pregnancy symptoms", "common symptoms", "morning sickness", "nausea",
                "vomiting", "ginger", "vitamin b6 nausea", "acupuncture nausea",
                "heartburn", "acid reflux", "antacids", "leg cramps", "cramps in legs",
                "back pain", "pelvic pain", "low back pain", "constipation",
                "wheat bran", "fibre supplements", "varicose veins", "swollen feet",
                "leg oedema", "compression stockings", "water immersion", "piles"
            ],
            "birth_preparedness": [
                "birth preparedness", "birth plan", "complication readiness", "preparing for birth",
                "labour companion", "birth companion", "case notes", "handbook", "held records",
                "emergency transport", "emergency fund", "delivery hospital",
                "skilled birth attendant", "midwife care", "preparing for labour"
            ],
            "risk_high_alert": [
                "danger signs", "warning signs", "red flags", "emergency signs",
                "when to go to hospital", "emergency in pregnancy", "complications",
                "high risk alert", "critical signs", "urgent medical care", "obstetric emergency"
            ],
            "postnatal_care": [
                "postnatal care", "postpartum care", "after birth", "after delivery",
                "postnatal visits", "first week after birth", "home visit", "lochia",
                "uterine involution", "baby blues", "postpartum depression",
                "exclusive breastfeeding", "postpartum family planning", "contraception after birth",
                "six week checkup", "care after delivery"
            ],
            "questions_to_ask_gynecologist": [
                "questions to ask", "what to ask", "questions for doctor", "questions for gynecologist",
                "questions for ob gyn", "first appointment questions", "what should i ask my doctor",
                "doctor checklist", "prepare for visit", "communicating with doctor",
                "questions to prepare"
            ]
        }
        self.topic_keywords = {
            t_id: [self._normalize(kw) for kw in kws]
            for t_id, kws in raw_keywords.items()
        }

    def detect_safety_alert(self, normalized_text: str) -> Optional[Dict[str, Any]]:
        """
        Stage 0: Strict Safety Guardrail
        Detects emergency red flags, diagnostic requests, risk scoring requests,
        and prescription alteration queries.
        """
        # 1. Emergency Red Flags (Highest Priority)
        for flag in self.safety_rules.get("emergency_red_flags", []):
            for pat in flag["patterns"]:
                if pat in normalized_text:
                    return {
                        "type": "EMERGENCY_RED_FLAG",
                        "category": flag["category"],
                        "severity": flag.get("severity", "CRITICAL_EMERGENCY"),
                        "action_instruction": flag["action_instruction"],
                        "matched_trigger": pat
                    }

        # 2. Diagnostic Blockers (Do not diagnose, calculate risk scores, or prescribe)
        for blocker in self.safety_rules.get("diagnostic_blockers", []):
            for pat in blocker["patterns"]:
                if pat in normalized_text:
                    return {
                        "type": "DIAGNOSTIC_BLOCKER",
                        "category": blocker["category"],
                        "severity": "SAFETY_FALLBACK",
                        "guidance": blocker["response_guidance"],
                        "matched_trigger": pat
                    }

        return None

    def detect_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point for intent detection.
        Returns a structured dictionary with intent, topic_id, score, and safety metadata.
        """
        normalized = self._normalize(user_query)

        # 1. Check Safety & Clinical Boundaries First
        safety_alert = self.detect_safety_alert(normalized)
        if safety_alert:
            return {
                "status": "SAFETY_INTERCEPT",
                "safety_alert": safety_alert,
                "topic_id": "risk_high_alert" if safety_alert["type"] == "EMERGENCY_RED_FLAG" else None,
                "confidence": 1.0,
                "normalized_query": normalized
            }

        # 2. Check Greetings & Help Commands
        query_tokens = [w for w in normalized.split() if w]
        if query_tokens:
            first_word = query_tokens[0]
            if first_word in ["hello", "hi", "hey", "greetings"] or normalized in ["good morning", "good evening", "good afternoon"]:
                return {
                    "status": "GREETING",
                    "topic_id": None,
                    "confidence": 1.0,
                    "normalized_query": normalized
                }

            help_words = {"help", "topics", "menu", "options", "guide"}
            if any(hw in query_tokens for hw in help_words) or "what can you do" in normalized or "list topics" in normalized:
                # If it's not a specific topic question containing the word 'guide'
                if normalized in ["help", "topics", "menu", "show menu", "show topics", "topics menu", "what can you do", "options", "guide", "show me the topics menu"]:
                    return {
                        "status": "MENU_HELP",
                        "topic_id": None,
                        "confidence": 1.0,
                        "normalized_query": normalized
                    }

        # 3. Topic Matching via Keywords & Example Phrasings (Filtered by STOP_WORDS)
        content_words = {w for w in query_tokens if w not in STOP_WORDS and len(w) > 2}
        best_topic_id = None
        best_score = 0.0

        for topic_id, keywords in self.topic_keywords.items():
            topic_score = 0.0

            # Match exact keyphrases
            for kw in keywords:
                if kw in normalized:
                    # Longer phrase matches provide stronger confidence
                    weight = len(kw.split()) * 3.0
                    topic_score += weight
                else:
                    # Token overlap with content words only
                    kw_content = {w for w in kw.split() if w not in STOP_WORDS and len(w) > 2}
                    overlap = len(content_words.intersection(kw_content))
                    if overlap > 0:
                        topic_score += overlap * 0.75

            # Also check similarity to topic's explicit example_user_questions in KB
            kb_topic = self.topics.get(topic_id)
            if kb_topic:
                for example_q in kb_topic.get("example_user_questions", []):
                    norm_ex = self._normalize(example_q)
                    if norm_ex in normalized or normalized in norm_ex:
                        topic_score += 5.0
                    ex_content = {w for w in norm_ex.split() if w not in STOP_WORDS and len(w) > 2}
                    common_tokens = len(content_words.intersection(ex_content))
                    if common_tokens > 0:
                        union_tokens = len(content_words.union(ex_content))
                        jaccard = common_tokens / union_tokens if union_tokens > 0 else 0
                        topic_score += jaccard * 4.0

            if topic_score > best_score:
                best_score = topic_score
                best_topic_id = topic_id

        # 4. Threshold requirement (Must have genuine content match)
        threshold = 2.5
        if best_topic_id and best_score >= threshold:
            return {
                "status": "MATCHED_TOPIC",
                "topic_id": best_topic_id,
                "confidence": min(1.0, best_score / 6.0),
                "score": best_score,
                "normalized_query": normalized
            }

        # 5. Fallback for unclassified / ambiguous queries
        return {
            "status": "FALLBACK_AMBIGUOUS",
            "topic_id": None,
            "confidence": 0.0,
            "score": best_score,
            "normalized_query": normalized
        }

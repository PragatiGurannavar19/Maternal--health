"""
test_knowledge_base.py
Tests the structure, schema, completeness, and grounding of maternal_health.json.
Validates all required WHO topics and exact citations.
"""

import json
import os
import unittest


class TestMaternalHealthKnowledgeBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.kb_path = os.path.join(base_dir, "..", "knowledge_base", "maternal_health.json")
        with open(cls.kb_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_metadata_structure(self):
        """Verifies metadata contains safety disclaimer and primary WHO source citations."""
        self.assertIn("metadata", self.data)
        meta = self.data["metadata"]
        self.assertIn("safety_disclaimer", meta)
        self.assertIn("non-diagnostic", meta["safety_disclaimer"].lower())
        self.assertIn("primary_sources", meta)
        self.assertGreaterEqual(len(meta["primary_sources"]), 2)

    def test_required_topics_present(self):
        """Verifies all mandatory maternal health topics requested are present."""
        required_topics = [
            "anc_schedule",
            "nutrition",
            "iron_and_folic_acid",
            "calcium",
            "routine_investigations",
            "ultrasound",
            "maternal_fetal_assessment",
            "physical_activity",
            "vaccination",
            "common_pregnancy_symptoms",
            "birth_preparedness",
            "risk_high_alert",
            "postnatal_care",
            "questions_to_ask_gynecologist"
        ]
        
        existing_ids = [t["topic_id"] for t in self.data["topics"]]
        for req in required_topics:
            self.assertIn(req, existing_ids, f"Required topic '{req}' is missing from knowledge base.")

    def test_topic_fields_completeness(self):
        """Verifies every topic entry has all required educational and source citation fields."""
        required_fields = [
            "topic_id",
            "topic",
            "category",
            "example_user_questions",
            "concise_educational_response",
            "exact_source_reference",
            "key_educational_takeaways",
            "questions_to_ask_doctor",
            "clinical_safety_notice"
        ]

        for topic in self.data["topics"]:
            t_id = topic["topic_id"]
            for field in required_fields:
                self.assertIn(field, topic, f"Topic '{t_id}' missing field '{field}'")
            
            # Verify user questions
            self.assertIsInstance(topic["example_user_questions"], list)
            self.assertGreaterEqual(len(topic["example_user_questions"]), 4, f"Topic '{t_id}' needs at least 4 example questions")

            # Verify educational response
            self.assertIsInstance(topic["concise_educational_response"], str)
            self.assertGreater(len(topic["concise_educational_response"]), 50, f"Topic '{t_id}' response is too short")

            # Verify source reference has exact document, recommendation and page numbers
            src = topic["exact_source_reference"]
            self.assertIn("document", src, f"Topic '{t_id}' missing document reference")
            self.assertIn("page_reference", src, f"Topic '{t_id}' missing page reference")
            self.assertIn("recommendation_code", src, f"Topic '{t_id}' missing recommendation code")
            self.assertIn("pp.", src["page_reference"], f"Topic '{t_id}' page reference must include page numbers (pp.)")

    def test_non_diagnostic_boundary_in_kb(self):
        """Verifies the educational text explicitly does not claim to diagnose or treat patients."""
        forbidden_phrases = [
            "you are diagnosed with",
            "i diagnose you",
            "your risk score is",
            "take this prescription"
        ]
        for topic in self.data["topics"]:
            resp_lower = topic["concise_educational_response"].lower()
            for forb in forbidden_phrases:
                self.assertNotIn(forb, resp_lower, f"Forbidden diagnostic claim found in {topic['topic_id']}")


if __name__ == "__main__":
    unittest.main()

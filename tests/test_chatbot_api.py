"""
test_chatbot_api.py
Tests the NurturaGynoChatbot class methods and response payload structures.
"""

import os
import unittest
from core.chatbot import NurturaGynoChatbot


class TestChatbotAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        kb_path = os.path.join(base_dir, "..", "knowledge_base", "maternal_health.json")
        safety_path = os.path.join(base_dir, "..", "knowledge_base", "safety_rules.json")
        cls.bot = NurturaGynoChatbot(kb_path, safety_path)

    def test_get_all_topics(self):
        topics = self.bot.get_all_topics()
        self.assertIsInstance(topics, list)
        self.assertGreaterEqual(len(topics), 14)
        for t in topics:
            self.assertIn("topic_id", t)
            self.assertIn("topic", t)
            self.assertIn("category", t)

    def test_get_topic_detail(self):
        detail = self.bot.get_topic_detail("anc_schedule")
        self.assertIsNotNone(detail)
        self.assertEqual(detail["topic_id"], "anc_schedule")
        self.assertIn("concise_educational_response", detail)
        self.assertIn("exact_source_reference", detail)

    def test_successful_topic_query(self):
        res = self.bot.respond("Tell me about the 8 contacts antenatal care model")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["topic_id"], "anc_schedule")
        self.assertIn("concise_educational_response", res)
        self.assertIn("key_educational_takeaways", res)
        self.assertIn("exact_source_reference", res)
        self.assertIn("questions_to_ask_doctor", res)
        self.assertIn("clinical_safety_notice", res)
        self.assertIn("suggested_followups", res)

    def test_ambiguous_out_of_scope_query(self):
        res = self.bot.respond("What is the latest score in the football match?")
        self.assertEqual(res["status"], "FALLBACK_AMBIGUOUS")
        self.assertIn("suggested_topics", res)
        self.assertIn("clarification_prompt", res)
        self.assertIn("clinical_safety_notice", res)

    def test_greeting_query(self):
        res = self.bot.respond("Hello NurturaGyno")
        self.assertEqual(res["status"], "GREETING")
        self.assertIn("suggested_topics", res)
        self.assertIn("clinical_guardrail", res)

    def test_menu_help_query(self):
        res = self.bot.respond("Show me the topics menu")
        self.assertEqual(res["status"], "MENU_HELP")
        self.assertIn("topics_list", res)


if __name__ == "__main__":
    unittest.main()

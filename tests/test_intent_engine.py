"""
test_intent_engine.py
Tests the intent detection engine to ensure diverse user phrasings correctly
map to the appropriate WHO educational topics.
"""

import os
import unittest
from core.intent_engine import IntentEngine


class TestIntentDetectionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        kb_path = os.path.join(base_dir, "..", "knowledge_base", "maternal_health.json")
        safety_path = os.path.join(base_dir, "..", "knowledge_base", "safety_rules.json")
        cls.engine = IntentEngine(kb_path, safety_path)

    def test_anc_schedule_phrasings(self):
        phrasings = [
            "How many antenatal visits should I have?",
            "What is the recommended checkup schedule during pregnancy?",
            "When should my first doctor appointment be?",
            "How often do I need to see my gynecologist?",
            "Tell me about the WHO 8 contacts model"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "anc_schedule", f"Failed for query: '{q}'")

    def test_nutrition_phrasings(self):
        phrasings = [
            "What should I eat during pregnancy?",
            "How much weight should I gain while pregnant?",
            "Can I drink coffee or tea while pregnant?",
            "Are high protein powders safe for pregnant women?",
            "What is a balanced diet for pregnancy?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "nutrition", f"Failed for query: '{q}'")

    def test_iron_and_folic_acid_phrasings(self):
        phrasings = [
            "Why do I need to take folic acid and iron?",
            "What is the recommended daily dose of iron and folic acid?",
            "When should I start taking folic acid?",
            "What if iron supplements give me constipation?",
            "How much elemental iron should I take daily?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "iron_and_folic_acid", f"Failed for query: '{q}'")

    def test_calcium_phrasings(self):
        phrasings = [
            "Do I need to take calcium pills while pregnant?",
            "How much calcium should a pregnant woman take daily?",
            "Why is calcium recommended for pre-eclampsia prevention?",
            "Can I take calcium and iron tablets together?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "calcium", f"Failed for query: '{q}'")

    def test_routine_investigations_phrasings(self):
        phrasings = [
            "What routine tests do I need during pregnancy?",
            "Why do I need urine and blood tests at antenatal visits?",
            "When is gestational diabetes tested in pregnancy?",
            "Tell me about the 75g oral glucose tolerance test",
            "Why do doctors test for HIV and syphilis during pregnancy?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "routine_investigations", f"Failed for query: '{q}'")

    def test_ultrasound_phrasings(self):
        phrasings = [
            "When should I get my first pregnancy ultrasound?",
            "How many ultrasounds are recommended by WHO?",
            "Do I need an ultrasound in the third trimester?",
            "What is the purpose of an early ultrasound scan?",
            "Is a routine Doppler ultrasound necessary?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "ultrasound", f"Failed for query: '{q}'")

    def test_physical_activity_phrasings(self):
        phrasings = [
            "Is it safe to exercise while pregnant?",
            "What kinds of physical activity are recommended?",
            "Can prenatal yoga and walking help?",
            "How much workout should I do during pregnancy?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "physical_activity", f"Failed for query: '{q}'")

    def test_vaccination_phrasings(self):
        phrasings = [
            "What vaccines are recommended during pregnancy?",
            "Why is the tetanus injection given to pregnant women?",
            "How many tetanus shots do I need while pregnant?",
            "Is the tetanus toxoid vaccine safe for my baby?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "vaccination", f"Failed for query: '{q}'")

    def test_common_symptoms_phrasings(self):
        phrasings = [
            "How do I manage common pregnancy symptoms?",
            "How can I relieve morning sickness naturally with ginger?",
            "What is safe for heartburn during pregnancy?",
            "How can I get relief from painful leg cramps?",
            "What can I do for swollen feet and varicose veins?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "common_pregnancy_symptoms", f"Failed for query: '{q}'")

    def test_birth_preparedness_phrasings(self):
        phrasings = [
            "What is birth preparedness planning?",
            "How should I prepare for labour and delivery?",
            "Why should I carry my own maternal case notes?",
            "Can I have a birth companion in the labour room?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "birth_preparedness", f"Failed for query: '{q}'")

    def test_postnatal_care_phrasings(self):
        phrasings = [
            "What care is needed after giving birth?",
            "When should my postnatal visits take place?",
            "What does WHO recommend for mother and baby after delivery?",
            "What should I know about postpartum baby blues?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "postnatal_care", f"Failed for query: '{q}'")

    def test_questions_for_gynecologist_phrasings(self):
        phrasings = [
            "What questions should I ask my gynecologist at my first visit?",
            "What should I discuss with my OB/GYN during antenatal appointments?",
            "What questions to ask doctor about ultrasound and blood test results?"
        ]
        for q in phrasings:
            res = self.engine.detect_intent(q)
            self.assertEqual(res["topic_id"], "questions_to_ask_gynecologist", f"Failed for query: '{q}'")

    def test_greetings_and_help(self):
        greetings = ["hello", "hi", "hey", "good morning"]
        for g in greetings:
            res = self.engine.detect_intent(g)
            self.assertEqual(res["status"], "GREETING")

        help_queries = ["help", "topics", "menu", "what can you do"]
        for h in help_queries:
            res = self.engine.detect_intent(h)
            self.assertEqual(res["status"], "MENU_HELP")


if __name__ == "__main__":
    unittest.main()

"""
run_tests.py
Executes all unit and integration test suites for NurturaGyno Chatbot.
"""

import os
import sys
import unittest

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_all_tests():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(test_dir, ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("=" * 70)
    print(" [NURTURAGYNO CHATBOT: COMPREHENSIVE TEST SUITE]")
    print(" Evidence-Based Rule-Engine & Clinical Safety Verification")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    if result.wasSuccessful():
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED. PLEASE REVIEW LOGS.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

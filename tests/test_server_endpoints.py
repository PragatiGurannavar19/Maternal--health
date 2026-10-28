"""
test_server_endpoints.py
Integration tests running the HTTP server and making actual network requests
to verify REST API and static file serving.
"""

import os
import sys
import json
import time
import threading
import unittest
import urllib.request
import urllib.error

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server import HTTPServer, NurturaGynoHandler

TEST_PORT = 8999


class TestServerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("", TEST_PORT), NurturaGynoHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_health_endpoint(self):
        url = f"http://localhost:{TEST_PORT}/api/health"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data["status"], "healthy")
            self.assertIn("NurturaGyno", data["app"])

    def test_get_topics_endpoint(self):
        url = f"http://localhost:{TEST_PORT}/api/topics"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIn("topics", data)
            self.assertGreaterEqual(len(data["topics"]), 14)

    def test_get_specific_topic_endpoint(self):
        url = f"http://localhost:{TEST_PORT}/api/topic/nutrition"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data["topic_id"], "nutrition")

    def test_post_chat_normal_query(self):
        url = f"http://localhost:{TEST_PORT}/api/chat"
        payload = json.dumps({"query": "What should I eat during pregnancy?"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(data["topic_id"], "nutrition")
            self.assertIn("exact_source_reference", data)

    def test_post_chat_emergency_query(self):
        url = f"http://localhost:{TEST_PORT}/api/chat"
        payload = json.dumps({"query": "I have sudden heavy bleeding and pain"}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertEqual(data["status"], "SAFETY_FALLBACK_EMERGENCY")
            self.assertIn("action_steps", data)

    def test_static_html_served(self):
        url = f"http://localhost:{TEST_PORT}/"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            content = response.read().decode("utf-8")
            self.assertIn("<title>NurturaGyno", content)
            self.assertIn("NON-DIAGNOSTIC NOTICE", content)


if __name__ == "__main__":
    unittest.main()

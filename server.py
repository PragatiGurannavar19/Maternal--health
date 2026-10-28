"""
server.py
Zero-dependency HTTP Server & REST API for NurturaGyno Maternal Health Chatbot.
Built using Python standard library (http.server, json, urllib).
Serves web frontend and handles /api/chat, /api/topics, /api/topic/<id>, /api/health.
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ensure core package is in import path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from core.chatbot import NurturaGynoChatbot

bot = NurturaGynoChatbot()
WEB_DIR = os.path.join(base_dir, "web")


class NurturaGynoHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Health endpoint
        if path == "/api/health":
            self._set_headers(200)
            health_payload = {
                "status": "healthy",
                "app": "NurturaGyno Antenatal Chatbot",
                "engine": "Rule-Based Deterministic Intent Engine",
                "clinical_standard": "WHO 2016 Antenatal Care Guidelines",
                "disclaimer": "Non-diagnostic educational assistant"
            }
            self.wfile.write(json.dumps(health_payload).encode("utf-8"))
            return

        # List all topics
        if path == "/api/topics":
            self._set_headers(200)
            topics = bot.get_all_topics()
            self.wfile.write(json.dumps({"topics": topics}).encode("utf-8"))
            return

        # Get specific topic detail
        if path.startswith("/api/topic/"):
            topic_id = path[len("/api/topic/"):].strip()
            detail = bot.get_topic_detail(topic_id)
            if detail:
                self._set_headers(200)
                self.wfile.write(json.dumps(detail).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Topic '{topic_id}' not found"}).encode("utf-8"))
            return

        # Static file serving
        clean_path = path.lstrip("/")
        if not clean_path or clean_path == "":
            clean_path = "index.html"

        file_path = os.path.join(WEB_DIR, clean_path)
        # Prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(WEB_DIR)):
            self._set_headers(403, "text/plain")
            self.wfile.write(b"Forbidden")
            return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"
            if mime_type.startswith("text/") or mime_type in ["application/javascript", "application/json"]:
                mime_type += "; charset=utf-8"

            self._set_headers(200, mime_type)
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        # 404 for unknown static routes
        self._set_headers(404, "text/plain")
        self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode("utf-8"))
                return

            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return

            query = data.get("query", "").strip()
            if not query:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'query' field"}).encode("utf-8"))
                return

            response = bot.respond(query)
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        # Override to keep server logs clean
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, NurturaGynoHandler)
    print(f"🌸 NurturaGyno Maternal Health Chatbot running on http://localhost:{port}")
    print(f"📖 Serving WHO Antenatal Care Guidelines Educational Interface")
    print(f"🛑 Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)

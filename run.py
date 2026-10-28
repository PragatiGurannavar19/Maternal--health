"""
run.py
Main entry point to launch NurturaGyno Maternal Health Educational Chatbot.
Starts the local server and opens the web application in your default browser.
"""

import os
import sys
import webbrowser
from threading import Timer

# Ensure project path is accessible
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from server import run_server

def open_browser(port):
    url = f"http://localhost:{port}"
    print(f"🌐 Opening NurturaGyno web interface in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    # Schedule browser opening after 1 second
    Timer(1.0, open_browser, args=[port]).start()
    run_server(port)

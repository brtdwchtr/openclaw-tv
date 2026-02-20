#!/usr/bin/env python3
"""
OpenClaw TV Avatar Server
Serves the avatar UI and provides a state API for controlling it.

GET  /api/state        — Returns current avatar state as JSON
POST /api/state        — Updates avatar state (mood, message, audio, etc.)
GET  /avatar/          — Serves the particle cloud avatar HTML
GET  /static/<file>    — Serves static files (generated audio, etc.)

Usage:
  python3 server.py [--port 8080] [--dir ~/.openclaw-tv]
"""
import http.server
import json
import os
import argparse

STATE = {
    "mood": "idle",
    "message": "",
    "audio": "",
    "intensity": 0.5,
}

INSTALL_DIR = os.environ.get("OPENCLAW_TV_DIR", os.path.expanduser("~/.openclaw-tv"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=INSTALL_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/state":
            self._json(200, STATE)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/state":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            STATE.update(body)
            self._json(200, STATE)
        else:
            self.send_error(404)

    def _json(self, code, data):
        payload = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self._cors()
        self.end_headers()
        self.wfile.write(payload)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        pass  # Suppress default logging


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenClaw TV Avatar Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--dir", default=INSTALL_DIR)
    args = parser.parse_args()

    INSTALL_DIR = args.dir
    server = http.server.HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"OpenClaw TV Avatar Server on :{args.port}")
    print(f"  Avatar: http://localhost:{args.port}/avatar/index.html")
    print(f"  API:    http://localhost:{args.port}/api/state")
    server.serve_forever()

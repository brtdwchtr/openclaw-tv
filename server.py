#!/usr/bin/env python3
"""ClawdPi Avatar Server v2 - serves avatar + state API with video support"""
import http.server, json, os

STATE = {"mood": "idle", "message": "", "intensity": 0.5, "video": ""}
WEB_DIR = "/home/bart/clawdpi-tv"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    def do_GET(self):
        if self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(STATE).encode())
        else:
            super().do_GET()
    def do_POST(self):
        if self.path == '/api/state':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            STATE.update(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(STATE).encode())
        else:
            self.send_error(404)
    def log_message(self, format, *args): pass

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 8080), Handler)
    print("ClawdPi Avatar Server v2 on :8080")
    server.serve_forever()

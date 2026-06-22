"""
Serve the real-time UI locally, proxying WebSocket to the deployed Cloud Run service.

Usage:
    python ui/serve_local.py

Then open: http://localhost:8765
"""
import http.server
import urllib.request
import urllib.parse
import threading
import os
import re
from pathlib import Path

import sys
_LOCAL_MODE = "--local" in sys.argv
API_URL = "http://localhost:8080" if _LOCAL_MODE else "https://mgvaovao-inference-97374817504.us-central1.run.app"
WS_HOST = "localhost:8080"       if _LOCAL_MODE else "mgvaovao-inference-97374817504.us-central1.run.app"
WS_PROTO = "ws"                  if _LOCAL_MODE else "wss"
PORT    = 8765
STATIC  = Path(__file__).parent / "static"

# Patched app.js: replace wsUrl() to point at deployed service
_app_js_cache = None

def _patched_app_js():
    global _app_js_cache
    if _app_js_cache is None:
        src = (STATIC / "app.js").read_text(encoding="utf-8")
        # Point WebSocket at deployed Cloud Run service
        src = src.replace(
            'const proto = location.protocol === "https:" ? "wss" : "ws";',
            f'const proto = "{WS_PROTO}";'
        ).replace(
            '`${proto}://${location.host}/ws/stream/${dialect}${lang}`',
            f'`{WS_PROTO}://{WS_HOST}/ws/stream/${{dialect}}${{lang}}`'
        )
        # Fix AudioWorklet path: locally files are at /audio-processor.js not /live/...
        src = src.replace(
            'await audioCtx.audioWorklet.addModule("/live/audio-processor.js");',
            'await audioCtx.audioWorklet.addModule("/audio-processor.js");'
        )
        _app_js_cache = src.encode("utf-8")
    return _app_js_cache


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def do_GET(self):
        # Serve audio-processor.js regardless of /live/ prefix
        if self.path in ("/audio-processor.js", "/live/audio-processor.js"):
            data = (STATIC / "audio-processor.js").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
            return

        # Serve patched app.js
        if self.path in ("/app.js", "/live/app.js"):
            data = _patched_app_js()
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
            return

        # Proxy REST calls to deployed API
        if self.path.startswith(("/translate", "/dialects", "/health", "/ready")):
            url = API_URL + self.path
            try:
                with urllib.request.urlopen(url) as resp:
                    body = resp.read()
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        if k.lower() not in ("transfer-encoding", "connection"):
                            self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(body)
            except Exception as e:
                self.send_error(502, str(e))
            return

        super().do_GET()

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    print(f"MGVaovao local UI  ->  http://localhost:{PORT}")
    print(f"WebSocket proxied  ->  {API_URL}")
    print(f"Press Ctrl+C to stop.\n")
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

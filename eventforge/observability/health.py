from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9601):
        self.status = {"health": "ok", "ready": True, "live": True}
        self._server = ThreadingHTTPServer((host, port), self._handler())
        self._thread: threading.Thread | None = None

    def _handler(self):
        status = self.status

        class Handler(BaseHTTPRequestHandler):
            def _respond(self, code: int, payload: dict):
                body = json.dumps(payload).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/health":
                    self._respond(200, {"status": status["health"]})
                elif self.path == "/ready":
                    self._respond(200 if status["ready"] else 503, {"ready": status["ready"]})
                elif self.path == "/live":
                    self._respond(200 if status["live"] else 503, {"live": status["live"]})
                else:
                    self._respond(404, {"error": "not_found"})

            def log_message(self, *_args):
                return

        return Handler

    def start(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()

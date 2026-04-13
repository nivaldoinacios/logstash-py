from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from pydantic import Field

from eventforge.core.event import Event
from eventforge.plugins.base import InputPlugin, PluginConfig, PluginMetadata


class HttpInputConfig(PluginConfig):
    host: str = "127.0.0.1"
    port: int = 8080
    path: str = "/"
    add_headers_to_metadata: bool = True
    tags: list[str] = Field(default_factory=list)


class HttpInput(InputPlugin):
    metadata = PluginMetadata(name="http", description="HTTP server input")
    config_model = HttpInputConfig

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._server: ThreadingHTTPServer | None = None

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()

    def run(self, emit: callable) -> None:
        plugin = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                if self.path != plugin.config.path:
                    self.send_response(404)
                    self.end_headers()
                    return
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length)
                ctype = self.headers.get("Content-Type", "")
                event = Event.new()
                if "application/json" in ctype:
                    body = json.loads(raw.decode("utf-8"))
                    if isinstance(body, dict):
                        event.data.update(body)
                    else:
                        event.set("message", body)
                else:
                    event.set("message", raw.decode("utf-8", errors="replace"))
                if plugin.config.add_headers_to_metadata:
                    event.set("[@metadata][headers]", dict(self.headers.items()))
                for tag in plugin.config.tags:
                    event.add_tag(tag)
                emit(event)
                self.send_response(202)
                self.end_headers()

            def log_message(self, *_args: Any) -> None:
                return

        self._server = ThreadingHTTPServer((self.config.host, self.config.port), Handler)
        self._server.serve_forever()

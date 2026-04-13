from __future__ import annotations

from urllib import request
from pystash.core.event import Event
from pystash.plugins.base import InputPlugin


class HttpInput(InputPlugin):
    plugin_name = "http"

    def run(self):
        url = self.config["url"]
        with request.urlopen(url, timeout=self.config.get("timeout", 5)) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            yield Event(data={"message": body, "status": resp.status})

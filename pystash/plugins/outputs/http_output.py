from __future__ import annotations

import json
from urllib import request
from pystash.plugins.base import OutputPlugin


class HttpOutput(OutputPlugin):
    plugin_name = "http"

    def send(self, events):
        url = self.config["url"]
        for event in events:
            data = json.dumps(event.data, default=str).encode("utf-8")
            req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with request.urlopen(req, timeout=self.config.get("timeout", 5)):
                pass

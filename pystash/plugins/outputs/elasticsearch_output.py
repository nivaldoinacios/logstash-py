from __future__ import annotations

import json
from urllib import request
from pystash.plugins.base import OutputPlugin


class ElasticsearchOutput(OutputPlugin):
    plugin_name = "elasticsearch"

    def send(self, events):
        endpoint = self.config.get("url", "http://localhost:9200")
        index = self.config.get("index", "pystash")
        bulk_lines = []
        for event in events:
            bulk_lines.append(json.dumps({"index": {"_index": index}}))
            bulk_lines.append(json.dumps(event.data, default=str))
        payload = ("\n".join(bulk_lines) + "\n").encode("utf-8")
        req = request.Request(
            f"{endpoint}/_bulk",
            data=payload,
            headers={"Content-Type": "application/x-ndjson"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.config.get("timeout", 5)):
            pass

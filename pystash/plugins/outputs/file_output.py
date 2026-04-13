from __future__ import annotations

import json
from pathlib import Path
from pystash.plugins.base import OutputPlugin


class FileOutput(OutputPlugin):
    plugin_name = "file"

    def __init__(self, config, context):
        super().__init__(config, context)
        self.path = Path(config["path"])
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def send(self, events):
        with self.path.open("a", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event.data, default=str) + "\n")

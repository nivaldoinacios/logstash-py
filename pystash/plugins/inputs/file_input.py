from __future__ import annotations

from pathlib import Path
from pystash.core.event import Event
from pystash.plugins.base import InputPlugin


class FileInput(InputPlugin):
    plugin_name = "file"

    def run(self):
        path = Path(self.config["path"])
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                yield Event(data={"message": line.rstrip("\n")})

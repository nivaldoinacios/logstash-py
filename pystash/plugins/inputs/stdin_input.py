from __future__ import annotations

from pystash.core.event import Event
from pystash.plugins.base import InputPlugin


class StdinInput(InputPlugin):
    plugin_name = "stdin"

    def run(self):
        for line in iter(input, ""):
            yield Event(data={"message": line.rstrip("\n")})

from __future__ import annotations

import json
from pystash.plugins.base import OutputPlugin


class StdoutOutput(OutputPlugin):
    plugin_name = "stdout"

    def send(self, events):
        for event in events:
            print(json.dumps(event.data, default=str))

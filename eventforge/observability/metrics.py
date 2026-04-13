from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, start_http_server


class Metrics:
    def __init__(self) -> None:
        self.events_in = Counter("eventforge_events_in_total", "Events in", ["pipeline"])
        self.events_out = Counter("eventforge_events_out_total", "Events out", ["pipeline"])
        self.events_dropped = Counter("eventforge_events_dropped_total", "Dropped events", ["pipeline"])
        self.plugin_errors = Counter("eventforge_plugin_errors_total", "Plugin errors", ["pipeline", "plugin", "type"])
        self.plugin_time = Histogram("eventforge_plugin_duration_seconds", "Plugin execution time", ["pipeline", "plugin", "type"])
        self.batch_size = Histogram("eventforge_batch_size", "Batch sizes", ["pipeline"])
        self.queue_depth = Gauge("eventforge_queue_depth", "Queue depth", ["pipeline"])
        self.reload_status = Gauge("eventforge_reload_status", "Reload success=1 failure=0", ["pipeline"])
        self.worker_alive = Gauge("eventforge_worker_alive", "Worker liveness", ["pipeline", "worker"])

    @staticmethod
    def start_metrics_server(port: int) -> None:
        start_http_server(port)

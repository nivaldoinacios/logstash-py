from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

from eventforge.config.ast import PipelineSpec, PluginSpec
from eventforge.core.event import Event
from eventforge.queue.memory import MemoryEventQueue
from eventforge.runtime.conditionals import evaluate


@dataclass
class RuntimePlugin:
    spec: PluginSpec
    instance: object
    condition: str | None


class PipelineRuntime:
    def __init__(self, spec: PipelineSpec, registry, metrics, queue_size: int = 10000):
        self.spec = spec
        self.registry = registry
        self.metrics = metrics
        self.queue = MemoryEventQueue(maxsize=queue_size)
        self._stop = threading.Event()
        self._inputs_done = threading.Event()
        self._input_threads: list[threading.Thread] = []
        self._worker_threads: list[threading.Thread] = []
        self._logger = logging.getLogger(f"eventforge.pipeline.{spec.pipeline_id}")
        self.inputs = self._build_plugins("input")
        self.filters = self._build_plugins("filter")
        self.outputs = self._build_plugins("output")

    def _build_plugins(self, plugin_type: str) -> list[RuntimePlugin]:
        result: list[RuntimePlugin] = []
        for spec in self.spec.plugins.get(plugin_type, []):
            config = dict(spec.config)
            condition = config.pop("when", None)
            instance = self.registry.create(plugin_type, spec.name, config)
            result.append(RuntimePlugin(spec=spec, instance=instance, condition=condition))
        return result

    def start(self) -> None:
        for plugin in [*self.inputs, *self.filters, *self.outputs]:
            plugin.instance.start()

        for runtime_input in self.inputs:
            thread = threading.Thread(target=self._run_input, args=(runtime_input,), daemon=True)
            thread.start()
            self._input_threads.append(thread)

        for idx in range(self.spec.workers):
            thread = threading.Thread(target=self._worker_loop, args=(idx,), daemon=True)
            thread.start()
            self._worker_threads.append(thread)

        monitor = threading.Thread(target=self._monitor_inputs, daemon=True)
        monitor.start()

    def _monitor_inputs(self) -> None:
        for thread in self._input_threads:
            thread.join()
        self._inputs_done.set()

    def _run_input(self, runtime_input: RuntimePlugin) -> None:
        label = dict(pipeline=self.spec.pipeline_id, plugin=runtime_input.spec.name, type="input")
        try:
            with self.metrics.plugin_time.labels(**label).time():
                runtime_input.instance.run(self._emit)
        except Exception:
            self.metrics.plugin_errors.labels(**label).inc()
            self._logger.exception("input plugin failed", extra=label)

    def _emit(self, event: Event) -> None:
        if self.queue.put(event):
            self.metrics.events_in.labels(self.spec.pipeline_id).inc()
        else:
            self.metrics.events_dropped.labels(self.spec.pipeline_id).inc()

    def _worker_loop(self, worker_id: int) -> None:
        alive_gauge = self.metrics.worker_alive.labels(self.spec.pipeline_id, str(worker_id))
        alive_gauge.set(1)
        while not self._stop.is_set():
            self.metrics.queue_depth.labels(self.spec.pipeline_id).set(self.queue.size)
            batch = self.queue.get_batch(self.spec.batch_size, timeout=0.5)
            if not batch:
                if self._inputs_done.is_set() and self.queue.size == 0:
                    break
                continue
            self.metrics.batch_size.labels(self.spec.pipeline_id).observe(len(batch))
            filtered = self._run_filters(batch)
            self._run_outputs(filtered)
            self.metrics.events_out.labels(self.spec.pipeline_id).inc(len(filtered))
        alive_gauge.set(0)

    def _run_filters(self, events: list[Event]) -> list[Event]:
        current = events
        for runtime_filter in self.filters:
            next_events: list[Event] = []
            label = dict(pipeline=self.spec.pipeline_id, plugin=runtime_filter.spec.name, type="filter")
            for event in current:
                if not evaluate(runtime_filter.condition, event):
                    next_events.append(event)
                    continue
                try:
                    with self.metrics.plugin_time.labels(**label).time():
                        next_events.extend(runtime_filter.instance.process(event))
                except Exception as exc:
                    event.mark_error(str(exc))
                    self.metrics.plugin_errors.labels(**label).inc()
                    self._logger.exception("filter plugin failed", extra=label)
                    next_events.append(event)
            current = next_events
            if not current:
                break
        return current

    def _run_outputs(self, events: list[Event]) -> None:
        for runtime_output in self.outputs:
            selected = [event for event in events if evaluate(runtime_output.condition, event)]
            if not selected:
                continue
            label = dict(pipeline=self.spec.pipeline_id, plugin=runtime_output.spec.name, type="output")
            try:
                with self.metrics.plugin_time.labels(**label).time():
                    runtime_output.instance.emit(selected)
            except Exception:
                self.metrics.plugin_errors.labels(**label).inc()
                self._logger.exception("output plugin failed", extra=label)
                for event in selected:
                    event.add_tag("_output_failure")

    def wait(self, timeout: float | None = None) -> None:
        start = time.monotonic()
        for thread in self._worker_threads:
            remaining = None if timeout is None else max(0.0, timeout - (time.monotonic() - start))
            thread.join(remaining)

    def stop(self) -> None:
        self._stop.set()
        for plugin in self.inputs:
            plugin.instance.stop()
        for plugin in self.outputs:
            plugin.instance.flush()
            plugin.instance.stop()
        for plugin in self.filters:
            plugin.instance.stop()

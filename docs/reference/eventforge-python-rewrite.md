---
mapped_pages: []
---

# Eventforge (Python rewrite bootstrap)

This repository now includes a bootstrap implementation of **Eventforge**, a Logstash-inspired Python engine.

## Included in this first slice

- CLI commands: `run`, `validate`, `explain`, `plugins`
- Config parser:
  - YAML multipipeline format (`pipelines:`)
  - Logstash-like DSL subset (`input/filter/output`)
- Event model with nested field references (`[a][b][c]`)
- Worker runtime with in-memory bounded queue
- Built-in plugin registry + SDK contracts
- Inputs: `stdin`, `file`, `http`
- Filters: `mutate`, `json`, `grok`, `date`, `drop`
- Outputs: `stdout`, `file`, `http`, `elasticsearch` (bulk)
- Observability endpoints:
  - `/metrics` (Prometheus, default port 9600)
  - `/health`, `/ready`, `/live` (default port 9601)

## Quickstart

```bash
python3 -m pip install -e .[dev]
python3 -m eventforge validate -c /home/runner/work/logstash-py/logstash-py/examples/eventforge/http_json_route.yml
python3 -m eventforge run -c /home/runner/work/logstash-py/logstash-py/examples/eventforge/http_json_route.yml
```

Then send data:

```bash
curl -X POST http://127.0.0.1:8088/ingest -H 'content-type: application/json' -d '{"service":"api","msg":"ok"}'
```

## Known gaps in this first slice

- Persistent queue and DLQ are not implemented yet.
- DSL subset parser is intentionally limited.
- Grok implementation supports a limited built-in pattern set.
- No hot-reload yet.

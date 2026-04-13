# PyStash (bootstrap)

Initial functional bootstrap of a Logstash-inspired Python pipeline engine.

## Features in this slice

- CLI: `pystash run`, `pystash validate`
- JSON pipeline config loader + validation
- Event model with nested field addressing (`[foo][bar]`)
- Plugin registry + built-in plugins
- Inputs: `stdin`, `file`
- Filters: `mutate`, `json`, `grok`, `date`, `drop`
- Outputs: `stdout`, `file`, `http`, `elasticsearch`

## Example config

```json
{
  "pipelines": [
    {
      "id": "main",
      "input": [{"plugin": "file", "path": "examples/input.log"}],
      "filter": [
        {"plugin": "grok", "pattern": "(?P<level>INFO|ERROR) (?P<msg>.*)", "source": "message"},
        {"plugin": "mutate", "add_field": {"[meta][env]": "dev"}}
      ],
      "output": [{"plugin": "stdout"}]
    }
  ]
}
```

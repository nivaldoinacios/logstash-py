from pathlib import Path

from eventforge.config.parser import load_config, validate_config
from eventforge.runtime.engine import Engine


def test_file_input_to_file_output(tmp_path: Path):
    source = tmp_path / "input.log"
    dest = tmp_path / "output.log"
    source.write_text('{"msg":"HELLO"}\n', encoding="utf-8")

    cfg = tmp_path / "pipeline.yml"
    cfg.write_text(
        f"""
pipelines:
  - id: p1
    workers: 1
    batch_size: 10
    input:
      - file:
          path: "{source}"
          mode: "read"
          codec: "plain"
    filter:
      - json:
          source: "message"
      - mutate:
          lowercase: ["msg"]
    output:
      - file:
          path: "{dest}"
""",
        encoding="utf-8",
    )

    config = load_config(str(cfg))
    validate_config(config)
    engine = Engine(config)
    engine.start()
    engine.wait(timeout=20)
    engine.stop()

    assert dest.exists()
    output = dest.read_text(encoding="utf-8")
    assert "hello" in output

from pathlib import Path

from eventforge.config.parser import load_config, validate_config


def test_yaml_parser(tmp_path: Path):
    cfg = tmp_path / "pipeline.yml"
    cfg.write_text(
        """
pipelines:
  - id: test
    input:
      - file:
          path: "/tmp/in.log"
          mode: "read"
    output:
      - stdout: {}
""",
        encoding="utf-8",
    )
    config = load_config(str(cfg))
    validate_config(config)
    assert len(config.pipelines) == 1


def test_dsl_parser(tmp_path: Path):
    cfg = tmp_path / "pipeline.conf"
    cfg.write_text(
        """
input { stdin { } }
filter { mutate { add_tag => [\"x\"] } }
output { stdout { } }
""",
        encoding="utf-8",
    )
    config = load_config(str(cfg))
    validate_config(config)
    assert config.pipelines[0].plugins["input"][0].name == "stdin"

from pathlib import Path

from eventforge.cli import main


def test_cli_validate(tmp_path: Path):
    cfg = tmp_path / "ok.yml"
    cfg.write_text(
        """
pipelines:
  - id: ok
    input:
      - stdin: {}
    output:
      - stdout: {}
""",
        encoding="utf-8",
    )
    code = main(["validate", "-c", str(cfg)])
    assert code == 0

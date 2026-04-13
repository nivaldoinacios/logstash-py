import json
from pathlib import Path

from pystash.config.loader import load_config, validate_config


def test_validate_requires_input_output(tmp_path: Path):
    cfg_path = tmp_path / "c.json"
    cfg_path.write_text(json.dumps({"pipelines": [{"id": "p1"}]}), encoding="utf-8")
    cfg = load_config(str(cfg_path))
    errs = validate_config(cfg)
    assert any("input is required" in e for e in errs)
    assert any("output is required" in e for e in errs)

from __future__ import annotations

import argparse
import json

from eventforge.config import load_config, validate_config
from eventforge.runtime import Engine, EngineOptions


def cmd_validate(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    validate_config(config)
    print(f"OK: {len(config.pipelines)} pipeline(s) validated")
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    validate_config(config)
    data = {
        "pipelines": [
            {
                "id": pipeline.pipeline_id,
                "workers": pipeline.workers,
                "batch_size": pipeline.batch_size,
                "queue": pipeline.queue_type,
                "inputs": [p.name for p in pipeline.plugins.get("input", [])],
                "filters": [p.name for p in pipeline.plugins.get("filter", [])],
                "outputs": [p.name for p in pipeline.plugins.get("output", [])],
            }
            for pipeline in config.pipelines
        ]
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def cmd_plugins(args: argparse.Namespace) -> int:
    from eventforge.plugins.builtin import register_builtin_plugins
    from eventforge.plugins.registry import PluginRegistry

    registry = PluginRegistry()
    register_builtin_plugins(registry)
    listing = registry.list_plugins()
    if args.output == "json":
        print(json.dumps(listing, indent=2, ensure_ascii=False))
    else:
        for ptype, names in listing.items():
            print(f"[{ptype}]")
            for name in names:
                print(f"  - {name}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    validate_config(config)
    engine = Engine(
        config,
        options=EngineOptions(metrics_port=args.metrics_port, health_port=args.health_port),
    )
    try:
        engine.run()
    finally:
        engine.stop()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eventforge", description="Logstash-inspired event pipeline engine")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Run pipelines")
    run_cmd.add_argument("-c", "--config", required=True, help="Config path (.yml/.yaml/.conf)")
    run_cmd.add_argument("--metrics-port", type=int, default=9600)
    run_cmd.add_argument("--health-port", type=int, default=9601)
    run_cmd.set_defaults(func=cmd_run)

    validate_cmd = sub.add_parser("validate", help="Validate config")
    validate_cmd.add_argument("-c", "--config", required=True)
    validate_cmd.set_defaults(func=cmd_validate)

    explain_cmd = sub.add_parser("explain", help="Explain compiled plan")
    explain_cmd.add_argument("-c", "--config", required=True)
    explain_cmd.set_defaults(func=cmd_explain)

    plugins_cmd = sub.add_parser("plugins", help="List plugins")
    plugins_cmd.add_argument("--output", choices=["text", "json"], default="text")
    plugins_cmd.set_defaults(func=cmd_plugins)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

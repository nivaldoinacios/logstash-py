from __future__ import annotations

import argparse
from pystash import __version__
from pystash.config.loader import load_config, validate_config
from pystash.runtime.engine import Engine
import pystash.plugins.builtin  # noqa: F401


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    errors = validate_config(cfg)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Config OK")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    errors = validate_config(cfg)
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    Engine(cfg).run()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pystash")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run")
    run_p.add_argument("-c", "--config", required=True)
    run_p.set_defaults(func=cmd_run)

    val_p = sub.add_parser("validate")
    val_p.add_argument("-c", "--config", required=True)
    val_p.set_defaults(func=cmd_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

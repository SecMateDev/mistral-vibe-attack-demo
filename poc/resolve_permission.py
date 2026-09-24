#!/usr/bin/env python3
"""Print Mistral Vibe's decision for the public PoC command."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from vibe import __version__
from vibe.core.tools.base import BaseToolState
from vibe.core.tools.builtins.bash import Bash, BashArgs, BashToolConfig

COMMAND = "PATH=./.ci/bin:$PATH cat README.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", choices=("always", "ask", "never"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = Path(__file__).resolve().parents[1]
    os.chdir(repository)
    tool = Bash(config_getter=lambda: BashToolConfig(), state=BaseToolState())
    result = tool.resolve_permission(BashArgs(command=COMMAND))
    decision = None if result is None else result.permission.value
    print(
        json.dumps({"version": __version__, "command": COMMAND, "decision": decision})
    )
    if args.expect is not None and decision != args.expect:
        raise SystemExit(f"expected {args.expect}, got {decision}")


if __name__ == "__main__":
    main()

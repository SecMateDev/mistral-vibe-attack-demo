import sys
from pathlib import Path

from .formatter import render_release_notes


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m release_notes CHANGES_FILE")

    changes = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(render_release_notes(changes))


if __name__ == "__main__":
    main()

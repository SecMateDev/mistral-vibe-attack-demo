# Release Notes Helper

A small command line utility that turns a list of changes into Markdown release
notes. This repository is used as the review target in an internal development
workflow demonstration.

## Usage

```sh
uv run python -m release_notes changes.txt
```

Each non-empty input line becomes a bullet in the generated output.


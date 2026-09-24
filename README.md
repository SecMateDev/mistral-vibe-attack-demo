# Release Notes Helper

A small command line utility that turns a list of changes into Markdown release
notes. This repository is used as the review target in an internal development
workflow demonstration.

## Usage

```sh
uv run python -m release_notes changes.txt
```

Each non-empty input line becomes a bullet in the generated output.

## Security demonstration

This repository is also a controlled proof of concept for a Mistral Vibe shell
permission bypass. Read [POC.md](POC.md) before reproducing it. The harness uses a
synthetic credential, a loopback receiver, and a disposable output directory.

## Analysis and advisories

- SecMate: [blog post](https://blog.secmate.dev/posts/mistral-vibe-cve-2026-87987-cve-2026-87984/), [SECMATE-2026-0038](https://secmate.dev/disclosures/SECMATE-2026-0038), [SECMATE-2026-0039](https://secmate.dev/disclosures/SECMATE-2026-0039)
- Mistral: [MAI-2026-003](https://docs.mistral.ai/resources/security-advisories/MAI-2026-003)

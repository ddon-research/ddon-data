# Tools and shell

The tools a human needs to work in this repository, and which work needs them. It is a summary for people: [`AGENTS.md`](../../AGENTS.md) is canonical for coding agents and holds the shell rules in full. A version is what the research machine had on 2026-11-04.

## By job

| Job | Tool | Version | Used by |
| --- | --- | --- | --- |
| Disassembly | IDA Pro, with the headless `ida` server (ida-mcp) | 9.5 | [Query an IDA database read-only](../how-to/query-ida-read-only.md) |
| Disassembly, archived | Ghidra with PyGhidra, [ddon-ghidra-scripts](https://github.com/ddon-research/ddon-ghidra-scripts) | 11.4 | [Decode a resource format](../how-to/decode-a-resource-format.md#the-archived-alternative-ghidra) |
| PS4 dumps | Orbis SDK `orbis-bin`, LLVM | SDK 12, LLVM 23 | [Regenerate the ELF dumps](../how-to/regenerate-elf-dumps.md) |
| Resource extraction | [ddon-extractor](https://github.com/ddon-research/ddon-extractor), JDK | `e6c358ea`, JDK 25 | [Extract client resources](../how-to/extract-client-resources.md) |
| Patterns | ImHex, CLI `imhex --pl format`; plbatch for the export | 1.38.1; ImHex is not on `PATH` | [Decode a resource format](../how-to/decode-a-resource-format.md), [Build plbatch](../how-to/build-plbatch.md) |
| Packets | Wireshark and `tshark` | 4.6.9 | [Decrypt a capture](../how-to/decrypt-a-capture.md) |
| Packet keys | [ddon_common_key_bruteforce](https://github.com/ddon-research/ddon_common_key_bruteforce), a fork of [the original](https://github.com/Andoryuuta/ddon_common_key_bruteforce) | | [Decrypt a capture](../how-to/decrypt-a-capture.md) |
| Packet annotation | `Arrowgene.Ddon.Cli` of the [server emulator](https://github.com/sebastian-heinz/Arrowgene.DragonsDogmaOnline), patched | | [Patch the Arrowgene CLI](../how-to/patch-the-arrowgene-cli.md) |
| Patching | radare2 | 6.1.0 | [Apply a client patch](../how-to/apply-a-client-patch.md) |
| Class recovery | Pharos OOAnalyzer in Docker | Docker 29.9.2 | [Run Pharos](../how-to/run-pharos.md) |
| Documentation check | `markdown-it-py` through `uv` | 4.2.0 | [Write documentation](../how-to/write-documentation.md) |

## Shell

The shell is Git Bash; WSL `Ubuntu` 26.04 serves Linux-only tooling. Automation is bash, not PowerShell. Scripts start with `set -o errexit -o nounset -o pipefail` and check their commands with `command -v`.

| Instead of | Use | Version |
| --- | --- | --- |
| `grep` | `rg`, or `git grep -n` for tracked files | ripgrep 15.2.0 |
| `find` | `fd`; add `-H -I` for ignored files | 10.5.0 |
| `sed -i`, which strips CRs | `sd -F` | 1.0.0 |
| `du` | `dust` | 1.2.7 |

Also on `PATH`: `jq` 1.8.2, `zstd` 1.5.7, `xxd`, `uv` 0.13.7, `gh` 2.103.3, `git` 2.56.0. `rsync` is missing from Git Bash: use `/c/msys64/usr/bin/rsync` or WSL.

| Rule | Why |
| --- | --- |
| Never list or diff `client/` or the packet data unbounded: use `git diff --stat -- <subdir>`, `rg -c`, `fd -d 2`, `dust` | they hold hundreds of thousands of files |
| Git Bash paths are `/d/ddon-data/...`, native programs take `D:/...`, WSL sees `/mnt/d/...` | set `MSYS_NO_PATHCONV=1` when passing a `/`-prefixed argument to a native program |
| Keep output trees short | native Windows programs (ImHex, the Arrowgene CLI) fail on paths of 260 characters or more |
| Each Python project uses its own `uv` environment and CPython 3.14: `uv run` in the project; ad-hoc scripts as `python -X utf8 -I <script>` | the root `.venv` is a legacy stub; `research/03040008/flags/` has `.venv-cpython314` |
| Commits are SSH-signed; never bypass it | [`AGENTS.md`](../../AGENTS.md) holds the rest of the commit rules |

## Agents and planning

Coding agents follow [`AGENTS.md`](../../AGENTS.md); `CLAUDE.md` imports it for Claude Code. Feature work is planned with [GitHub Spec Kit](https://github.com/github/spec-kit) 1.1.3: repository-wide features in `specs/`, the knowledge graph in `research/knowledge-graph/specs/`. The gate agents and people share is on [Gate and hooks](gate-and-hooks.md).

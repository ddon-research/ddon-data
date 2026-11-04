"""009 T007: move the text that moves whole out of the client READMEs, from the base commit, onto its pages.

    python -X utf8 -I specs/009-docs-structure/research/T007-split.py <base sha>

Reads three files at <base> with `git show` and rewrites four pages, so a rerun gives the same bytes. It moves:
the hash tables of patches/README.md; the mechanism table and the crash protocol of protections/README.md; section 4
of the ELF README (AsciiDoc to Markdown). The prose around them is in this script.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BASE = sys.argv[1]
REPORTS = {"R1": "R1-online.md", "R2": "R2-static.md", "R3": "R3-patches.md"}


def show(path):
    out = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=REPO, capture_output=True, check=True).stdout
    return out.decode("utf-8").replace("\r\n", "\n").split("\n")


def between(lines, first, last):
    """Lines first..last, numbered from 1, inclusive."""
    return "\n".join(lines[first - 1:last])


def reports(text):
    """`R3 §2.1` or `R3 §1, §7` becomes the report's file name in a code span, which the wording gate accepts."""
    return re.sub(r"\b(R[123]) §", lambda m: f"`{REPORTS[m.group(1)]}` §", text)


def write(path, text):
    (REPO / path).write_bytes(text.encode("utf-8"))
    print(path, len(text.splitlines()), "lines")


# --- docs/reference/client-patches.md -------------------------------------------------------------------------------

pat = show("patches/README.md")
assert pat[64] == "## Vanilla Client Hashes" and pat[75] == "## Modded Client Hashes"


def r2_spans(text):
    return re.sub(r"(?<![`\w/])(patches/[\w.-]+\.r2)", r"`\1`", text)


client_patches = f"""# Client patches

The hash chain of the Windows client executables, for anyone who must tell which executable they hold or which layer sits on which. It lists every recorded executable by SHA-256, the lineage between them, the file offsets of the dumps and the encoding of the `.r2` and `.json` files. To use a layer, see [Apply a client patch](../how-to/apply-a-client-patch.md); to record one, [Add a client patch layer](../how-to/add-a-client-patch-layer.md). Why the client looks like this: [Client lineage and protections](../explanation/client-lineage-and-protections.md).

Executables are named by the start of their hash (`f1c9`, `f2a8`). Every executable of the tables below is PC build 03040008 unless its row says otherwise. Lineage and per-layer sites were measured by a byte diff in `research/03040008/protections/R3-patches.md` §1 and §2.

{between(pat, 65, 74)}

## Patched executables

All binary diffs are `.r2` scripts with a `.json` beside them. Each row gives the hash a layer starts from and the hash it must produce.

### 2020–2022

{r2_spans(between(pat, 80, 91))}

### 2025

{r2_spans(between(pat, 95, 103))}

### 2026

{r2_spans(between(pat, 107, 119))}

### A layer outside the index

`patches/` also holds `2026_10_17_ddo_dump_fix_4.r2` and its `.json`, not tracked at 2026-11-04 (other work):

| Name | Date | Starting Hash | Target Hash | Notes |
|------|------|---------------|-------------|-------|
| 2026_10_17_DDO_DUMP_FIX_4.exe | 2026-10-17 | `f1c974d0e529d4bb7dc5f0953d37eea6bbb023f2667f9a1d3a3b878f4919fa20` | `d38412ca6443540f1b22e766749f11b59e4239a6a43d4dbec55e85f2fa1cde84` | 33 bytes: the three checksum compares `0x24CD5DE`, `0x3A87F64`, `0x430DF3B` with the bytes of `1c8c`, and four `call [IsDebuggerPresent]` sites `0xBEEA24`, `0x19A7F4E`, `0x19AE2F1`, `0x19C1429` as `xor eax,eax` plus nops. Its `.json` adds `sites` and `validation`: in its three smoke runs on 2026-10-17 the hooked client still crashed |

## Lineage

An arrow reads "was built from". `f1c9` is `e50d` plus 2 bytes in content, though its `.r2` replays from the Mutex build `9c95`; `f2a8` descends from `ef9d` alone (`research/03040008/protections/R3-patches.md` §1).

```text
01dc41a9 vanilla (packed) -> 0a7c plain dump -> ef9d FIX2 -> e50d FIX_3 -> f1c9 DUMP_FIX (= FIX_3 + 2 B)
                                                  |                          |-> ChatEdit, ChatEdit_4GB
                                                  |                          |-> Bunie 3-in-1 (= 100FPS), 5-in-1
                                                  |                          `-> PerfPatch v1=v2=v3 exe (ac83) -> v7 (0306)
                                                  `-> 1c8c Win7 dump (filmmachine_, IAT rebuild) -> f2a8 installed DDO.exe
```

| Layer | What it changes, by the publishers' lists |
| --- | --- |
| 2020–2022 | unpacked dump; CRC checks disabled; unlimited instances |
| 2025 | chatbox limit from 30 to 127 characters; application allowed 4 GB of RAM (the row of `bf51` says what that write does) |
| 2026 | up to 100 FPS in Borderless Windowed mode; shout message cooldown from 10 s to 5 s; hidden chat cooldown from 1 s to 0 s |

## File offsets of the dumps

Every dump-sized executable (68,231,680 bytes) has this section table, from `research/03040008/protections/R3-patches.md`. A `.r2` writes at file offsets; IDA and the pages give virtual addresses (VA).

| Section | VA range | File offset of VA start | VA = |
| --- | --- | --- | --- |
| header | `0x400000`–`0x4003FF` | `0x0` | off + `0x400000` |
| `.text` (game, first) | `0x401000`–`0x1AD4FFF` | `0x400` | off + `0x400C00` |
| `.rdata` | `0x1AD5000`– | `0x16D4000` | off + `0x401000` |
| `.data` | `0x2113000`– | `0x1D11A00` | off + `0x401600` |
| `.rsrc` | `0x220F000`– | `0x1D7BE00` | |
| `.reloc` (holds the IAT at `0x2233xxx` and protector code) | `0x2231000`–`0x240EFFF` | `0x1D9DC00` | off + `0x493400` |
| `.text#2` (captured SecureEngine image) | `0x240F000`–`0x45A3FFF` | `0x1F7B200` | off + `0x493E00` |
| `.SCY` (Scylla IAT store) | `0x45A4000`– | `0x410FE00` | |

## The `.r2` and `.json` files

| File | Form | Encoding |
| --- | --- | --- |
| `<layer>.r2` | a radare2 script of `wx <hex> @ <file offset>` commands, written by [`radiff2 -r`](https://book.rada.re/tools/radiff2/intro.html) | 10 of the 12 tracked are UTF-16LE with a BOM and CRLF; `rootofallthings_chat_edit.r2` and `bunie_5_in_1.r2` are UTF-8. radare2 6.1.0 runs only the UTF-8 ones: on a UTF-16 script it prints `Invalid command` and writes nothing ([what to do](../how-to/apply-a-client-patch.md#steps)), and `rg` and `sd` see NUL bytes in it. |
| `<layer>.json` | [`radiff2 -j`](https://book.rada.re/tools/radiff2/datadiff.html): `files`, two objects of `filename`, `size`, `sha256`, the parent first; `changes`, objects of `addr` (decimal file offset), `from`, `to` (hex bytes) | all 12 tracked are UTF-16LE with a BOM |

The `filename` values are the publisher's or the lab's names, so they differ from the Name column for several rows. All 12 tracked `.r2` files replay to their stated target hashes in an in-memory replay ([Status](status.md#client-patches)). The `.json` hashes of those 12 equal the two hash columns above ([Status](status.md#client-patches)).
"""
write("docs/reference/client-patches.md", client_patches)

# --- docs/reference/protection-inventory.md -------------------------------------------------------------------------

prot = show("research/03040008/protections/README.md")
assert prot[44] == "## 2. Protection inventory" and prot[123] == "## 5. Crash-triage protocol"
table = between(prot, 47, 63)
peb = "| PEB `BeingDebugged` reads `fs:[30h]` | 23 sites in `.text#2` (list in R3 §6) | live | live | R2 §3 |"
assert peb in table
table = table.replace(peb, "| PEB reads `fs:[30h]`, then `[eax+0Ch]` (`PEB.Ldr`) | 23 sites in `.text#2`: [listed below](#the-23-peb-reads) | live | live | below |")
table = reports(table)

inventory = f"""# Protection inventory

The mechanisms still present in the PC 03040008 dumps and what each layer did to them, for anyone classifying a fault or choosing a layer. Addresses are virtual addresses in the `f1c9` database (image base `0x400000`, no relocations). You need the executables' names from [Client patches](client-patches.md). Why they are there: [Client lineage and protections](../explanation/client-lineage-and-protections.md). "[inference]" marks a conclusion, as in the reports. The evidence is in `research/03040008/protections/`: `R2-static.md` and `R3-patches.md`, with `R1-online.md` for the outside sources.

## Mechanisms

`f1c9` is the DUMP_FIX executable, `f2a8` the installed `DDO.exe`.

{table}

{reports(between(prot, 64, 65))}

## Other sites no layer touches

From `R3-patches.md` §6, each checked against every diff run of every layer.

| Protection | Location | Touched by | Note |
| --- | --- | --- | --- |
| Padding descriptors in the style of FIX and FIX_3 | other `… c3 [len] 00 00 00 …` blocks next to DTI getters, read by engine code (pattern of `0x738B66`, `0x738B7A`) | only two zeroed (FIX), two set to -1 (FIX_3, unconfirmed) | **not run**: a scan for more such blocks |
| Mutation dispatch and cross-segment edges | ~32.6k `lea esp,[esp+4]; jmp [esp-4]`; ~16k `E8`/`E9` into `.text#2` | only the 9 macro-entry skips (FIX2) and the runtime patch at `0xF09655` (v3, v7 with `Debugging=1`) | the engine stays reachable everywhere |
| Game `IsDebuggerPresent` call | `0xBEEA24`, in `sub_BEEA00` | the layer FIX_4 alone (`2026_10_17_ddo_dump_fix_4.json`) | the CRT's three calls are at `0x19A7F4E`, `0x19AE2F1`, `0x19C1429` |

## The 23 PEB reads

`0x246A13B`, `0x24A1000`, `0x24BF352`, `0x24C9D83`, `0x24CEB5C`, `0x24D0150`, `0x2527530`, `0x2F487A4`, `0x33CF678`, `0x33D9701`, `0x350E390`, `0x35125C5`, `0x3645E41`, `0x3A8644F`, `0x3B1667C`, `0x3C06CA0`, `0x3C0714F`, `0x3D2C8AA`, `0x40861F3`, `0x4092D1E`, `0x412C3EF`, `0x41B6891`, `0x4225011`.

Each is `64 A1 30 00 00 00` (`mov eax,fs:[30h]`) followed by `8B 40 0C` (`mov eax,[eax+0Ch]`), directly at 20 sites and after one `jmp` at `0x3A8644F`, `0x3B1667C`, `0x3C06CA0`: read from the bytes of `f1c9` on 2026-11-04. So they read `PEB.Ldr`, the module list, and not `PEB.BeingDebugged` at `PEB+2`. `R2-static.md` §3 and `R3-patches.md` §6 call them `BeingDebugged` reads, and ddon-hook's spec 009 records the same correction. Patching them out would break the engine's import resolution [inference].
"""
write("docs/reference/protection-inventory.md", inventory)

# --- docs/how-to/triage-a-client-crash.md ---------------------------------------------------------------------------

protocol = "\n".join(prot[128:151])
for old, new in (
    ("map it to §2's table", "map it to the [protection inventory](../reference/protection-inventory.md)"),
    ("neutralises", "neutralizes"),
    ("findings about the\n   client come back here as rows in §2", "findings about the\n   client come back as rows of the [protection inventory](../reference/protection-inventory.md)"),
):
    assert old in protocol, old
    protocol = protocol.replace(old, new)
protocol = reports(protocol)

triage = f"""# Triage a client crash

This page is for anyone whose PC 03040008 client died under a hook or an automated run and who must find the cause rather than guess at it. You capture the crash, classify the faulting address, find the writer and record the result in a ledger. Every crash gets a root cause and, where it is a trap, a patch. You need a client you may run: the client runs only from ddon-hook, against the local Arrowgene server, whose own triage page secures a run's evidence first. Background: [Client lineage and protections](../explanation/client-lineage-and-protections.md).

## The protocol

Addresses are virtual addresses in the `f1c9` database.

{protocol}

ddon-hook's `run_cycles.py` runs step 1's capture as `procdump -ma -e 1 -f C0000005 -n 5 <pid> <dumps folder>` when given `--procdump`, and appends the ledger row to `build\\automation-runs\\crash-ledger.jsonl`. Its logging VEH is the switch `DDON_HOOK_EXCEPTION_LOG=1`.

You are done with a crash when its ledger row has `class`, `root_cause` and `verified`. A crash without them stays open.

## When a hook writes `.text`

Any inline patch of `.text` draws the protector's integrity reaction ([why](../explanation/client-lineage-and-protections.md#why-a-code-patch-crashes-the-client)). Take these in order of cost; each has a stop rule.

1. **Base on `f1c9`, never `f2a8`,** for hooked runs: `f2a8` lacks FIX_3's 122 stubs. Pass it to the run with `--exe`.
2. **Tell the kinds of cause apart,** one run each, more samples where needed, since crash times are random:
   - Unhook after 10 s. If the client survives past 60 s, the crash is a reaction to the live patch, not the hook's code.
   - Build the same hook with MinHook. If only SafetyHook crashes, it is the library.
   - A no-op hook that only calls the original. If that still crashes, the cause is the patch itself, not timing or added work.
3. **Try the layer FIX_4 on `f1c9`** if the checksum compares are in question. **Status:** implemented, not tracked at 2026-11-04: `2026_10_17_ddo_dump_fix_4.r2`, recorded in [Client patches](../reference/client-patches.md#a-layer-outside-the-index). It stubs `0x24CD5DE`, `0x3A87F64` and `0x430DF3B` with the bytes of `1c8c`, and in its smoke runs of 2026-10-17 the hooked client still crashed, so it does not stop this crash on its own.
4. **Answer the anti-debug probes in the proxy,** as Bunie and ScyllaHide do (`R1-online.md` §4, `R3-patches.md` §4): fake `NtQueryInformationProcess` for the own process. Needed only when a debugger or TTD is attached. Do not copy Bunie's `NtSetContextThread` mask bug ([what it is](../explanation/client-lineage-and-protections.md#what-bunies-dlls-add)).
5. **Use a hook that does not write `.text`,** when the patch itself is what trips the check:
   - hardware breakpoints in `DR0`–`DR3` with a VEH (PolyHook2 has both kinds), which needs the `NtSetContextThread` fix above. ddon-hook's data watch is this kind, and the protector holds the debug registers of the main thread;
   - a read-only sampler of the data, with no hook at all, which ddon-hook's RNG work ended on;
   - a PAGE_GUARD VEH hook;
   - hooking the callers' data (vtables, function pointers) where one exists. `nrand` is called directly from hundreds of sites, so that does not apply to it.
6. **Only if 2–5 fail: find and disable the scheduler of the integrity jobs.** The TERA precedent did this: scan for the VM trampolines (`pushfq` sequences) and remove the job that writes the corrupting pointer (`R1-online.md` §6). It needs TTD to find the write.
"""
write("docs/how-to/triage-a-client-crash.md", triage)

# --- docs/explanation/ps4-elf.md ------------------------------------------------------------------------------------

elf = show("binaries/PS4_02020005/elf-dumps/README.adoc")
start = elf.index("== 4. Structure of the binary")
inline = elf.index("=== Inline chains")
ida = elf.index("=== IDA's jump tables and no-return functions")
code = elf.index("=== Code")
end = elf.index("== 5. Notes on other tools")


def adoc_to_md(lines):
    out, table, cols = [], None, 0
    for line in lines:
        if line.startswith("[cols="):
            continue
        if line == "|===":
            if table is None:
                table, cols = [], 3
            else:
                head, rows = table[0], table[1:]
                out.append("| " + " | ".join(head) + " |")
                out.append("| " + " | ".join(["---"] * len(head)) + " |")
                out.extend("| " + " | ".join(r) + " |" for r in rows)
                table = None
            continue
        if table is not None:
            table.append([c.strip() for c in line.lstrip("|").split("|")])
            continue
        if line.startswith("=== "):
            out.append("## " + line[4:])
            continue
        match = re.match(r"^(\*{1,2}) (.*)$", line)
        if match:
            line = ("  " if len(match.group(1)) == 2 else "") + "- " + match.group(2)
        line = re.sub(r"(?<![*\w`])\*([^*\n]+?)\*(?![*\w])", r"**\1**", line)
        out.append(line)
    return "\n".join(out).replace("≥", ">=")


body = adoc_to_md(elf[start + 2:inline]) + "\n\n" + adoc_to_md(elf[code:end])
old = ("The\n  archived comparison's \"resolves all 648\" overstates this (found by the reconstructor's\n  inventory, 2026-10-17).")
assert old in body
body = body.replace(old, "The\n  comparison in `archive/` says \"resolves all 648\", which overstates this (the reconstructor's\n  inventory, 2026-10-17).")

ps4_elf = f"""# Structure of the PS4 ELF

What is unusual about `DDOORBIS.elf`, the PS4 client executable of build PS4_02020005, and what a reader of its dumps has to expect from it. It is for a reverse engineer who knows ELF and DWARF and is about to read this binary, or a tool's output on it. You need nothing first; the input's hash and the files per category are in [the dump set's README](../../binaries/PS4_02020005/elf-dumps/README.adoc), and the formats of the dumps in [ELF dumps](../reference/elf-dumps.md). The numbers describe that one fixed input, SHA-256 `4236f598acc8f15893181455ed195e39dfa4dbfda4eeda8b56fcbd82312c63c0`.

{body}

## Why inlined chains come from one address per run

`orbis-addr2line` (binutils 2.22) answers an address according to the addresses that share its run, since a run keeps the compile units it has read and up to 1,014 of them claim one range. An address run alone gets the answer that depends on the address only. On 30,904 addresses of the reconstructor's measurement, 77 answers differ from batches of 256, 75 of them with more frames. So the file of chains pays one process per address, about 2 h 40 min at 16 jobs, and is then read instead of run ([format](../reference/elf-dumps.md#inline-chains)).

## Why IDA's analysis only corroborates

IDA's jump tables and no-return functions are a second opinion on the reconstructor's analysis of every body. The comparison reports counters that gate nothing: DWARF and the bytes decide, and IDA's function boundaries are its own conventions.
"""
write("docs/explanation/ps4-elf.md", ps4_elf)

# --- binaries/PS4_02020005/elf-dumps/README.adoc: § 1, § 3, § 5 and § 7 stay; the others keep their numbers ---------

DOCS = "../../../docs"
sec2, sec3, sec4, sec5, sec6, sec7 = (elf.index(h) for h in (
    "== 2. Production", "== 3. Contents", "== 4. Structure of the binary", "== 5. Notes on other tools",
    "== 6. Verification", "== 7. Use and regeneration"))
contents = "\n".join(elf[sec3:sec4])
for old, new in (
    ("the reconstructor's `tools/ida/export.py`", "the reconstructor's `ddon-dwarf-reconstructor-rust/tools/ida/export.py`"),
    ("see _Inline chains_ below", f"see link:{DOCS}/reference/elf-dumps.md#inline-chains[Inline chains]"),
    ("see _IDA's jump tables and no-return functions_ below", f"see link:{DOCS}/reference/elf-dumps.md#ida-export[IDA export]"),
):
    assert old in contents, old
    contents = contents.replace(old, new)
readme = "\n".join(elf[:sec2]) + f"""
== 2. Production

`generate-elf-dumps.sh` writes the set: the tools, procedure and exit status are in link:{DOCS}/how-to/regenerate-elf-dumps.md[Regenerate the ELF dumps], provenance and storage in link:{DOCS}/reference/elf-dumps.md[ELF dumps].

""" + contents + f"""
== 4. Structure of the binary

What is unusual about this binary, section by section: link:{DOCS}/explanation/ps4-elf.md[Structure of the PS4 ELF].

""" + "\n".join(elf[sec5:sec6]) + f"""
== 6. Verification

Spot checks, reproducibility, integrity and the input guard: link:{DOCS}/reference/elf-dumps.md#verification[ELF dumps].

""" + "\n".join(elf[sec7:])
write("binaries/PS4_02020005/elf-dumps/README.adoc", readme)

"""Function facts the matcher reads from the T004 dumps (PC 03040008 IDA, PS4 02020005 IDA + DWARF).

Every loader checks the dump's sha256 against ``dumps/MANIFEST.tsv`` before parsing (fail closed).
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

INDIRECT = None  # call target of an indirect call


@dataclass(frozen=True)
class Call:
    site: int
    target: int | None  # None: indirect
    pushed_bytes: int | None = None  # PC only


@dataclass
class Func:
    va: int
    name: str
    side: str  # "pc" | "ps4"
    size: int
    instructions: int
    calls: list[Call]
    strings: frozenset[str] = frozenset()
    constants: frozenset[int] = frozenset()
    data_refs: frozenset[int] = frozenset()
    callers_count: int = 0
    caller_sites: int = 0
    ecx_read_before_write: bool | None = None  # PC only
    ret_imm: tuple[int, ...] = ()
    default_name: bool = True


@dataclass(frozen=True)
class Param:
    name: str
    type: str
    type_die: int | None
    artificial: bool = False


@dataclass(frozen=True)
class DwarfType:
    die: int
    tag: str
    name: str
    size: int | None
    target_die: int | None = None
    target: str | None = None


@dataclass
class Facts:
    """Everything the rules read. Built from the dumps or by tests."""

    pc: dict[int, Func]
    ps4: dict[int, Func]
    table_callbacks: set[int]  # PC handler-table callbacks (non-null)
    table_group: dict[int, int]  # callback -> table group
    # OnPacket_ strings also referenced from outside any function
    onpacket_orphan_strings: set[str] = field(default_factory=set)
    missing_roots: set[int] = field(default_factory=set)
    dwarf_params: dict[int, list[Param]] = field(default_factory=dict)  # PS4 va -> params (only functions with DWARF)
    dwarf_inlines: dict[int, list[int]] = field(default_factory=dict)  # PS4 va -> start VA of each top-level inline
    types: dict[int, DwarfType] = field(default_factory=dict)
    pc_callsites: dict[int, list[Call]] = field(default_factory=dict)  # PC target -> call sites in the dump

    def __post_init__(self) -> None:
        if not self.pc_callsites:
            for f in self.pc.values():
                for c in f.calls:
                    if c.target is not None:
                        self.pc_callsites.setdefault(c.target, []).append(c)


class DumpIdentityError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(dumps: Path) -> dict[str, dict[str, str]]:
    with (dumps / "MANIFEST.tsv").open(encoding="utf-8", newline="") as fh:
        return {r["file"]: r for r in csv.DictReader(fh, delimiter="\t")}


def verify_dump(dumps: Path, name: str, manifest: dict[str, dict[str, str]]) -> dict:
    """Check the file sha256 against MANIFEST.tsv and the header's source sha256; return the header."""
    path = dumps / name
    row = manifest.get(name)
    if row is None:
        raise DumpIdentityError(f"{name}: not in MANIFEST.tsv")
    got = sha256_file(path)
    if got != row["sha256"]:
        raise DumpIdentityError(f"{name}: sha256 {got} != MANIFEST {row['sha256']}")
    with path.open(encoding="utf-8") as fh:
        header = json.loads(fh.readline())
    src = header.get("input_sha256") or header.get("elf_sha256")
    if header.get("kind") != "header" or src != row["source_sha256"]:
        raise DumpIdentityError(f"{name}: header source {src} != MANIFEST {row['source_sha256']}")
    return header


def _iter(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            yield json.loads(line)


def _func(r: dict, side: str) -> Func:
    calls = sorted(
        (Call(c["site"], None if c["target"] == "indirect" else int(c["target"]), c.get("pushed_bytes"))
         for c in r["calls"]),
        key=lambda c: c.site,
    )
    return Func(
        va=r["va"], name=r["name"], side=side, size=r["size"], instructions=r["instructions"], calls=calls,
        strings=frozenset(s["text"] for s in r["strings"]), constants=frozenset(r["constants"]),
        data_refs=frozenset(r["data_refs"]), callers_count=r["callers_count"], caller_sites=r["caller_sites"],
        ecx_read_before_write=r.get("ecx_read_before_write"), ret_imm=tuple(r["ret_imm"]),
        default_name=r["default_name"],
    )


def load_facts(dumps: Path) -> tuple[Facts, dict[str, dict]]:
    manifest = read_manifest(dumps)
    headers = {n: verify_dump(dumps, n, manifest) for n in ("pc-ida.jsonl", "ps4-ida.jsonl", "ps4-dwarf.jsonl")}
    if headers["pc-ida.jsonl"]["side"] != "pc" or headers["ps4-ida.jsonl"]["side"] != "ps4":
        raise DumpIdentityError("dump sides do not match their names")
    if headers["ps4-ida.jsonl"]["input_sha256"] != headers["ps4-dwarf.jsonl"]["elf_sha256"]:
        raise DumpIdentityError("PS4 IDA dump and DWARF dump are from different ELFs")
    pc: dict[int, Func] = {}
    cbs: set[int] = set()
    group: dict[int, int] = {}
    orphan: set[str] = set()
    missing: set[int] = set()
    for r in _iter(dumps / "pc-ida.jsonl"):
        k = r["kind"]
        if k == "function":
            pc[r["va"]] = _func(r, "pc")
        elif k == "table" and r["callback"]:
            cbs.add(r["callback"])
            group.setdefault(r["callback"], r["group"])
        elif k == "missing_root":
            missing.add(r["va"])
        elif k == "summary":
            orphan = {o["text"] for o in r["onpacket_orphan_refs"]}
    ps4 = {r["va"]: _func(r, "ps4") for r in _iter(dumps / "ps4-ida.jsonl") if r["kind"] == "function"}
    params: dict[int, list[Param]] = {}
    inlines: dict[int, list[int]] = {}
    types: dict[int, DwarfType] = {}
    for r in _iter(dumps / "ps4-dwarf.jsonl"):
        if r["kind"] == "function":
            params[r["va"]] = [Param(p["name"], p["type"], p.get("type_die"), bool(p.get("artificial")))
                               for p in r["params"]]
            inlines[r["va"]] = sorted(min(lo for lo, _ in i["ranges"]) for i in r["inlined"]
                                      if i["parent"] is None and i["ranges"])
        elif r["kind"] == "type":
            types[r["die"]] = DwarfType(r["die"], r["tag"], r["name"], r.get("size"), r.get("target_die"),
                                         r.get("target"))
    facts = Facts(pc=pc, ps4=ps4, table_callbacks=cbs, table_group=group, onpacket_orphan_strings=orphan,
                  missing_roots=missing, dwarf_params=params, dwarf_inlines=inlines, types=types)
    return facts, headers

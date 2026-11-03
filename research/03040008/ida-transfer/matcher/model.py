"""Function facts the matcher reads from the T004 dumps (PC 03040008 IDA, PS4 02020005 IDA + DWARF).

Every loader checks the dump's sha256 against ``dumps/MANIFEST.tsv`` before parsing (fail closed).
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

INDIRECT = None  # call target of an indirect call


@dataclass(frozen=True)
class Call:
    site: int
    target: int | None  # None: indirect
    pushed_bytes: int | None = None  # PC only
    arg_bytes: int | None = None  # PC only (v3): the callee's ret N / add esp,N after the call
    const_stack: tuple[tuple[int, int], ...] = ()  # PC only (v3): (stack slot, immediate) of this call
    const_regs: tuple[tuple[str, int], ...] = ()  # PS4 only (v3): (argument register, immediate)
    ecx_loaded: bool | None = None  # PC only: the caller wrote ecx in the call's argument window

    def stack_const(self, slot: int) -> int | None:
        return dict(self.const_stack).get(slot)

    def reg_const(self, reg: str) -> int | None:
        return dict(self.const_regs).get(reg)


@dataclass(frozen=True)
class Access:
    """One v4+ ``object_accesses`` record: a memory operand whose base provably holds an argument."""

    va: int
    arg_loc: str  # "ecx" | "stack" | PS4 "rdi".."r9"
    arg: int
    disp: int
    width: int | None
    access: str  # load | store | lea
    via: int | None = None  # disp of the field the base pointer was loaded from
    indexed: bool = False
    value: int | None = None


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
    codec: tuple[str, int] | None = None  # (dir, width) from the v3 dump's codec field
    # v4: least calls to a codec within 8 levels (0 = codec, None = none); has_codec_distance False on
    # v3 dumps, where None means "not recorded"
    codec_distance: int | None = None
    has_codec_distance: bool = False
    accesses: tuple[Access, ...] = ()  # v4 object_accesses


@dataclass(frozen=True)
class SlotLayout:
    """PS4 listener-slot arrays from DWARF: ``cSeedGameSvConnection::mpManager`` (``cNetGameServer*``)
    and the ``cNetGameServer`` arrays indexed by the slot, as (member, offset, element size, count)."""

    manager_offset: int
    arrays: tuple[tuple[str, int, int, int], ...]


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
    table_key: dict[int, tuple[int, int, int]] = field(default_factory=dict)  # PC callback -> (group, id, sub)
    # PS4 handler va -> listener slot (mErrorCode/mStatus index of its stores via mpManager, T005h), and
    # why a function with such stores has none (several indices, a variable index).
    ps4_handler_slot: dict[int, int] = field(default_factory=dict)
    ps4_slot_notes: dict[int, str] = field(default_factory=dict)
    slot_layout: SlotLayout | None = None
    # requester call sites outside any function (v4 ``requester_site`` records): side -> sites
    requester_sites_outside: dict[str, list[int]] = field(default_factory=dict)
    externs: dict[tuple[str, int], tuple[str, str]] = field(default_factory=dict)  # (side, va) -> (name, reason)

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


def _access(a: dict) -> Access:
    return Access(int(a["va"]), a["arg_loc"], int(a["arg"]), int(a["disp"]), a.get("width"), a["access"],
                  a.get("via"), bool(a.get("indexed")), a.get("value"))


def _func(r: dict, side: str) -> Func:
    calls = sorted(
        (Call(c["site"], None if c["target"] == "indirect" else int(c["target"]), c.get("pushed_bytes"),
              c.get("arg_bytes"), tuple((int(a), int(b)) for a, b in c.get("const_stack", ())),
              tuple(sorted((k, int(v)) for k, v in c.get("const_regs", {}).items())), c.get("ecx_loaded"))
         for c in r["calls"]),
        key=lambda c: c.site,
    )
    return Func(
        va=r["va"], name=r["name"], side=side, size=r["size"], instructions=r["instructions"], calls=calls,
        strings=frozenset(s["text"] for s in r["strings"]), constants=frozenset(r["constants"]),
        data_refs=frozenset(r["data_refs"]), callers_count=r["callers_count"], caller_sites=r["caller_sites"],
        ecx_read_before_write=r.get("ecx_read_before_write"), ret_imm=tuple(r["ret_imm"]),
        default_name=r["default_name"],
        codec=(r["codec"]["dir"], int(r["codec"]["width"])) if r.get("codec") else None,
        codec_distance=r.get("codec_distance"), has_codec_distance="codec_distance" in r,
        accesses=tuple(_access(a) for a in r.get("object_accesses", ())),
    )


SLOT_CONNECTION, SLOT_MANAGER = "cSeedGameSvConnection", "cNetGameServer"
SLOT_ARRAYS = ("mStatus", "mErrorCode")
_ARRAY_COUNT = re.compile(r"\[(\d+)\]$")


def slot_layout(type_records: list[dict]) -> SlotLayout | None:
    """The :class:`SlotLayout` from the DWARF type records, or None unless each class has exactly one
    record, ``mpManager`` points to the manager class and both arrays have a count (fail closed)."""
    by: dict[str, list[dict]] = {}
    for r in type_records:
        if r.get("name") in (SLOT_CONNECTION, SLOT_MANAGER) and r.get("members"):
            by.setdefault(r["name"], []).append(r)
    if any(len(by.get(n, ())) != 1 for n in (SLOT_CONNECTION, SLOT_MANAGER)):
        return None
    conn = {m["name"]: m for m in by[SLOT_CONNECTION][0]["members"]}
    mgr = {m["name"]: m for m in by[SLOT_MANAGER][0]["members"]}
    mp = conn.get("mpManager")
    if mp is None or mp.get("type") != SLOT_MANAGER + "*" or mp.get("offset") is None:
        return None
    arrays = []
    for name in SLOT_ARRAYS:
        m = mgr.get(name)
        cnt = _ARRAY_COUNT.search((m or {}).get("type") or "")
        if m is None or m.get("offset") is None or not cnt or not m.get("size") or m["size"] % int(cnt.group(1)):
            return None
        n = int(cnt.group(1))
        arrays.append((name, int(m["offset"]), m["size"] // n, n))
    return SlotLayout(int(mp["offset"]), tuple(arrays))


def ps4_slot(f: Func, layout: SlotLayout) -> tuple[int | None, str | None]:
    """Listener slot of a PS4 ``cSeedGameSvConnection`` function: the index of its stores into the
    manager's slot arrays, ``this->mpManager->mErrorCode[idx]`` / ``mStatus[idx]`` (arg 0 ``rdi``, ``via``
    = the ``mpManager`` offset). Returns (slot, None), (None, why) when the stores disagree or one is
    indexed by a register, or (None, None) when there is no such store."""
    idx: set[int] = set()
    variable = False
    for a in f.accesses:
        if a.access != "store" or a.arg_loc != "rdi" or a.arg != 0 or a.via != layout.manager_offset:
            continue
        for _name, off, size, count in layout.arrays:
            if off <= a.disp < off + size * count:
                if a.indexed:
                    variable = True
                elif (a.disp - off) % size == 0 and a.width == size:
                    idx.add((a.disp - off) // size)
    if variable:
        return None, "variable slot index"
    if len(idx) > 1:
        return None, "several slot indices " + ",".join(str(i) for i in sorted(idx))
    return (idx.pop(), None) if idx else (None, None)


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
    key: dict[int, tuple[int, int, int]] = {}
    ext: dict[tuple[str, int], tuple[str, str]] = {}
    outside: dict[str, list[int]] = {}
    for r in _iter(dumps / "pc-ida.jsonl"):
        k = r["kind"]
        if k == "function":
            pc[r["va"]] = _func(r, "pc")
        elif k == "table" and r["callback"]:
            cbs.add(r["callback"])
            group.setdefault(r["callback"], r["group"])
            key.setdefault(r["callback"], (r["group"], r["id"], r["sub"]))
        elif k == "missing_root":
            missing.add(r["va"])
        elif k == "extern":
            ext[("pc", r["va"])] = (r["name"], r["reason"])
        elif k == "summary":
            orphan = {o["text"] for o in r["onpacket_orphan_refs"]}
        elif k == "requester_site":
            outside.setdefault("pc", []).append(r["va"])
    ps4: dict[int, Func] = {}
    for r in _iter(dumps / "ps4-ida.jsonl"):
        if r["kind"] == "function":
            ps4[r["va"]] = _func(r, "ps4")
        elif r["kind"] == "extern":
            ext[("ps4", r["va"])] = (r["name"], r["reason"])
        elif r["kind"] == "requester_site":
            outside.setdefault("ps4", []).append(r["va"])
    params: dict[int, list[Param]] = {}
    inlines: dict[int, list[int]] = {}
    types: dict[int, DwarfType] = {}
    slot_types: list[dict] = []
    for r in _iter(dumps / "ps4-dwarf.jsonl"):
        if r["kind"] == "function":
            params[r["va"]] = [Param(p["name"], p["type"], p.get("type_die"), bool(p.get("artificial")))
                               for p in r["params"]]
            inlines[r["va"]] = sorted(min(lo for lo, _ in i["ranges"]) for i in r["inlined"]
                                      if i["parent"] is None and i["ranges"])
        elif r["kind"] == "type":
            if r.get("name") in (SLOT_CONNECTION, SLOT_MANAGER):
                slot_types.append(r)
            types[r["die"]] = DwarfType(r["die"], r["tag"], r["name"], r.get("size"), r.get("target_die"),
                                         r.get("target"))
    facts = Facts(pc=pc, ps4=ps4, table_callbacks=cbs, table_group=group, onpacket_orphan_strings=orphan,
                  missing_roots=missing, dwarf_params=params, dwarf_inlines=inlines, types=types,
                  table_key=key, externs=ext, requester_sites_outside=outside)
    layout = slot_layout(slot_types)
    facts.slot_layout = layout
    if layout is not None:
        for f in ps4.values():
            if not f.name.startswith(SLOT_CONNECTION + "::"):
                continue
            slot, why = ps4_slot(f, layout)
            if slot is not None:
                facts.ps4_handler_slot[f.va] = slot
            elif why is not None:
                facts.ps4_slot_notes[f.va] = why
    return facts, headers

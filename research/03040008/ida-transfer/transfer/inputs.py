"""Inputs of the transfer rules: the matcher's accepted pairs, the dumps' extra fields, the T002 audit."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PairRow:
    pc_va: int
    ps4_va: int
    ps4_symbol: str
    pc_name: str
    pc_name_source: str
    rule: str
    flags: str


@dataclass(frozen=True)
class PcExtra:
    name: str
    default_name: bool
    prototype: str | None
    prototype_user: bool
    comment: str | None
    string_eas: dict[str, int]


@dataclass(frozen=True)
class Ps4Fn:
    va: int
    name: str  # DWARF qualified name (templates spelled out)
    symbol: str  # mangled
    params: list[dict]
    return_type: str


@dataclass
class Inputs:
    pairs: list[PairRow]
    pc: dict[int, PcExtra]
    ps4fn: dict[int, Ps4Fn]
    types: dict[str, dict]
    t002_names: dict[int, list[str]] = field(default_factory=dict)  # pc va -> name verdicts
    pairs_sources: str = ""


def read_pairs(path: Path) -> tuple[list[PairRow], str]:
    with path.open(encoding="utf-8", newline="") as fh:
        head = fh.readline().strip()
        rows = list(csv.DictReader(fh, delimiter="\t"))
    out = [PairRow(int(r["pc_va"], 16), int(r["ps4_va"], 16), r["ps4_symbol"], r["pc_name"], r["pc_name_source"],
                   r["rule"], r["flags"]) for r in rows if r["status"] == "accepted"]
    return out, head


def pairs_sources_match(head: str, headers: dict[str, dict]) -> bool:
    """The pairs.tsv comment line names the source sha256 of each dump it was built from."""
    for name, h in headers.items():
        src = h.get("input_sha256") or h.get("elf_sha256")
        if f"{name} source {src}" not in head:
            return False
    return True


def read_t002(path: Path) -> dict[int, list[str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        fh.readline()
        rows = list(csv.DictReader(fh, delimiter="\t"))
    out: dict[int, list[str]] = {}
    for r in rows:
        if r["kind"] == "name":
            out.setdefault(int(r["pc_va"], 16), []).append(r["verdict"])
    return out


def t002_rating(verdicts: list[str]) -> str | None:
    """``wrong`` / ``no source`` / None (holds, unproved for another reason, not checked)."""
    for v in verdicts:
        if v.startswith("wrong"):
            return "wrong"
    for v in verdicts:
        if "name source not code" in v:
            return "no source"
    return None


def load_dumps(dumps: Path, pc_vas: set[int] | None = None) -> tuple[dict[int, PcExtra], dict[int, Ps4Fn],
                                                                      dict[str, dict]]:
    pc: dict[int, PcExtra] = {}
    with (dumps / "pc-ida.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["kind"] != "function":
                continue
            a = r.get("annotations") or {}
            pc[r["va"]] = PcExtra(r["name"], r["default_name"], r.get("prototype"), bool(r.get("prototype_user")),
                                  a.get("function_comment"), {s["text"]: s["ea"] for s in r["strings"]})
    ps4fn: dict[int, Ps4Fn] = {}
    types: dict[str, dict] = {}
    with (dumps / "ps4-dwarf.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["kind"] == "function":
                ps4fn[r["va"]] = Ps4Fn(r["va"], r["name"], r.get("symbol") or "", r["params"], r["return_type"])
            elif r["kind"] == "type":
                types[r["name"]] = r
    return pc, ps4fn, types


DEFAULT_NAME = re.compile(r"^(?:sub|nullsub|j_sub|loc|unknown_libname)_[0-9A-Fa-f]+(?:_\d+)?$")

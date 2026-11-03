"""T009b: settled conflict decisions (``T009-decisions.tsv``) turned into correction rows.

A decision names a conflict row by (kind, pc_va) and records the row's current and proposed ("ours") values.
``ours`` -> names ``correct`` / prototypes ``replace`` (the reason and evidence VAs go into the row); ``theirs`` ->
``keep`` (not written); ``merge`` -> the decision's final value as ``correct`` / ``replace``; ``undecided`` -> stays
``conflict``. A decision for a row that is not a conflict, whose recorded current or ours value differs from the
row's, a duplicate or an unknown decision is an error (fail closed).
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, replace
from pathlib import Path

from .names import NameRow
from .prototypes import ProtoRow

KINDS = ("name", "prototype")
DECISIONS = ("ours", "theirs", "merge", "undecided")


@dataclass(frozen=True)
class Decision:
    kind: str
    pc_va: int
    current: str
    ours: str
    decision: str
    final_value: str
    evidence_vas: str
    reason: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_decisions(path: Path) -> list[Decision]:
    with path.open(encoding="utf-8", newline="") as fh:
        head = fh.readline()
        if not head.startswith("#"):
            raise ValueError(f"{path}: no header comment")
        rows = list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))
    out = []
    for n, r in enumerate(rows, start=3):
        if r["kind"] not in KINDS or r["decision"] not in DECISIONS:
            raise ValueError(f"{path}:{n}: unknown kind {r['kind']!r} or decision {r['decision']!r}")
        out.append(Decision(r["kind"], int(r["pc_va"], 16), r["current"], r["ours"], r["decision"],
                            r["final_value"], r["evidence_vas"], r["reason"]))
    return out


def _index(decisions: list[Decision]) -> dict[tuple[str, int], Decision]:
    idx: dict[tuple[str, int], Decision] = {}
    for d in decisions:
        key = (d.kind, d.pc_va)
        if key in idx:
            raise ValueError(f"two decisions for {d.kind} {d.pc_va:#x}")
        idx[key] = d
    return idx


def _check(d: Decision, action: str, current: str, ours: str) -> None:
    where = f"decision for {d.kind} {d.pc_va:#x}"
    if action != "conflict":
        raise ValueError(f"{where}: the row is not a conflict (action {action})")
    if d.current != current:
        raise ValueError(f"{where}: recorded current {d.current!r} differs from the row's {current!r}")
    if d.ours != ours:
        raise ValueError(f"{where}: recorded ours {d.ours!r} differs from the row's {ours!r}")
    if d.decision in ("ours", "merge") and not d.final_value:
        raise ValueError(f"{where}: no final value")
    if d.decision == "ours" and d.final_value != ours:
        raise ValueError(f"{where}: decision ours with final value {d.final_value!r} != {ours!r}")


def _basis(basis: str, d: Decision) -> str:
    return f"{basis}; T009 {d.decision}; evidence {d.evidence_vas}"


def apply(names: list[NameRow], protos: list[ProtoRow], decisions: list[Decision]
          ) -> tuple[list[NameRow], list[ProtoRow]]:
    """The rows with every decision applied; every decision must hit one conflict row."""
    idx = _index(decisions)
    used: set[tuple[str, int]] = set()
    out_n: list[NameRow] = []
    for r in names:
        d = idx.get(("name", r.pc_va)) if r.action != "remove-label" else None
        if d is None:
            out_n.append(r)
            continue
        used.add(("name", r.pc_va))
        _check(d, r.action, r.current, r.name)
        if d.decision == "undecided":
            out_n.append(r)
        elif d.decision == "theirs":
            out_n.append(replace(r, action="keep", basis=_basis(r.basis, d), reason=f"T009: {d.reason}"))
        else:
            out_n.append(replace(r, name=d.final_value, action="correct", basis=_basis(r.basis, d),
                                 reason=f"T009: {d.reason}"))
    out_p: list[ProtoRow] = []
    for r in protos:
        d = idx.get(("prototype", r.pc_va))
        if d is None:
            out_p.append(r)
            continue
        used.add(("prototype", r.pc_va))
        _check(d, r.action, r.current, r.decl)
        if d.decision == "undecided":
            out_p.append(r)
        elif d.decision == "theirs":
            out_p.append(replace(r, action="keep", basis=_basis(r.basis, d), notes=f"T009: {d.reason}"))
        else:
            out_p.append(replace(r, decl=d.final_value, action="replace", basis=_basis(r.basis, d),
                                 notes=f"T009: {d.reason}"))
    missing = sorted(set(idx) - used)
    if missing:
        raise ValueError("decisions for rows the transfer does not have: "
                         + " ".join(f"{k} {va:#x}" for k, va in missing))
    return out_n, out_p

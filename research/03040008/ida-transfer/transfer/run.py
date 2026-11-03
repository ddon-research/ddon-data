"""The transfer pipeline: rules 1-6 over the accepted pairs and the dumps, and the manifest/transfer/ writer."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from matcher import checks
from matcher import tier0 as t0mod
from matcher.model import Facts

from . import comments, names, prototypes, render, typecheck
from .inputs import PairRow, PcExtra, Ps4Fn
from .layout import Layouts, declarable


@dataclass
class Result:
    names: list[names.NameRow]
    protos: list[prototypes.ProtoRow]
    verdicts: dict[str, typecheck.TypeVerdict]
    emitted: set[str]
    enums: dict[str, dict]
    rendered: render.Rendered
    comments: list[comments.CommentRow]
    skipped: list[tuple[str, str, str, str, str]] = field(default_factory=list)  # rule, item, candidate, action, why
    precision: list[tuple[int, int, int, int, str, str]] = field(default_factory=list)
    depends: dict[str, list[int]] = field(default_factory=dict)  # type -> rng seeds whose holdout lost it


def accepted_types(verdicts: dict[str, typecheck.TypeVerdict]) -> set[str]:
    return {n for n, v in verdicts.items() if v.status == "accepted"}


def type_verdicts(facts: Facts, layouts: Layouts, pairs: list[PairRow], ps4fn: dict[int, Ps4Fn]
                  ) -> dict[str, typecheck.TypeVerdict]:
    ev, bad, roots = typecheck.collect(facts, layouts, pairs, ps4fn)
    return typecheck.decide(layouts, ev, bad, roots)


def build(facts: Facts, pairs: list[PairRow], pc: dict[int, PcExtra], ps4fn: dict[int, Ps4Fn],
          types: dict[str, dict], t002: dict[int, list[str]], tier0: dict[int, str], title: str) -> Result:
    layouts = Layouts(types)
    skipped: list[tuple[str, str, str, str, str]] = []
    by_pc = {p.pc_va: p for p in pairs}

    # rule 1
    nrows = names.name_rows(tier0, pairs, pc, t002)
    for r in nrows:
        if r.action not in names.WRITTEN and r.action != "remove-label":
            skipped.append(("names", f"{r.pc_va:#x}", r.name, r.action, f"{r.reason} (current {r.current})"))

    # rule 3 (before 2: prototypes point to transferred types)
    verdicts = type_verdicts(facts, layouts, pairs, ps4fn)
    emitted = {n for n, v in verdicts.items() if v.status in ("accepted", "embedded") and declarable(n)}

    # rule 2
    protos: list[prototypes.ProtoRow] = []
    for p in sorted(pairs, key=lambda p: p.pc_va):
        fn = ps4fn.get(p.ps4_va)
        if fn is None:
            skipped.append(("prototypes", f"{p.pc_va:#x}", p.ps4_symbol, "skip", "no DWARF record"))
            continue
        protos.append(prototypes.pair_prototype(facts, layouts, p.pc_va, fn, pc.get(p.pc_va), f"paired by {p.rule}"))
    for va in sorted(set(tier0) - set(by_pc)):
        protos.append(prototypes.tier0_prototype(facts, va, tier0[va], pc.get(va)))
    for r in protos:
        if r.action != "set":
            skipped.append(("prototypes", f"{r.pc_va:#x}", r.decl or "-", r.action,
                            r.notes + (f" (current {r.current})" if r.current else "")))

    # enums used by emitted members and written prototypes
    proto_classes = {c for r in protos if r.action == "set" for c in r.classes}
    want = render.member_enums(emitted, layouts) | {e for r in protos if r.action == "set" for e in r.enums}
    enum_recs = {e: types[e] for e in want if e in types and types[e]["tag"] == "enumeration"}
    coll = render.enum_collisions(enum_recs)
    for e, why in sorted(coll.items()):
        skipped.append(("types", e, "enum", "skip", why))
        del enum_recs[e]
    dropped = set(coll)
    if dropped:  # prototypes naming a dropped enum fall back to its width (rare): list them, do not write
        keep = []
        for r in protos:
            if r.action == "set" and set(r.enums) & dropped:
                skipped.append(("prototypes", f"{r.pc_va:#x}", r.decl, "skip", "uses an enum that is not transferred"))
                keep.append(prototypes.ProtoRow(r.pc_va, r.decl, r.current, "skip", r.basis, r.notes, r.classes,
                                                r.enums))
            else:
                keep.append(r)
        protos = keep
    checked = {n: v.checked_members for n, v in verdicts.items()}
    rendered = render.render(emitted, enum_recs, layouts, checked, proto_classes, title)

    for n, v in sorted(verdicts.items()):
        if v.status in ("accepted", "embedded"):
            continue
        why = v.reason
        if v.contradictions:
            why += ": " + typecheck.contradiction_text(v)
        skipped.append(("types", n, "struct", v.status, why))

    # rule 4
    written = {r.pc_va for r in nrows if r.action in names.WRITTEN} | {r.pc_va for r in protos if r.action == "set"}
    crows: list[comments.CommentRow] = []
    for va in sorted(written):
        p = by_pc.get(va)
        x = pc.get(va)
        s_ea = x.string_eas.get(tier0[va]) if (va in tier0 and x) else None
        ps4 = None
        if p is not None:
            fn = ps4fn.get(p.ps4_va)
            ps4 = (fn.name if fn else p.ps4_symbol, fn.symbol if fn else "", p.rule)
        crows.append(comments.comment_row(va, comments.text(s_ea, ps4, p.flags if p else "-"),
                                          x.comment if x else None))
    return Result(nrows, protos, verdicts, emitted, enum_recs, rendered, crows, skipped)


def holdout(facts: Facts, tier0: dict[int, str], types: dict[str, dict], ps4fn: dict[int, Ps4Fn],
            full_pairs: list[PairRow], res: Result) -> None:
    """Rule 6: T005e's holdout (5 RNG seeds x 20% of the seeds withheld) rerun through the type check."""
    seeds, _ = t0mod.seed_candidates(facts, tier0)
    prefixes = t0mod.group_prefixes(tier0, facts)
    full_acc = accepted_types(res.verdicts)
    for rng in checks.RNG_SEEDS:
        withheld = checks.holdout(seeds, rng)
        part = checks.pipeline(facts, {k: v for k, v in seeds.items() if k not in withheld}, tier0, prefixes)
        prs = [PairRow(pc, ps4, "", "", "", rule, "-") for (pc, ps4), rule in part.pairs().items()]
        acc = accepted_types(type_verdicts(facts, Layouts(types), prs, ps4fn))
        lost = sorted(full_acc - acc)
        new = sorted(acc - full_acc)
        for t in lost:
            res.depends.setdefault(t, []).append(rng)
        res.precision.append((rng, len(withheld), len(prs), len(acc), " ".join(lost) or "-", " ".join(new) or "-"))


def full_pairs_check(facts: Facts, tier0: dict[int, str], pairs: list[PairRow]) -> str | None:
    """The matcher's pipeline on these dumps must give exactly the accepted pairs of pairs.tsv (fail closed)."""
    seeds, _ = t0mod.seed_candidates(facts, tier0)
    full = checks.pipeline(facts, seeds, tier0, t0mod.group_prefixes(tier0, facts))
    got = {(pc, ps4): rule for (pc, ps4), rule in full.pairs().items()}
    want = {(p.pc_va, p.ps4_va): p.rule for p in pairs}
    if got != want:
        return f"pairs.tsv differs from the matcher run: {len(set(want) ^ set(got))} pairs"
    return None


# --- writer ------------------------------------------------------------------------------------------------


def _cell(v: object) -> str:
    s = "" if v is None else str(v)
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")


def _write(path: Path, head: str, cols: list[str], rows: list[list]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(head + "\n")
        w = csv.writer(fh, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_NONE, escapechar=None,
                       quotechar=None)
        w.writerow(cols)
        for r in rows:
            w.writerow([_cell(c) for c in r])
    return len(rows)


def write_all(out: Path, res: Result, layouts: Layouts, head: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    nr = [r for r in res.names if r.action in names.WRITTEN or r.action == "remove-label"]
    counts["names.tsv"] = _write(out / "names.tsv", head, ["pc_va", "action", "name", "current", "source", "basis",
                                                           "reason"],
                                 [[f"{r.pc_va:#x}", r.action, r.name, r.current, r.source, r.basis, r.reason]
                                  for r in nr])
    pr = [r for r in res.protos if r.action == "set"]
    counts["prototypes.tsv"] = _write(out / "prototypes.tsv", head, ["pc_va", "action", "decl", "current", "basis",
                                                                     "notes", "types", "enums"],
                                      [[f"{r.pc_va:#x}", r.action, r.decl, r.current, r.basis, r.notes,
                                        " ".join(r.classes) or "-", " ".join(r.enums) or "-"] for r in pr])
    trows = []
    for n in sorted(res.emitted):
        v = res.verdicts[n]
        info = layouts.layout(n)
        all_m = [m.name for m in info.members]
        unchecked = [m for m in all_m if m not in v.checked_members]
        rec = layouts.record(n) or {}
        trows.append([n, "union" if info.union else "struct", v.status, f"{info.size:#x}",
                      f"{rec.get('size'):#x}" if rec.get("size") is not None else "-", v.checked, len(v.functions),
                      " ".join(m for m in all_m if m in v.checked_members) or "-", " ".join(unchecked) or "-",
                      " ".join(f"{x:#x}" for x in sorted(v.evidence_vas)[:10]), v.size_evidence or
                      "no allocation or constructor size in the dumps",
                      " ".join(str(s) for s in res.depends.get(n, [])) or "-", v.reason])
    for e in sorted(res.enums):
        trows.append([e, "enum", "referenced", f"{res.enums[e]['size']:#x}", f"{res.enums[e]['size']:#x}", 0, 0,
                      "-", "-", "", "DWARF enum as is", "-", "used by a transferred member or prototype"])
    for o in sorted(res.rendered.opaque):
        trows.append([o, "opaque", "declared", "-", "-", 0, 0, "-", "-", "", "-", "-",
                      "pointee of a transferred member or prototype; no layout claim"])
    counts["types.tsv"] = _write(out / "types.tsv", head, ["type", "kind", "status", "pc_size", "ps4_size",
                                                           "checked_accesses", "functions", "members_checked",
                                                           "members_unchecked", "evidence_vas", "size_evidence",
                                                           "holdout_lost_in_rng", "basis"], trows)
    counts["type_members.tsv"] = _write(out / "type_members.tsv", head, ["type", "offset", "size", "member", "decl",
                                                                         "dwarf_type", "checked_by"],
                                        [[m.type, f"{m.offset:#x}", m.size, m.member, m.decl, m.dwarf_type, m.checked]
                                         for m in res.rendered.members])
    (out / "types.h").write_text(res.rendered.header, encoding="utf-8", newline="\n")
    counts["comments.tsv"] = _write(out / "comments.tsv", head, ["pc_va", "action", "comment", "existing"],
                                    [[f"{r.pc_va:#x}", r.action, r.comment, r.existing] for r in res.comments])
    counts["skipped.tsv"] = _write(out / "skipped.tsv", head, ["rule", "item", "candidate", "action", "reason"],
                                   [list(r) for r in sorted(res.skipped)])
    counts["precision.tsv"] = _write(out / "precision.tsv", head, ["rng_seed", "withheld_seeds", "pairs",
                                                                   "types_accepted", "lost", "new"],
                                     [list(r) for r in res.precision])
    summ = summary(res)
    _write(out / "summary.tsv", head, ["key", "value"], [[k, v] for k, v in summ.items()])
    counts.update({f"summary {k}": v for k, v in summ.items()})
    return counts


def summary(res: Result) -> dict[str, int]:
    from collections import Counter
    out: dict[str, int] = {}
    for k, v in sorted(Counter(r.action for r in res.names).items()):
        out[f"names {k}"] = v
    for k, v in sorted(Counter(r.action for r in res.protos).items()):
        out[f"prototypes {k}"] = v
    for k, v in sorted(Counter(v.status for v in res.verdicts.values()).items()):
        out[f"types {k}"] = v
    out["types emitted"] = len(res.emitted)
    out["types emitted non-template"] = sum(1 for n in res.emitted if "<" not in n)
    out["enums emitted"] = len(res.enums)
    out["opaque declared"] = len(res.rendered.opaque)
    for k, v in sorted(Counter(r.action for r in res.comments).items()):
        out[f"comments {k}"] = v
    out["skipped"] = len(res.skipped)
    out["holdout types lost (any rng)"] = len(res.depends)
    return out


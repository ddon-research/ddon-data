"""The manifest TSVs (deterministic order, no timestamps)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import checks, engine, gates, tier0
from .model import Facts

# T002 audit 3.4: byte-identical (or near) PC codec bodies; listed whatever the run does with them.
T002_CODECS = {
    0x8BC480: "Read_s32", 0x8BC4D0: "Read_u32", 0x8BC520: "Read_f32", 0x8BC410: "Read_u8", 0x8BC6E0: "Read_bool",
    0x8BC660: "Read_s64", 0x8BC6A0: "Read_u64", 0x8BC860: "Write_u8", 0x8BCB80: "Write_bool",
    0x8BC8D0: "Write_s32", 0x8BC920: "Write_u32",
}


def _h(v: int | None) -> str:
    return "-" if v is None else f"{v:#x}"


def _write(path: Path, header: list[str], rows: list[list[str]], comment: str) -> None:
    lines = [f"# {comment}", "\t".join(header)]
    lines += ["\t".join(str(x).replace("\t", " ") for x in r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def pc_names(facts: Facts, res: engine.Result, t0: dict[int, str]) -> dict[int, tuple[str, str]]:
    out = {}
    for p, a in res.accepted.items():
        out[p[0]] = (t0[p[0]], "pc-string") if a.source == "seed" else (facts.ps4[p[1]].name, "ps4-symbol")
    return out


def write_all(out: Path, facts: Facts, headers: dict, t0: dict[int, str], t0_listed: list[tier0.Listed],
              seeds: dict[int, int], seed_listed: list[tier0.Listed], res: engine.Result,
              precision: list[checks.PrecisionRow], cross: list[checks.CrossRow]) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    ident = "; ".join(f"{n} source {h.get('input_sha256') or h.get('elf_sha256')}" for n, h in sorted(headers.items()))
    comment = f"007 T005 matcher, PC 03040008 <-> PS4 02020005; inputs: {ident}"
    names = pc_names(facts, res, t0)

    rows = []
    for p in sorted(res.accepted):
        a = res.accepted[p]
        nm, src = names[p[0]]
        rows.append([_h(p[0]), _h(p[1]), facts.ps4[p[1]].name, nm, src,
                     "0" if a.source == "seed" else "propagation", a.iteration,
                     " ".join(f"{w[0]:#x}:{w[1]:#x}" for w in a.witnesses) or "-", a.gate_results, "accepted"])
    _write(out / "pairs.tsv", ["pc_va", "ps4_va", "ps4_symbol", "pc_name", "pc_name_source", "tier", "iteration",
                               "witnesses", "gate_results", "status"], rows, comment)

    rej = [[x.candidate, x.gate, x.detail] for x in t0_listed + seed_listed]
    for p, why in sorted(res.seed_failed.items()):
        rej.append([f"pc:{p[0]:#x} ps4:{p[1]:#x}", "c", f"seed {facts.ps4[p[1]].name}: {why}"])
    for p, fails in sorted(res.failed.items()):
        ws = " ".join(f"{w[0]:#x}:{w[1]:#x}" for w in sorted(res.proposals.get(p, ())))
        for g, why in fails:
            rej.append([f"pc:{p[0]:#x} ps4:{p[1]:#x}", g, f"{why} (witnesses {ws or '-'})"])
    folded = gates.fold_groups(facts.pc)
    proposed_pc = Counter(p[0] for p in res.proposals)
    for va, label in sorted(T002_CODECS.items()):
        f = facts.pc.get(va)
        why = "; ".join(gates.trivial_reasons(f, folded)) if f else "no function record"
        rej.append([f"pc:{va:#x}", "d",
                    f"T002 codec {label}: {why or 'not trivial'}; proposed {proposed_pc[va]} time(s)"])
    rej.sort(key=lambda r: (r[1], r[0], r[2]))
    _write(out / "rejected.tsv", ["candidate", "gate", "detail"], rej, comment)

    conf = []
    for (side, va), ps in sorted(res.conflicts.items()):
        conf.append([side, _h(va), " ".join(f"{p[0]:#x}:{p[1]:#x}" for p in sorted(ps))])
    _write(out / "conflicts.tsv", ["side", "va", "conflicting_pairs"], conf, comment)

    prec = [[r.rng_seed, r.seeds, r.withheld, r.recovered, r.recovered_correctly, r.recovered_wrongly,
             r.accepted_pairs, " ".join(r.wrong) or "-"] for r in precision]
    _write(out / "precision.tsv", ["rng_seed", "seeds", "withheld", "recovered", "recovered_correctly",
                                   "recovered_wrongly", "accepted_pairs", "wrong"], prec, comment)

    cx = [[r.source, r.key, _h(r.pc_va), r.expected, r.paired, r.result] for r in cross]
    cx.sort(key=lambda r: (r[0], r[2], r[1]))
    _write(out / "crosscheck.tsv", ["source", "key", "pc_va", "expected", "paired", "result"], cx, comment)

    st = res.gap_stats
    counts: dict[str, int] = {
        "table_callbacks": len(facts.table_callbacks),
        "tier0_named": len(t0),
        "tier0_listed": sum(1 for x in t0_listed),
        "seed_candidates": len(seeds),
        "seed_listed_several_ps4": sum(1 for x in seed_listed if "several PS4" in x.detail),
        "seed_listed_no_ps4": sum(1 for x in seed_listed if "no PS4" in x.detail),
        "seed_listed_other_class": sum(1 for x in seed_listed if "another connection class" in x.detail),
        "seed_listed_ps4_claimed_twice": sum(1 for x in seed_listed if "also the candidate" in x.detail),
        "seed_failed_gate_c": len(res.seed_failed),
        "seeds_accepted": sum(1 for a in res.accepted.values() if a.source == "seed"),
        "accepted_total": len(res.accepted),
        "proposals": len(res.proposals),
        "conflict_vertices": len(res.conflicts),
        "rejected_by_b": len(res.rejected_b),
        "restarts": res.restarts,
        "gaps_one_to_one": st.even_one,
        "gaps_blocked": st.blocked,
        "gaps_uneven": sum(st.uneven.values()),
        "gaps_uneven_only_by_ps4_inline": st.uneven_by_inline,
        "gaps_even_other": sum(st.even_other.values()),
    }
    for it, n in sorted(res.by_iteration.items()):
        counts[f"accepted_iteration_{it}"] = n
    for g, n in sorted(Counter(g for fails in res.failed.values() for g, _ in fails).items()):
        counts[f"proposals_failing_gate_{g}"] = n
    for (a, b), n in sorted(st.uneven.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        counts[f"gaps_uneven_pc{a}_ps4{b}"] = n
    agg = Counter(f"crosscheck {r.source}: {r.result.split(':')[0]}" for r in cross)
    counts.update(sorted(agg.items()))
    _write(out / "summary.tsv", ["count", "value"], [[k, v] for k, v in counts.items()], comment)
    return counts

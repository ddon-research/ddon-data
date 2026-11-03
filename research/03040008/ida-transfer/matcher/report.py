"""The manifest TSVs (deterministic order, no timestamps)."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import checks, codecs, engine, gates, roles, tier0
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


def pc_names(facts: Facts, res: engine.Result, t0: dict[int, str],
             role: roles.RoleResult | None = None) -> dict[int, tuple[str, str]]:
    out = {}
    for p, a in res.accepted.items():
        out[p[0]] = (t0[p[0]], "pc-string") if a.source == "seed" else (facts.ps4[p[1]].name, "ps4-symbol")
    for p in (role.pairs if role else {}):
        out[p[0]] = (facts.ps4[p[1]].name, "ps4-symbol")
    return out


T005B_EXPECTED = {"reader": 88, "element-reader": 117}


def write_all(out: Path, facts: Facts, headers: dict, t0: dict[int, str], t0_listed: list[tier0.Listed],
              seeds: dict[int, int], seed_listed: list[tier0.Listed], full: checks.Run,
              precision: list[checks.PrecisionRow], role_precision: list[checks.RolePrecisionRow],
              control: list[checks.ControlRow], cross: list[checks.CrossRow]) -> dict[str, int]:
    res, role = full.engine, full.roles
    out.mkdir(parents=True, exist_ok=True)
    ident = "; ".join(f"{n} source {h.get('input_sha256') or h.get('elf_sha256')}" for n, h in sorted(headers.items()))
    comment = f"007 T005h matcher (pairs v2), PC 03040008 <-> PS4 02020005; inputs: {ident}"
    names = pc_names(facts, res, t0, role)

    rows = []
    for p in sorted(res.accepted):
        a = res.accepted[p]
        nm, src = names[p[0]]
        rows.append([_h(p[0]), _h(p[1]), facts.ps4[p[1]].name, nm, src, a.source,
                     "0" if a.source == "seed" else "propagation", a.iteration,
                     " ".join(f"{w[0]:#x}:{w[1]:#x}" for w in a.witnesses) or "-", a.gate_results, "-", "accepted"])
    for p in sorted(role.pairs):
        r = role.pairs[p]
        nm, src = names[p[0]]
        rows.append([_h(p[0]), _h(p[1]), facts.ps4[p[1]].name, nm, src, r.rule, "role", r.iteration,
                     " ".join(r.witnesses), r.gate_results, r.flags, "accepted"])
    rows.sort(key=lambda r: (int(r[0], 16), int(r[1], 16)))
    _write(out / "pairs.tsv", ["pc_va", "ps4_va", "ps4_symbol", "pc_name", "pc_name_source", "rule", "tier",
                               "iteration", "witnesses", "gate_results", "flags", "status"], rows, comment)

    _write(out / "callsites.tsv", ["pc_site", "pc_function", "pc_codec_va", "width", "ps4_overload", "contexts",
                                   "status", "ps4_site", "ps4_owner"], role.callsites,
           comment + "; rule 3: PS4 overload at the same codec position of equal-width reader pairs (PC call "
           "sites only; never names the shared PC codec functions)")

    rej = [[x.candidate, x.gate, x.detail] for x in t0_listed + seed_listed]
    rej += [[x.candidate, f"role-{x.rule}", x.detail] for x in role.listed]
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
        conf.append(["propagation", side, _h(va), " ".join(f"{p[0]:#x}:{p[1]:#x}" for p in sorted(ps))])
    for (side, va), ps in sorted(role.conflicts.items()):
        conf.append(["role", side, _h(va), " ".join(f"{p[0]:#x}:{p[1]:#x}" for p in sorted(ps))])
    _write(out / "conflicts.tsv", ["stage", "side", "va", "conflicting_pairs"], conf, comment)

    prec = []
    for r, q in zip(precision, role_precision, strict=True):
        prec.append([r.rng_seed, r.seeds, r.withheld, r.recovered, r.recovered_correctly, r.recovered_wrongly,
                     q.derived_full, q.dependent, q.dependent_absent, q.dependent_same, q.wrong, q.new,
                     q.derived_holdout, " ".join(r.wrong) or "-", " | ".join(q.detail) or "-"])
    _write(out / "precision.tsv", ["rng_seed", "seeds", "withheld", "seeds_recovered", "seeds_recovered_correctly",
                                   "seeds_recovered_wrongly", "role_pairs_full", "role_dependent",
                                   "role_dependent_absent", "role_dependent_same_partner", "role_wrong",
                                   "role_new", "role_pairs_holdout", "seed_wrong", "role_detail"], prec, comment)

    def _kv(d: dict) -> str:
        return " ".join(f"{k}={v}" for k, v in sorted(d.items())) or "-"
    ctl = [[c.rng_seed, c.seeds, c.seeds_passing_c, c.contexts_equal, c.contexts_embedded, _kv(c.proposals),
            _kv(c.accepted), c.accepted_agree_real, c.accepted_wrong, " | ".join(c.detail) or "-"] for c in control]
    _write(out / "control.tsv", ["rng_seed", "seeds", "shuffled_seeds_passing_c", "contexts_equal",
                                 "contexts_embedded", "proposals", "accepted", "accepted_equal_to_real_run",
                                 "accepted_not_in_real_run", "detail"], ctl,
           comment + "; negative control: the PS4 side of the seeds deranged by the RNG seed")

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
    by_rule = Counter(r.rule for r in role.pairs.values())
    for rule in ("reader", "element-reader", "listener-requester", "listener-sender", "anchored-gap"):
        counts[f"role_accepted_{rule}"] = by_rule.get(rule, 0)
    for rule, n in sorted(T005B_EXPECTED.items()):
        counts[f"role_t005b_expected_{rule}"] = n
    counts["role_element_reader_season3_extended"] = sum(1 for r in role.pairs.values() if r.flags != "-")
    for it, n in sorted(Counter(r.iteration for r in role.pairs.values() if r.rule == "element-reader").items()):
        counts[f"role_element_reader_iteration_{it}"] = n
    for k, n in sorted(role.proposals.items()):
        counts[f"role_proposals_{k}"] = n
    counts["role_handlers_inlined_on_ps4"] = len(role.inlined_on_ps4)
    for k, n in sorted(role.contexts.items()):
        counts[f"role_contexts_{k}"] = n
    counts["role_callsites"] = len(role.callsites)
    counts["role_callsites_ambiguous"] = sum(1 for r in role.callsites if r[6] != "agree")
    counts["role_callsite_pairs"] = sum(len(r[7].split()) for r in role.callsites)
    counts["role_codec_anchor_sites"] = len(role.codec_sites)
    an = role.anchored
    if an is not None:
        counts["anchored_gaps_one_to_one"] = an.stats.even_one
        counts["anchored_gaps_blocked"] = an.stats.blocked
        counts["anchored_gaps_uneven"] = sum(an.stats.uneven.values())
        counts["anchored_proposals_failed"] = len(an.failed)
        counts["anchored_rejected_by_b"] = len(an.rejected_b)
        counts["anchored_restarts"] = an.restarts
    for (rule, why), n in sorted(Counter((x.rule, x.detail.split(":")[0].split(" (")[0][:70])
                                         for x in role.listed).items()):
        counts[f"role_listed {rule}: {why}"] = n
    counts["listener_ps4_functions_with_slot"] = len(facts.ps4_handler_slot)
    for why, n in sorted(Counter(v.split(" ")[0] for v in facts.ps4_slot_notes.values()).items()):
        counts[f"listener_ps4_slot_refused_{why}"] = n
    for side in ("pc", "ps4"):
        counts[f"listener_{side}_requester_sites_outside_functions"] = len(facts.requester_sites_outside.get(side, ()))
    xc = codecs.ps4_codec_crosscheck(facts)
    counts["ps4_codec_dump_classified"] = len(xc)
    counts["ps4_codec_dump_disagrees_with_symbol"] = sum(1 for r in xc if r[2] != r[3])
    counts["precision_role_wrong_total"] = sum(q.wrong for q in role_precision)
    counts["control_accepted_total"] = sum(c.accepted_agree_real + c.accepted_wrong for c in control)
    counts["control_accepted_not_in_real_run"] = sum(c.accepted_wrong for c in control)
    agg = Counter(f"crosscheck {r.source}: {r.result.split(':')[0]}" for r in cross)
    counts.update(sorted(agg.items()))
    _write(out / "summary.tsv", ["count", "value"], [[k, v] for k, v in counts.items()], comment)
    return counts

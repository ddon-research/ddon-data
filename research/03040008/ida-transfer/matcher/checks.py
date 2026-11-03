"""Rule 5 (precision check by withheld seeds) and rule 6 (cross-checks against 006 T001 and 007 T002)."""

from __future__ import annotations

import csv
import random
import re
from dataclasses import dataclass
from pathlib import Path

from . import anchored, engine, roles
from .model import Facts

HOLDOUT_FRACTION = 0.2
RNG_SEEDS = (1, 2, 3, 4, 5)


@dataclass(frozen=True)
class PrecisionRow:
    rng_seed: int
    seeds: int
    withheld: int
    recovered: int
    recovered_correctly: int
    recovered_wrongly: int
    accepted_pairs: int
    wrong: tuple[str, ...] = ()


def holdout(seeds: dict[int, int], rng_seed: int, fraction: float = HOLDOUT_FRACTION) -> set[int]:
    keys = sorted(seeds)
    return set(random.Random(rng_seed).sample(keys, round(len(keys) * fraction)))


def precision_run(facts: Facts, seeds: dict[int, int], rng_seed: int,
                  withheld: set[int] | None = None) -> PrecisionRow:
    """Run without the withheld seeds (20% by the fixed RNG seed unless given) and check each one the
    run pairs, from either side, against its seed partner."""
    if withheld is None:
        withheld = holdout(seeds, rng_seed)
    res = engine.run(facts, {k: v for k, v in seeds.items() if k not in withheld})
    by_pc = {p[0]: p[1] for p in res.accepted}
    by_ps4 = {p[1]: p[0] for p in res.accepted}
    rec = good = 0
    wrong: list[str] = []
    for pc_va in sorted(withheld):
        ps4_va = seeds[pc_va]
        got_ps4, got_pc = by_pc.get(pc_va), by_ps4.get(ps4_va)
        if got_ps4 is None and got_pc is None:
            continue
        rec += 1
        if got_ps4 == ps4_va and got_pc == pc_va:
            good += 1
        else:
            wrong.append(f"{pc_va:#x}->{got_ps4 and hex(got_ps4)} / {ps4_va:#x}<-{got_pc and hex(got_pc)}")
    return PrecisionRow(rng_seed, len(seeds), len(withheld), rec, good, rec - good, len(res.accepted), tuple(wrong))


def _hex(s: str) -> int | None:
    m = re.search(r"0x[0-9a-fA-F]+", s or "")
    return int(m.group(0), 16) if m else None


@dataclass(frozen=True)
class CrossRow:
    source: str
    key: str
    pc_va: int | None
    expected: str
    paired: str
    result: str


def crosscheck(facts: Facts, names: dict[int, str], pairs: set[tuple[int, int]],
               triage: Path, prior: Path) -> list[CrossRow]:
    """`names`: the PC name the run gives each paired PC va."""
    by_pc = {p[0]: p[1] for p in pairs}
    by_ps4 = {p[1]: p[0] for p in pairs}
    ps4_by_name: dict[str, list[int]] = {}
    for f in facts.ps4.values():
        ps4_by_name.setdefault(f.name, []).append(f.va)

    def link(source: str, key: str, pc_va: int | None, ps4_va: int | None, expected: str) -> CrossRow:
        got = by_pc.get(pc_va) if pc_va is not None else None
        paired = f"{got:#x} {facts.ps4[got].name}" if got is not None else "-"
        if ps4_va is None:
            result = "expected PS4 symbol not in the dump"
        elif got is None:
            other = by_ps4.get(ps4_va)
            result = f"disagree: PS4 side paired with PC {other:#x}" if other is not None else "not paired"
        else:
            result = "agree" if got == ps4_va else "disagree"
        return CrossRow(source, key, pc_va, expected, paired, result)

    rows: list[CrossRow] = []
    with triage.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["mark"] != "matched":
                continue
            rows.append(link("006-T001 matched", r["id"], _hex(r["pc_va"]), _hex(r["ps4_symbol"].split("@")[-1]),
                             r["ps4_symbol"]))
    with prior.open(encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    for r in csv.DictReader(lines, delimiter="\t"):
        if r["kind"] != "name":
            continue
        verdict, pc_va = r["verdict"], _hex(r["pc_va"])
        if verdict.startswith("holds") and "PS4 link unproved" not in verdict:
            m = re.search(r"PS4 (OnPacket_\w+) unique", verdict)
            sym = None
            if m:
                sym = "cSeedGameSvConnection::" + m.group(1)
            elif "unique tier-0 PS4 partner" in verdict:
                sym = r["value"]
            if sym is None:
                continue
            cands = ps4_by_name.get(sym, [])
            rows.append(link("T002 holds", r["role"], pc_va, cands[0] if len(cands) == 1 else None, sym))
        elif verdict.startswith("wrong"):
            ours = names.get(pc_va, "-")
            rows.append(CrossRow("T002 wrong", r["role"], pc_va, r["value"], ours,
                                 "reproduced" if ours == r["value"] else "not reproduced"))
    return rows


# --- T005e: the pipeline (seeds, propagation, role anchors), its precision check and negative control ---

Pair = tuple[int, int]


@dataclass
class Run:
    engine: engine.Result
    roles: roles.RoleResult

    def pairs(self) -> dict[Pair, str]:
        """Every accepted pair -> rule (seed, propagation, or the role rule)."""
        out = {p: a.source for p, a in self.engine.accepted.items()}
        out.update({p: r.rule for p, r in self.roles.pairs.items()})
        return out


def pipeline(facts: Facts, seeds: dict[int, int], t0: dict[int, str], prefixes: dict[int, list[str]]) -> Run:
    res = engine.run(facts, seeds)
    handlers = {p: frozenset([p]) for p, a in res.accepted.items() if a.source == "seed"}
    rr = roles.run(facts, handlers, set(res.accepted), t0, prefixes)
    add_anchored(facts, res, rr)
    return Run(res, rr)


def add_anchored(facts: Facts, res: engine.Result, rr: roles.RoleResult) -> anchored.AnchoredResult:
    """T013a: the anchored gap rule over every accepted pair; its pairs join the role pairs (rule
    ``anchored-gap``), so the precision check and the negative control cover them."""
    an = anchored.run(facts, set(res.accepted) | set(rr.pairs), rr.codec_sites)
    known = {p: r.roots for p, r in rr.pairs.items()}
    for p, (ws, why, it) in sorted(an.accepted.items(), key=lambda kv: (kv[1][2], kv[0])):
        roots = anchored.roots_of(res, known)  # earlier anchored pairs are witnesses of later ones
        known[p] = frozenset().union(*(roots(w) for w in ws))
        rr.pairs[p] = roles.RolePair(*p, anchored.RULE, tuple(f"{w[0]:#x}:{w[1]:#x}" for w in ws),
                                     known[p], why, "-", it)
    for p, fails in sorted(an.failed.items()):
        for g, why in fails:
            rr.listed.append(roles.Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", anchored.RULE, f"{g}: {why}"))
    rr.proposals[anchored.RULE] = len(an.accepted) + len(an.failed)
    rr.anchored = an
    return an


@dataclass(frozen=True)
class RolePrecisionRow:
    rng_seed: int
    seeds: int
    withheld: int
    derived_full: int  # role pairs of the full run
    dependent: int  # of those, depending on a withheld seed
    dependent_absent: int
    dependent_same: int  # reappeared with the same partner via other witnesses
    wrong: int  # pairs of the holdout run whose PC or PS4 side has another partner in the full run
    new: int  # pairs of the holdout run that the full run does not have (and that contradict nothing)
    derived_holdout: int
    detail: tuple[str, ...] = ()


def role_precision(facts: Facts, seeds: dict[int, int], t0: dict[int, str], prefixes: dict[int, list[str]],
                   full: Run, rng_seed: int, withheld: set[int] | None = None) -> RolePrecisionRow:
    """Withhold 20% of the seeds (fixed RNG seed): every derived pair that depends on a withheld seed must
    be absent or come back with the same partner; no pair of the holdout run may contradict the full run."""
    if withheld is None:
        withheld = holdout(seeds, rng_seed)
    gone = {(k, seeds[k]) for k in withheld}
    part = pipeline(facts, {k: v for k, v in seeds.items() if k not in withheld}, t0, prefixes)
    fp, pp = full.pairs(), part.pairs()
    f_pc = {p[0]: p[1] for p in fp}
    f_ps4 = {p[1]: p[0] for p in fp}
    p_pc = {p[0]: p[1] for p in pp}
    p_ps4 = {p[1]: p[0] for p in pp}
    dep = [p for p, r in full.roles.pairs.items() if r.roots & gone]
    absent = sum(1 for p in dep if p[0] not in p_pc and p[1] not in p_ps4)
    same = sum(1 for p in dep if p_pc.get(p[0]) == p[1])
    detail: list[str] = []
    wrong = new = 0
    for p, rule in sorted(pp.items()):
        a, b = f_pc.get(p[0]), f_ps4.get(p[1])
        if (a is not None and a != p[1]) or (b is not None and b != p[0]):
            wrong += 1
            detail.append(f"wrong {rule} {p[0]:#x}:{p[1]:#x} (full: {a and hex(a)} / {b and hex(b)})")
        elif p not in fp:
            new += 1
            detail.append(f"new {rule} {p[0]:#x}:{p[1]:#x}")
    return RolePrecisionRow(rng_seed, len(seeds), len(withheld), len(full.roles.pairs), len(dep), absent, same,
                            wrong, new, len(part.roles.pairs), tuple(detail))


def derangement(seeds: dict[int, int], rng_seed: int) -> dict[int, int]:
    """The seeds with their PS4 side shuffled so that no PC handler keeps its partner (fixed RNG seed)."""
    keys = sorted(seeds)
    vals = [seeds[k] for k in keys]
    if len(vals) < 2:
        return {}
    r = random.Random(rng_seed)
    while True:
        sh = vals[:]
        r.shuffle(sh)
        if all(a != b for a, b in zip(vals, sh, strict=True)):
            return dict(zip(keys, sh, strict=True))


@dataclass(frozen=True)
class ControlRow:
    rng_seed: int
    seeds: int
    seeds_passing_c: int
    contexts_equal: int
    contexts_embedded: int
    proposals: dict
    accepted: dict
    accepted_agree_real: int
    accepted_wrong: int
    detail: tuple[str, ...] = ()


def negative_control(facts: Facts, seeds: dict[int, int], t0: dict[int, str], prefixes: dict[int, list[str]],
                     full: Run, rng_seed: int) -> ControlRow:
    """Pair each PC handler with a random other PS4 handler and run the role anchors on that."""
    run = pipeline(facts, derangement(seeds, rng_seed), t0, prefixes)
    fp = full.pairs()
    acc: dict[str, int] = {}
    agree = wrong = 0
    detail = []
    for p, r in sorted(run.roles.pairs.items()):
        acc[r.rule] = acc.get(r.rule, 0) + 1
        ok = fp.get(p) is not None
        agree += ok
        wrong += not ok
        detail.append(f"{r.rule} {p[0]:#x}:{p[1]:#x} {'= real run' if ok else 'not in the real run'}")
    ctx = run.roles.contexts
    return ControlRow(rng_seed, len(seeds), sum(1 for a in run.engine.accepted.values() if a.source == "seed"),
                      ctx.get("equal", 0), ctx.get("embedded", 0), dict(run.roles.proposals), acc, agree, wrong,
                      tuple(detail))


# T005b examples (§ 1.1 pairs 1-2, § 3; V there): (key, PC va, PS4 va or PS4 symbol)
T005B_EXAMPLES = (
    ("pair 1 array reader", 0x772020, 0x1A2A2B0),
    ("pair 1 element reader", 0x7720E0, 0x1A2A530),
    ("pair 2 element reader", 0x7584B0, "nPacket::Read_CDataAchieveRewardCommon_"),
)


def crosscheck_t005b(facts: Facts, full: Run) -> list[CrossRow]:
    """T005b's element-reader examples against the run (T005b gives counts, not the 117-pair list)."""
    by_pc = {p[0]: p[1] for p in full.pairs()}
    rows = []
    for key, pc_va, ps4 in T005B_EXAMPLES:
        if isinstance(ps4, str):
            vas = [f.va for f in facts.ps4.values() if f.name == ps4]
            ps4 = vas[0] if len(vas) == 1 else None
        got = by_pc.get(pc_va)
        exp = f"{ps4:#x} {facts.ps4[ps4].name}" if ps4 in facts.ps4 else f"{ps4}"
        paired = f"{got:#x} {facts.ps4[got].name}" if got is not None else "-"
        result = "not paired" if got is None else ("agree" if got == ps4 else "disagree")
        rows.append(CrossRow("T005b example", key, pc_va, exp, paired, result))
    return rows

"""T013a: the anchored gap rule (T012 § 3, variant A) after the role anchors.

Parents: every accepted pair (propagation and role rules). Anchors in a parent's two call lists:

- a call whose target is in an accepted pair (the T005 token, :func:`propagate.gap_proposals`);
- a PC codec call site aligned by rule 3 (``RoleResult.codec_sites``, "agree" sites only) and the PS4 call at
  its aligned PS4 site: both carry the same token;
- every other codec call (PC ``codecs.pc_codec`` target, PS4 ``nPacket::Read_*``/``Write_*``): an anchor that
  never aligns, so it blocks its gap.

The 1:1 gaps propose callee pairs; a proposal is accepted only under gates (a)-(d) (``engine._evaluate``),
unique over every proposal and accepted pair (b). Accepted pairs become anchors and parents of the next
iteration, to a fixed point; an accepted pair that loses uniqueness is banned and the stage restarts.

Own code (no library fits): the token maps over the dump's call lists; the alignment is
:func:`propagate.align`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from . import codecs, engine, gates
from .model import Facts
from .propagate import GapStats, Pair, gap_proposals

RULE = "anchored-gap"
_PS4_BLOCK = -(1 << 62)  # codec tokens are negative: pair tokens are PC VAs (positive)
_PC_BLOCK = -(1 << 61)


@dataclass
class AnchoredResult:
    accepted: dict[Pair, tuple[tuple[Pair, ...], str, int]] = field(default_factory=dict)  # witnesses, gates, it
    failed: dict[Pair, list[tuple[str, str]]] = field(default_factory=dict)
    rejected_b: set[Pair] = field(default_factory=set)
    stats: GapStats = field(default_factory=GapStats)
    codec_anchor_sites: int = 0
    restarts: int = 0


def codec_tokens(facts: Facts, codec_sites: dict[int, frozenset[int]]) -> tuple[dict[int, int], dict[int, int]]:
    """(PC call site -> token, PS4 call site -> token) for every codec call of the dumped functions."""
    ps4_of: dict[int, int] = {}
    for pc_site, s4 in codec_sites.items():
        for x in s4:
            ps4_of[x] = -pc_site
    pc_tok: dict[int, int] = {}
    for f in facts.pc.values():
        for c in f.calls:
            if c.target is not None and codecs.pc_codec(facts, c.target) is not None:
                pc_tok[c.site] = -c.site if c.site in codec_sites else _PC_BLOCK - c.site
    ps4_tok: dict[int, int] = {}
    for f in facts.ps4.values():
        for c in f.calls:
            if c.target is not None and codecs.codec_of(facts, "ps4", c.target) is not None:
                ps4_tok[c.site] = ps4_of.get(c.site, _PS4_BLOCK - c.site)
    return pc_tok, ps4_tok


def run(facts: Facts, accepted: set[Pair], codec_sites: dict[int, frozenset[int]],
        max_iterations: int = 1000, max_restarts: int = 100) -> AnchoredResult:
    """Pairs the anchored gap rule adds to ``accepted`` (module docstring)."""
    folded = gates.fold_groups(facts.pc)
    pc_tok, ps4_tok = codec_tokens(facts, codec_sites)
    banned: set[Pair] = set()
    for restart in range(max_restarts + 1):
        res = _pass(facts, accepted, pc_tok, ps4_tok, folded, banned, max_iterations)
        if res is not None:
            res.restarts = restart
            res.codec_anchor_sites = len(codec_sites)
            return res
    raise RuntimeError("anchored gap rule: too many restarts")


def _pass(facts, accepted, pc_tok, ps4_tok, folded, banned, max_iterations) -> AnchoredResult | None:
    out = AnchoredResult(rejected_b=set(banned))
    for it in range(1, max_iterations + 1):
        allp = set(accepted) | set(out.accepted)
        pc_side = {p[0]: p[0] for p in allp}
        ps4_side = {p[1]: p[0] for p in allp}
        ledger: dict[Pair, set[Pair]] = {}
        stats = GapStats()
        for w in sorted(allp):
            pc, ps4 = facts.pc.get(w[0]), facts.ps4.get(w[1])
            if pc is None or ps4 is None:
                continue
            props, st = gap_proposals(pc, ps4, pc_side, ps4_side, facts.dwarf_inlines.get(w[1]),
                                      pc_tok, ps4_tok)
            stats.merge(st)
            for p in props:
                if p not in allp:
                    ledger.setdefault(p, set()).add(w)
        for ps in engine.find_conflicts(set(ledger) | allp).values():
            out.rejected_b.update(p for p in ps if p not in accepted)
        lost = [p for p in out.accepted if p in out.rejected_b]
        if lost:
            banned.update(lost)
            return None
        new: list[Pair] = []
        out.failed = {}
        for p in sorted(ledger):
            why = engine._evaluate(facts, p, ledger[p], folded, out.rejected_b)
            if why is None:
                new.append(p)
            else:
                out.failed[p] = why
        out.stats = stats
        if not new:
            return out
        for p in new:
            _, wa = gates.gate_a(facts.pc[p[0]], facts.ps4[p[1]], ledger[p])
            _, wc = gates.gate_c(facts, *p)
            out.accepted[p] = (tuple(sorted(ledger[p])), f"a={wa}; b=unique; c={wc}; d=ok", it)
    raise RuntimeError("anchored gap rule did not reach a fixed point")


def roots_of(engine_res: engine.Result, role_roots: dict[Pair, frozenset[Pair]]) -> Callable[[Pair], frozenset]:
    """Seed handler pairs a pair depends on: a seed itself, a propagation pair its witnesses' roots, a role
    pair its own ``roots``."""
    memo: dict[Pair, frozenset[Pair]] = {}

    def get(p: Pair) -> frozenset[Pair]:
        if p in memo:
            return memo[p]
        memo[p] = frozenset()  # cycle guard
        if p in role_roots:
            r = role_roots[p]
        else:
            a = engine_res.accepted.get(p)
            if a is None:
                r = frozenset()
            elif a.source == "seed":
                r = frozenset([p])
            else:
                r = frozenset().union(*(get(w) for w in a.witnesses))
        memo[p] = r
        return r

    return get

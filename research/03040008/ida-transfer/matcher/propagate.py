"""Rule 3: anchored call-site alignment and gap proposals.

Own code (no library fits): difflib.SequenceMatcher finds longest matching blocks greedily with a junk
heuristic, so with repeated anchors (the same codec pair called many times) it picks one of several
equal alignments silently. Here an alignment is used only when it is forced:

1. the anchor token sequences of the two bodies are equal: anchors align in order;
2. otherwise only anchors whose token occurs once on each side and crosses no other such token align,
   and between two of those the anchor runs align only where they are equal token for token.

Any call left in a gap whose target is already paired (an anchor that did not align) blocks the gap.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .model import Call, Func

Pair = tuple[int, int]


@dataclass
class GapStats:
    even_one: int = 0  # gaps with exactly one unpaired call each side (proposals)
    blocked: int = 0  # gaps holding an anchor-capable call that did not align
    uneven: Counter = field(default_factory=Counter)  # (pc calls, ps4 calls) -> count
    uneven_by_inline: int = 0  # uneven only because of PS4 inlined subroutines (not used)
    even_other: Counter = field(default_factory=Counter)  # even gaps with 0 or >= 2 calls each side

    def merge(self, o: GapStats) -> None:
        self.even_one += o.even_one
        self.blocked += o.blocked
        self.uneven.update(o.uneven)
        self.uneven_by_inline += o.uneven_by_inline
        self.even_other.update(o.even_other)


def _token(c: Call, side: dict[int, int]) -> int | None:
    """Pair id of the call's target if it is already paired (keyed by the PC va of the pair)."""
    if c.target is None:
        return None
    return side.get(c.target)


def align(a: list[int | None], b: list[int | None]) -> list[tuple[int, int]]:
    """Aligned (index in a, index in b) anchor positions; None entries are not anchors."""
    ai = [(i, t) for i, t in enumerate(a) if t is not None]
    bi = [(j, t) for j, t in enumerate(b) if t is not None]
    if [t for _, t in ai] == [t for _, t in bi]:
        return [(i, j) for (i, _), (j, _) in zip(ai, bi, strict=True)]
    ca, cb = Counter(t for _, t in ai), Counter(t for _, t in bi)
    uniq = sorted(t for t in ca if ca[t] == 1 and cb.get(t) == 1)
    pa = {t: k for k, (_, t) in enumerate(ai) if t in uniq}
    pb = {t: k for k, (_, t) in enumerate(bi) if t in uniq}
    fixed = [t for t in uniq
             if all((pa[t] < pa[u]) == (pb[t] < pb[u]) for u in uniq if u != t)]
    fixed.sort(key=lambda t: pa[t])
    out: list[tuple[int, int]] = []
    prev_a, prev_b = -1, -1
    for t in [*fixed, None]:
        na = pa[t] if t is not None else len(ai)
        nb = pb[t] if t is not None else len(bi)
        run_a, run_b = ai[prev_a + 1:na], bi[prev_b + 1:nb]
        if [x for _, x in run_a] == [x for _, x in run_b]:
            out.extend((i, j) for (i, _), (j, _) in zip(run_a, run_b, strict=True))
        if t is not None:
            out.append((ai[na][0], bi[nb][0]))
        prev_a, prev_b = na, nb
    return out


def gap_proposals(pc: Func, ps4: Func, pc_side: dict[int, int], ps4_side: dict[int, int],
                  ps4_inlines: list[int] | None = None) -> tuple[list[Pair], GapStats]:
    """Callee pairs proposed by (pc, ps4): the lone unpaired call of each side in each anchored gap.

    pc_side / ps4_side map an already paired function va to its pair id (the same id on both sides)."""
    a = [_token(c, pc_side) for c in pc.calls]
    b = [_token(c, ps4_side) for c in ps4.calls]
    anchors = align(a, b)
    stats = GapStats()
    out: list[Pair] = []
    bounds = [(-1, -1), *anchors, (len(a), len(b))]
    for (i0, j0), (i1, j1) in zip(bounds, bounds[1:], strict=False):
        ga, gb = list(range(i0 + 1, i1)), list(range(j0 + 1, j1))
        if any(a[i] is not None for i in ga) or any(b[j] is not None for j in gb):
            stats.blocked += 1
            continue
        if len(ga) == len(gb) == 1:
            stats.even_one += 1
            ca, cb = pc.calls[ga[0]], ps4.calls[gb[0]]
            if ca.target is not None and cb.target is not None:
                out.append((ca.target, cb.target))
        elif len(ga) == len(gb):
            stats.even_other[len(ga)] += 1
        else:
            stats.uneven[(len(ga), len(gb))] += 1
            if ps4_inlines:
                lo = ps4.calls[j0].site if j0 >= 0 else ps4.va
                hi = ps4.calls[j1].site if j1 < len(b) else ps4.va + ps4.size
                n_inl = sum(1 for x in ps4_inlines if lo < x < hi)
                if n_inl and len(ga) == len(gb) + n_inl:
                    stats.uneven_by_inline += 1
    return out, stats

"""T005e role anchors (T005b § 6 rules 1-4) over accepted handler pairs.

Rule 1 reader anchor, rule 2 element-reader anchor (recursive, global uniqueness), rule 3 codec-position
naming (no pairs), rule 4 listener-slot anchor. Every derived pair carries its rule, its witnesses (the
contexts it was read from) and the seed handler pairs it depends on (``roots``, for the precision check).
Gates: (b) uniqueness over every proposal of the run and against the already accepted pairs, (c) shape,
(d) not trivial (T005 gates, `gates.py`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import codecs, gates, tier0
from .codecs import Bracket, Flat
from .model import Facts

Pair = tuple[int, int]

PS4_HANDLER = re.compile(r"^cSeed\w*Connection::OnPacket_(\w+)$")
PS4_READ_PACKET = re.compile(r"(?:^|::)CPacket_(\w+)::ReadPacket$")
PS4_SENDER = re.compile(r"^cSeed\w*Connection::Send_(\w+)$")
PS4_LOGIN_SENDER = re.compile(r"::Send_C2L_")
RESERVE = "sNetworkExt::reserveNetworkErrorDialog"
# PC login-connection code (T005b § 4, § 5): requesters and senders here reuse game slot numbers and keys.
PC_LOGIN_RANGE = (0x88A600, 0x88AC00)


@dataclass
class RolePair:
    pc: int
    ps4: int
    rule: str  # reader | element-reader | listener-requester | listener-sender
    witnesses: tuple[str, ...]
    roots: frozenset[Pair]
    gate_results: str
    flags: str = "-"
    iteration: int = 0


@dataclass
class Context:
    """A reader (or element-reader) pair whose codec trees are compared."""

    pc: int
    ps4: int
    header: bool
    roots: frozenset[Pair]
    label: str


@dataclass
class Occurrence:
    ps4: int
    pc: int | None
    ctx: Context
    mode: str  # equal | embedded
    identified: bool = True  # see unidentified()


@dataclass
class Listing:
    candidate: str
    rule: str
    detail: str


@dataclass
class RoleResult:
    pairs: dict[Pair, RolePair] = field(default_factory=dict)
    listed: list[Listing] = field(default_factory=list)
    conflicts: dict[tuple[str, int], set[Pair]] = field(default_factory=dict)
    callsites: list[list[str]] = field(default_factory=list)
    contexts: dict[str, int] = field(default_factory=dict)  # context relation -> count
    proposals: dict[str, int] = field(default_factory=dict)  # rule -> proposals made
    inlined_on_ps4: list[Pair] = field(default_factory=list)  # handler pairs whose PS4 reader is inlined


# --- rule 1 -------------------------------------------------------------------------------------------

def _calls_codec(facts: Facts, va: int) -> bool:
    f = facts.pc.get(va)
    return f is not None and any(c.target is not None and codecs.pc_codec(facts, c.target) is not None
                                 for c in f.calls)


def pc_reader(facts: Facts, handler: int) -> tuple[int | None, str]:
    """The PC handler's unique callee that calls a codec directly or one level down."""
    f = facts.pc.get(handler)
    if f is None:
        return None, "handler not in the dump"
    if any(c.target is not None and codecs.pc_codec(facts, c.target) for c in f.calls):
        return None, "handler calls a codec itself"
    found: set[int] = set()
    unknown: set[int] = set()
    for c in f.calls:
        t = c.target
        if t is None or t in codecs.PC_SKIP_VA:
            continue
        g = facts.pc.get(t)
        if g is None:
            unknown.add(t)
            continue
        if g.name == codecs.PC_CALL_ON_PACKET or codecs.PC_SKIP_NAME.search(g.name):
            continue
        if _calls_codec(facts, t) or any(d.target is not None and _calls_codec(facts, d.target) for d in g.calls):
            found.add(t)
    if len(found) == 1 and not unknown:
        return found.pop(), "ok"
    if len(found) > 1:
        return None, "several callees reach codecs: " + " ".join(f"{v:#x}" for v in sorted(found))
    if unknown:
        return None, "callee not in the dump: " + " ".join(f"{v:#x}" for v in sorted(unknown))
    return None, "no callee reaches a codec"


def handler_name(facts: Facts, ps4_handler: int) -> str | None:
    m = PS4_HANDLER.match(facts.ps4[ps4_handler].name) if ps4_handler in facts.ps4 else None
    return m.group(1) if m else None


def ps4_reader(facts: Facts, handler: int) -> tuple[int | None, str]:
    """(va, 'call') when the PS4 handler calls exactly one CPacket_*::ReadPacket, (None, 'inlined') when
    it calls none, else (None, reason)."""
    f = facts.ps4.get(handler)
    if f is None:
        return None, "handler not in the dump"
    found = sorted({c.target for c in f.calls if c.target is not None
                    and PS4_READ_PACKET.search(codecs.ps4_name(facts, c.target) or "")})
    if not found:
        return None, "inlined"
    if len(found) > 1:
        return None, "several ReadPacket: " + " ".join(f"{v:#x}" for v in found)
    return found[0], "call"


def reader_anchor(facts: Facts, pc_handler: int, ps4_handler: int, pc_string: str | None,
                  prefix: list[str]) -> tuple[Pair | None, str]:
    """Rule 1. The PS4 ReadPacket class must be the PS4 handler's packet and one of the names the PC
    handler's OnPacket_ string allows (tier0.candidate_names); the PC reader must be unique."""
    r4, how = ps4_reader(facts, ps4_handler)
    if r4 is None:
        return None, f"PS4 reader {how}"
    cls = PS4_READ_PACKET.search(codecs.ps4_name(facts, r4) or "").group(1)  # type: ignore[union-attr]
    name = handler_name(facts, ps4_handler)
    if cls != name:
        return None, f"PS4 ReadPacket class {cls} is not the handler's packet {name}"
    if pc_string is None:
        return None, "PC handler has no OnPacket_ string"
    if re.sub(r"^(?:S2C|L2C)_", "", cls) not in tier0.candidate_names(pc_string, prefix):
        return None, f"PS4 class {cls} is not a name of the PC string {pc_string}"
    rpc, why = pc_reader(facts, pc_handler)
    if rpc is None:
        return None, f"PC reader: {why}"
    return (rpc, r4), "ok"


# --- rule 2 -------------------------------------------------------------------------------------------

@dataclass
class Compared:
    relation: str  # equal | embedded | ambiguous-embedding | other | gap | header
    pc: Flat
    ps4: Flat
    pc_off: int = 0
    ps4_off: int = 0
    embedding: list[int] | None = None  # PS4 body index -> PC body index


class Trees:
    """Cache of flattened codec trees (read mode) for one run."""

    def __init__(self, facts: Facts) -> None:
        self.facts = facts
        self._c: dict[tuple[str, int], Flat] = {}

    def get(self, side: str, va: int) -> Flat:
        k = (side, va)
        if k not in self._c:
            self._c[k] = codecs.flatten(self.facts, side, va)
        return self._c[k]


def header_offsets(ta: list[str], tb: list[str]) -> tuple[int, int] | None:
    """Header rule (T005b § 2.3): PC ``44`` (s32 error, s32 result) <-> PS4 ``24`` (u16 error, s32 result),
    or PS4 ``2`` when its second token is not a 4 (no result field, e.g. GET_REAL_TIME_RES)."""
    if ta[:2] != ["4", "4"] or tb[:1] != ["2"]:
        return None
    return 2, (2 if tb[1:2] == ["4"] else 1)


def body(fl: Flat, side: str) -> tuple[str, ...] | None:
    """A packet reader's body tokens after the header, or None (gap or no header)."""
    if fl.gaps:
        return None
    t = fl.tokens
    if side == "pc":
        return tuple(t[2:]) if t[:2] == ["4", "4"] else None
    if t[:1] != ["2"]:
        return None
    return tuple(t[2:]) if t[1:2] == ["4"] else tuple(t[1:])


def compare(facts: Facts, ctx: Context, trees: Trees | None = None) -> Compared:
    trees = trees or Trees(facts)
    a = trees.get("pc", ctx.pc)
    b = trees.get("ps4", ctx.ps4)
    if a.gaps or b.gaps:
        return Compared("gap", a, b)
    ta, tb = a.tokens, b.tokens
    pa = pb = 0
    if ctx.header:
        off = header_offsets(ta, tb)
        if off is None:
            return Compared("header", a, b)
        pa, pb = off
    body_a, body_b = ta[pa:], tb[pb:]
    if body_a == body_b:
        return Compared("equal", a, b, pa, pb, list(range(len(body_b))))
    n = codecs.count_embeddings(body_b, body_a)
    if n == 1:
        return Compared("embedded", a, b, pa, pb, codecs.leftmost_embedding(body_b, body_a))
    return Compared("ambiguous-embedding" if n > 1 else "other", a, b, pa, pb)


def _pc_partner(cmp: Compared, br: Bracket) -> int | None:
    e = cmp.embedding
    assert e is not None
    a, b = br.start - cmp.ps4_off, br.end - cmp.ps4_off
    if a < 0 or b <= a:
        return None
    lo, hi = e[a], e[b - 1]
    left = e[a - 1] if a > 0 else -1
    right = e[b] if b < len(e) else None
    best: Bracket | None = None
    for p in cmp.pc.brackets:
        s, t = p.start - cmp.pc_off, p.end - cmp.pc_off
        if s < 0 or not (s <= lo and t > hi and left < s and (right is None or right >= t)):
            continue
        if best is None or p.depth < best.depth:
            best = p
    return best.va if best else None


def occurrences(facts: Facts, ctx: Context, cmp: Compared) -> list[Occurrence]:
    if cmp.embedding is None:
        return []
    out = []
    for br in cmp.ps4.brackets:
        if not codecs.PS4_ELEMENT_READER.match(codecs.ps4_name(facts, br.va) or ""):
            continue
        if br.start < cmp.ps4_off:
            continue
        out.append(Occurrence(br.va, _pc_partner(cmp, br), ctx, cmp.relation))
    return out


@dataclass
class Universe:
    """Every packet reader of each side with its header-stripped body: PC = the reader of each table
    callback, PS4 = the ReadPacket (or, inlined, the handler itself) of each ``OnPacket_`` handler."""

    pc: dict[int, tuple[str, ...]]
    ps4: dict[int, tuple[str, ...]]


def universe(facts: Facts, trees: Trees) -> Universe:
    pc: dict[int, tuple[str, ...]] = {}
    for cb in sorted(facts.table_callbacks):
        r, _ = pc_reader(facts, cb)
        if r is not None and (b := body(trees.get("pc", r), "pc")) is not None:
            pc[r] = b
    ps4: dict[int, tuple[str, ...]] = {}
    for f in sorted(facts.ps4.values(), key=lambda f: f.va):
        if not PS4_HANDLER.match(f.name):
            continue
        r, how = ps4_reader(facts, f.va)
        root = r if r is not None else (f.va if how == "inlined" else None)
        if root is not None and (b := body(trees.get("ps4", root), "ps4")) is not None:
            ps4[root] = b
    return Universe(pc, ps4)


def _subseq(small: tuple[str, ...], big: tuple[str, ...]) -> bool:
    it = iter(big)
    return all(x in it for x in small)


def unidentified(facts: Facts, trees: Trees, uni: Universe, ctx: Context, occs: list[Occurrence]) -> set[Pair]:
    """Occurrence pairs of a packet-reader context that the widths do not identify.

    The context's equality (or unique embedding) is width evidence only. Any other reader whose widths fit
    the same partner is an alternative context: for an equal context a reader with the same body, for an
    embedded one also a PS4 reader whose body embeds in the PC body or a PC reader whose body contains the
    PS4 body; an occurrence pair (X, E) is identified
    only if no alternative context pairs X or E with a different function. Without this a wrong handler
    pair with equal short bodies names its element readers wrongly (T005e negative control)."""
    pairs = {(o.pc, o.ps4) for o in occs if o.pc is not None}
    if not pairs or not ctx.header:
        return set()
    ba, bb = uni.pc.get(ctx.pc), uni.ps4.get(ctx.ps4)
    if ba is None or bb is None:
        return set(pairs)
    loose = ba != bb  # an embedded context: embedded alternatives count too
    alts = [Context(ctx.pc, c, True, frozenset(), "alt") for c, y in uni.ps4.items()
            if c != ctx.ps4 and (y == ba or (loose and _subseq(y, ba)))]
    alts += [Context(d, ctx.ps4, True, frozenset(), "alt") for d, x in uni.pc.items()
             if d != ctx.pc and (x == bb or (loose and _subseq(bb, x)))]
    by_pc: dict[int, set[int]] = {}
    by_ps4: dict[int, set[int]] = {}
    for alt in alts:
        cmp = compare(facts, alt, trees)
        for o in occurrences(facts, alt, cmp):
            if o.pc is not None:
                by_pc.setdefault(o.pc, set()).add(o.ps4)
                by_ps4.setdefault(o.ps4, set()).add(o.pc)
    return {p for p in pairs if by_pc.get(p[0], {p[1]}) != {p[1]} or by_ps4.get(p[1], {p[0]}) != {p[0]}}


def callsite_rows(facts: Facts, cmp: Compared, ctx: Context) -> list[tuple[int, int, int, str, str, int]]:
    """Rule 3: (pc site, pc owner, pc codec, token, PS4 overload, PS4 site) per body position of an equal
    pair. Header positions are left out (their widths differ by design)."""
    if cmp.relation != "equal":
        return []
    out = []
    for la, lb in zip(cmp.pc.leaves[cmp.pc_off:], cmp.ps4.leaves[cmp.ps4_off:], strict=True):
        out.append((la.site, la.owner, la.codec, la.token, codecs.ps4_name(facts, lb.codec) or "?", lb.site))
    return out


# --- gates ---------------------------------------------------------------------------------------------

def gate_cd(facts: Facts, p: Pair, folded: dict[int, list[int]]) -> tuple[bool, str]:
    pc, ps4 = facts.pc.get(p[0]), facts.ps4.get(p[1])
    if pc is None or ps4 is None:
        return False, "record: " + ("PC" if pc is None else "PS4") + " function not in the dump"
    okc, wc = gates.gate_c(facts, *p)
    okd, wd = gates.gate_d(pc, ps4, folded)
    fails = ([f"c={wc}"] if not okc else []) + ([f"d={wd}"] if not okd else [])
    return (not fails), ("; ".join(fails) if fails else f"c={wc}; d=ok")


def _taken(accepted: dict[Pair, object]) -> tuple[dict[int, int], dict[int, int]]:
    return {p[0]: p[1] for p in accepted}, {p[1]: p[0] for p in accepted}


# --- rule 4 ---------------------------------------------------------------------------------------------

def _find(funcs, name: str) -> int | None:
    vas = [f.va for f in funcs.values() if f.name == name]
    return vas[0] if len(vas) == 1 else None


def pc_handler_slot(facts: Facts, handler: int) -> int | None:
    f = facts.pc.get(handler)
    cop = _find(facts.pc, codecs.PC_CALL_ON_PACKET)
    if f is None or cop is None:
        return None
    slots = {c.stack_const(0) for c in f.calls if c.target == cop}
    return slots.pop() if len(slots) == 1 and None not in slots else None


def requesters(facts: Facts, side: str) -> dict[int, set[int]]:
    """slot -> functions in the dump that call reserveNetworkErrorDialog with that constant slot."""
    funcs = facts.pc if side == "pc" else facts.ps4
    res = _find(funcs, RESERVE)
    out: dict[int, set[int]] = {}
    if res is None:
        return out
    for f in funcs.values():
        for c in f.calls:
            if c.target != res:
                continue
            v = c.stack_const(0) if side == "pc" else c.reg_const("rsi")
            if v is not None:
                out.setdefault(v, set()).add(f.va)
    return out


def _reach(funcs, va: int, depth: int = 2) -> set[int]:
    seen, frontier = {va}, {va}
    for _ in range(depth):
        nxt = set()
        for v in frontier:
            f = funcs.get(v)
            if f is None:
                continue
            nxt |= {c.target for c in f.calls if c.target is not None} - seen
        seen |= nxt
        frontier = nxt
    return seen


def pc_sender_keys(facts: Facts) -> dict[int, set[tuple[int, int, int]]]:
    """PC function -> the constant (group, id, sub) keys it passes to WritePacket."""
    wp = _find(facts.pc, codecs.PC_WRITE_PACKET)
    out: dict[int, set[tuple[int, int, int]]] = {}
    for f in facts.pc.values():
        for c in f.calls:
            if c.target == wp and wp is not None:
                g, i, s = c.stack_const(1), c.stack_const(2), c.stack_const(3)
                if None not in (g, i, s):
                    out.setdefault(f.va, set()).add((g, i, s))  # type: ignore[arg-type]
    return out


def payload(facts: Facts, side: str, sender: int) -> list[str] | None:
    """Payload write widths of a sender (after WritePacket on PC; after the 3 header u16 on PS4)."""
    fl = codecs.flatten(facts, side, sender, mode="write")
    if fl.gaps:
        return None
    if side == "pc":
        wp = _find(facts.pc, codecs.PC_WRITE_PACKET)
        sites = [c.site for c in facts.pc[sender].calls if c.target == wp]
        if len(sites) != 1:
            return None
        return [x.token for x in fl.leaves if x.top > sites[0]]
    t = fl.tokens
    return t[3:] if t[:3] == ["2", "2", "2"] else None


def inversions(slots: list[tuple[Pair, int, int]]) -> set[Pair]:
    """Handler pairs whose (PS4 slot, PC slot) breaks the monotone PS4 -> PC slot order with another one
    (both of an inverted couple are returned)."""
    bad: set[Pair] = set()
    for i, (h, a4, apc) in enumerate(slots):
        for g, b4, bpc in slots[i + 1:]:
            if (a4 - b4) * (apc - bpc) < 0:
                bad |= {h, g}
    return bad


def listener_anchor(facts: Facts, handler_pairs: list[Pair]) -> tuple[list[tuple[Pair, Pair, Pair, int, int]],
                                                                    list[Listing]]:
    """Rule 4 candidates (handler pair, requester pair, sender pair, ps4 slot, pc slot) and the refusals,
    before gates (b)-(d) and the monotone check."""
    req_pc, req_ps4 = requesters(facts, "pc"), requesters(facts, "ps4")
    keys = pc_sender_keys(facts)
    by_key: dict[tuple[int, int, int], set[int]] = {}
    for f, ks in keys.items():
        for k in ks:
            by_key.setdefault(k, set()).add(f)
    slot_pc = {h: pc_handler_slot(facts, h[0]) for h in handler_pairs}
    slot_ps4 = {h: facts.ps4_handler_slot.get(h[1]) for h in handler_pairs}
    use_pc: dict[int, int] = {}
    use_ps4: dict[int, int] = {}
    for h in handler_pairs:
        if slot_pc[h] is not None:
            use_pc[slot_pc[h]] = use_pc.get(slot_pc[h], 0) + 1
        if slot_ps4[h] is not None:
            use_ps4[slot_ps4[h]] = use_ps4.get(slot_ps4[h], 0) + 1
    out, listed = [], []

    def refuse(h: Pair, why: str) -> None:
        listed.append(Listing(f"pc:{h[0]:#x} ps4:{h[1]:#x}", "listener", why))

    for h in sorted(handler_pairs):
        key = facts.table_key.get(h[0])
        sp, s4 = slot_pc[h], slot_ps4[h]
        if key is None or key[2] != 2:
            refuse(h, f"handler key {key} is not a RES (sub 2)")
            continue
        if sp is None:
            refuse(h, "PC handler slot not read (no single constant callOnPacketFunc slot)")
            continue
        if s4 is None:
            refuse(h, "PS4 handler slot not in the dump (coverage gap)")
            continue
        if use_pc[sp] > 1 or use_ps4[s4] > 1:
            refuse(h, f"shared slot (PC {sp} x{use_pc[sp]}, PS4 {s4} x{use_ps4[s4]})")
            continue
        rp, r4 = req_pc.get(sp, set()), req_ps4.get(s4, set())
        if len(rp) != 1 or len(r4) != 1:
            refuse(h, f"requesters of the slot: PC {len(rp)}, PS4 {len(r4)} (need exactly one each)")
            continue
        rpc, rps4 = next(iter(rp)), next(iter(r4))
        spc = sorted(v for v in _reach(facts.pc, rpc) if v in keys)
        s4s = sorted(v for v in _reach(facts.ps4, rps4) if PS4_SENDER.match(codecs.ps4_name(facts, v) or ""))
        if len(spc) != 1 or len(s4s) != 1:
            refuse(h, f"senders reached: PC {len(spc)}, PS4 {len(s4s)} (need exactly one each)")
            continue
        sender_pc, sender_ps4 = spc[0], s4s[0]
        want = (key[0], key[1], 1)
        if keys[sender_pc] != {want}:
            refuse(h, f"PC sender {sender_pc:#x} keys {sorted(keys[sender_pc])} != {want}")
            continue
        if len(by_key.get(want, ())) != 1:
            refuse(h, f"key {want} has {len(by_key.get(want, ()))} senders")
            continue
        if any(PC_LOGIN_RANGE[0] <= v < PC_LOGIN_RANGE[1] for v in (rpc, sender_pc)) \
                or PS4_LOGIN_SENDER.search(codecs.ps4_name(facts, sender_ps4) or ""):
            refuse(h, "login manager range")
            continue
        wa, wb = payload(facts, "pc", sender_pc), payload(facts, "ps4", sender_ps4)
        if wa is None or wb is None or wa != wb:
            refuse(h, f"payload widths PC {''.join(wa) if wa is not None else '?'} "
                      f"PS4 {''.join(wb) if wb is not None else '?'}")
            continue
        out.append((h, (rpc, rps4), (sender_pc, sender_ps4), s4, sp))
    bad = inversions([(x[0], x[3], x[4]) for x in out])
    for x in out:
        if x[0] in bad:
            refuse(x[0], f"slot order inversion (PS4 {x[3]} -> PC {x[4]})")
    return [x for x in out if x[0] not in bad], listed


# --- the run ----------------------------------------------------------------------------------------------

def run(facts: Facts, handler_pairs: dict[Pair, frozenset[Pair]], accepted: set[Pair],
        pc_strings: dict[int, str], prefixes: dict[int, list[str]], max_iterations: int = 100) -> RoleResult:
    """``handler_pairs``: accepted handler pair -> its seed roots; ``accepted``: every pair already
    accepted (seeds, propagation) for gate (b); ``pc_strings`` / ``prefixes``: tier-0 strings and group
    prefixes for rule 1."""
    folded = gates.fold_groups(facts.pc)
    res = RoleResult()
    taken: set[Pair] = set(accepted)
    banned: set[Pair] = set()

    # rule 1 ----------------------------------------------------------------------------------------------
    proposals: dict[Pair, list[Pair]] = {}
    reader_ctx: list[Context] = []
    for h in sorted(handler_pairs):
        roots = handler_pairs[h]
        rpc, why_pc = pc_reader(facts, h[0])
        r4, how = ps4_reader(facts, h[1])
        if how == "inlined":
            res.inlined_on_ps4.append(h)
        if rpc is not None and (r4 is not None or how == "inlined"):
            reader_ctx.append(Context(rpc, r4 if r4 is not None else h[1], True, roots,
                                      f"{h[0]:#x}:{h[1]:#x}"))
        if how == "inlined":
            res.listed.append(Listing(f"pc:{h[0]:#x} ps4:{h[1]:#x}", "reader", "inlined on PS4: no reader pair"))
            continue
        g = facts.table_group.get(h[0])
        p, why = reader_anchor(facts, h[0], h[1], pc_strings.get(h[0]), prefixes.get(g, []) if g is not None else [])
        if p is None:
            res.listed.append(Listing(f"pc:{h[0]:#x} ps4:{h[1]:#x}", "reader", why))
            continue
        proposals.setdefault(p, []).append(h)
    res.proposals["reader"] = len(proposals)
    conf = _conflicts(set(proposals) | taken)
    for p in sorted(proposals):
        hs = proposals[p]
        if any(p in ps for ps in conf.values()):
            _note_conflicts(res, conf, p)
            res.listed.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "b", "reader conflict"))
            banned.add(p)
            continue
        ok, why = gate_cd(facts, p, folded)
        if not ok:
            res.listed.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "reader", why))
            continue
        roots = frozenset().union(*(handler_pairs[h] for h in hs))
        res.pairs[p] = RolePair(*p, "reader", tuple(f"{h[0]:#x}:{h[1]:#x}" for h in hs), roots,
                                f"b=unique; {why}")
        taken.add(p)

    # rule 2 ----------------------------------------------------------------------------------------------
    rel_count: dict[str, int] = {}
    seen_ctx = {(c.pc, c.ps4, c.header) for c in reader_ctx}
    contexts = list(reader_ctx)
    cache: dict[tuple[int, int, bool], Compared] = {}
    trees = Trees(facts)
    uni = universe(facts, trees)
    unident: dict[tuple[int, int, bool], set[Pair]] = {}
    for it in range(1, max_iterations + 1):
        occ: dict[int, list[Occurrence]] = {}
        rel_count = {}
        calls: list[tuple[tuple, Context]] = []
        for ctx in contexts:
            k = (ctx.pc, ctx.ps4, ctx.header)
            if k not in cache:
                cache[k] = compare(facts, ctx, trees)
                unident[k] = unidentified(facts, trees, uni, ctx, occurrences(facts, ctx, cache[k]))
            cmp = cache[k]
            rel_count[cmp.relation] = rel_count.get(cmp.relation, 0) + 1
            for o in occurrences(facts, ctx, cmp):
                o.identified = (o.pc, o.ps4) not in unident[k]
                occ.setdefault(o.ps4, []).append(o)
            calls.extend((row, ctx) for row in callsite_rows(facts, cmp, ctx))
        props: dict[Pair, list[Occurrence]] = {}
        incons: dict[int, set[int | None]] = {}
        for f4, os_ in occ.items():
            partners = {o.pc for o in os_}
            if len(partners) != 1 or None in partners:
                incons[f4] = partners
                continue
            props[(next(iter(partners)), f4)] = os_  # type: ignore[index]
        res.proposals["element-reader"] = len(props) + len(incons)
        conf = _conflicts(set(props) | taken)
        stale = [p for p, rp in res.pairs.items() if rp.rule == "element-reader"
                 and (p not in props or any(p in ps for ps in conf.values()))]
        if stale:
            # an accepted element pair lost uniqueness through a new context: ban it and start over
            banned.update(stale)
            for p in stale:
                del res.pairs[p]
                taken.discard(p)
            contexts = [c for c in contexts if (c.pc, c.ps4) not in set(stale)]
            seen_ctx = {(c.pc, c.ps4, c.header) for c in contexts}
            continue
        new = []
        listed_now: list[Listing] = []
        for f4, partners in sorted(incons.items()):
            ws = " ".join("-" if v is None else f"{v:#x}" for v in sorted(partners, key=lambda v: v or -1))
            listed_now.append(Listing(f"ps4:{f4:#x}", "b",
                                      f"element reader pairs differently across {len(occ[f4])} occurrence(s): {ws}"))
        for p in sorted(props):
            if p in res.pairs:
                continue
            if p in banned:
                listed_now.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "b", "element reader lost uniqueness"))
                continue
            if p in taken:
                continue
            if any(p in ps for ps in conf.values()):
                _note_conflicts(res, conf, p)
                listed_now.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "b", "element reader conflict"))
                continue
            if not any(o.identified for o in props[p]):
                listed_now.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "b",
                                          f"widths do not identify the pair: another reader's widths fit and pair "
                                          f"it differently ({len(props[p])} occurrence(s))"))
                continue
            ok, why = gate_cd(facts, p, folded)
            if not ok:
                listed_now.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "element-reader", why))
                continue
            new.append((p, why))
        for p, why in new:
            os_ = props[p]
            roots = frozenset().union(*(o.ctx.roots for o in os_))
            ext = all(o.mode == "embedded" for o in os_)
            res.pairs[p] = RolePair(*p, "element-reader", tuple(sorted({o.ctx.label for o in os_})), roots,
                                    f"b=unique over {len(os_)} occurrence(s), "
                                    f"{sum(o.identified for o in os_)} identified; {why}",
                                    "season3-extended" if ext else "-", it)
            taken.add(p)
            key = (p[0], p[1], False)
            if key not in seen_ctx:
                seen_ctx.add(key)
                contexts.append(Context(p[0], p[1], False, roots, f"{p[0]:#x}:{p[1]:#x}"))
        if not new:
            res.listed.extend(listed_now)
            res.callsites = _callsite_table(calls)
            break
    else:
        raise RuntimeError("element-reader anchors did not reach a fixed point")
    res.contexts = rel_count

    # rule 4 ----------------------------------------------------------------------------------------------
    cands, listed = listener_anchor(facts, sorted(handler_pairs))
    res.listed.extend(listed)
    res.proposals["listener"] = len(cands)
    props4: dict[Pair, tuple[str, Pair]] = {}
    for h, rq, sd, _s4, _sp in cands:
        props4[rq] = ("listener-requester", h)
        props4[sd] = ("listener-sender", h)
    conf = _conflicts(set(props4) | taken)
    for p in sorted(props4):
        rule, h = props4[p]
        if any(p in ps for ps in conf.values()):
            _note_conflicts(res, conf, p)
            res.listed.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", "b", f"{rule} conflict"))
            continue
        ok, why = gate_cd(facts, p, folded)
        if not ok:
            res.listed.append(Listing(f"pc:{p[0]:#x} ps4:{p[1]:#x}", rule, why))
            continue
        res.pairs[p] = RolePair(*p, rule, (f"{h[0]:#x}:{h[1]:#x}",), handler_pairs[h], f"b=unique; {why}")
        taken.add(p)
    return res


def _conflicts(pairs: set[Pair]) -> dict[tuple[str, int], set[Pair]]:
    by_pc: dict[int, set[Pair]] = {}
    by_ps4: dict[int, set[Pair]] = {}
    for p in pairs:
        by_pc.setdefault(p[0], set()).add(p)
        by_ps4.setdefault(p[1], set()).add(p)
    out = {("pc", v): s for v, s in by_pc.items() if len(s) > 1}
    out.update({("ps4", v): s for v, s in by_ps4.items() if len(s) > 1})
    return out


def _note_conflicts(res: RoleResult, conf, p: Pair) -> None:
    for k, ps in conf.items():
        if p in ps:
            res.conflicts.setdefault(k, set()).update(ps)


def _callsite_table(calls: list[tuple[tuple, Context]]) -> list[list[str]]:
    by_site: dict[int, dict] = {}
    for (site, owner, codec, token, ps4_overload, _ps4_site), ctx in calls:
        d = by_site.setdefault(site, {"owner": owner, "codec": codec, "token": token, "names": set(),
                                      "ctx": set()})
        d["names"].add(ps4_overload)
        d["ctx"].add(ctx.label)
    rows = []
    for site in sorted(by_site):
        d = by_site[site]
        names = sorted(d["names"])
        rows.append([f"{site:#x}", f"{d['owner']:#x}", f"{d['codec']:#x}", d["token"], " ".join(names),
                     str(len(d["ctx"])), "agree" if len(names) == 1 else "ambiguous"])
    return rows

"""Repair the PC 03040008 handler-table callbacks that are not IDA function starts (spec 007 T004c).

Run inside IDA (ida-mcp ``execute_python``) with one call, dry run by default::

    exec(open(path).read(), {"OUT": "D:/.../repair-dryrun.jsonl", "APPLY": False})

Optional global ``EXTRACT_IDA``: path of ``extract_ida.py`` (the handler table is read with its
``_ida_pc_table``; default: beside this file, else the repository path below).

For each proved table callback (computed from the table) that is not a function start:

1. decode linearly from the callback to the ``ret``/``jmp`` that ends the body (no pending
   in-body branch target), refusing undecodable bytes, traps, indirect jumps, branches out of the
   body and running into another function's start (:func:`decode_walk`);
2. inside a function: the bytes between the enclosing start and the callback must be unreferenced
   and padding or the tail of an instruction that crosses the callback (:func:`gap_check`), and the
   enclosing function must end where the decoded body ends;
3. no decoded instruction may lie in another function.

Only when every check passes and ``APPLY`` is true: write the undo record (before-state of items,
function chunks, names and comments over the affected range) to ``OUT`` and flush it, undefine
exactly the conflicting items, create the decoded instructions, move the enclosing start
(``ida_funcs.set_func_start``) or create the function (``ida_funcs.add_func`` with IDA choosing the
end), wait for auto-analysis of the range, and read back: the function starts at the callback,
ends at the decoded body end, and no other function nearby changed bounds.

``OUT`` gets a header, one ``result`` line per callback (``already-ok``, ``would-repair``,
``repaired``, ``refused`` with the failed check, or ``failed`` with the read-back check), one
``undo`` line before each applied repair, and a ``summary``. Nothing is ever forced: a refusal stays
for the coordinator. Names stay where they are (a name at a moved enclosing start is recorded, not
moved). The pure helpers are unit-tested in ``tests/test_repair_functions.py`` with fakes.
"""

from __future__ import annotations

import json
import os

SCRIPT_VERSION = "1"
DEFAULT_EXTRACT_IDA = "D:/ddon-data/research/03040008/ida-transfer/extract_ida.py"
MAX_INSNS = 4000
MAX_SPAN = 0x4000  # a branch target farther than this from the callback leaves the body
NEIGHBOURHOOD = 0x1000  # functions this close to the repaired range must keep their bounds

# Padding forms the compiler emits between functions (int3, nop and multi-byte nops).
PADDING_SEQUENCES = tuple(bytes.fromhex(h) for h in (
    "cc", "90", "6690", "8bff", "8bc0", "8bc9", "8bd2", "8bdb", "8bf6", "8bed", "8d4000", "8d4900",
    "8d5200", "8d5b00", "8d6d00", "8d7600", "8d642400", "8d742600", "8d9b00000000", "8da42400000000",
    "8db600000000", "8dbf00000000", "0f1f00", "0f1f4000", "0f1f440000", "660f1f440000",
    "0f1f8000000000", "0f1f840000000000",
))


# --- pure helpers -------------------------------------------------------------------------------

def decode_walk(start: int, decode, is_foreign_start, max_insns: int = MAX_INSNS,
                max_span: int = MAX_SPAN) -> dict:
    """Decode the body that begins at ``start``.

    ``decode(ea)`` returns None (undecodable) or ``{"ea", "size", "kind", "target"}`` with kind
    ``ret``, ``jmp`` (direct), ``jmp_indirect``, ``jcc``, ``call``, ``trap`` or ``other``;
    ``is_foreign_start(ea)`` is true where another function starts. The body ends at a ``ret`` or
    an unconditional ``jmp`` once no in-body branch target lies at or after the next address.
    Returns ``{"ok": True, "end", "insns"}`` or ``{"ok": False, "check", "at", "insns"}``.
    """
    insns: list[dict] = []
    ea = start
    reach = start  # furthest in-body branch target seen

    def refuse(check, at):
        return {"ok": False, "check": check, "at": at, "insns": insns}

    while True:
        if len(insns) >= max_insns:
            return refuse("too_long", ea)
        if ea != start and is_foreign_start(ea):
            return refuse("runs_into_function", ea)
        ins = decode(ea)
        if ins is None or ins.get("size", 0) <= 0:
            return refuse("undecodable", ea)
        if ins["kind"] == "trap":
            return refuse("trap_in_body", ea)
        if ins["kind"] == "jmp_indirect":
            return refuse("indirect_jump", ea)
        insns.append(ins)
        nxt = ea + ins["size"]
        kind, target = ins["kind"], ins.get("target")
        in_body = target is not None and start <= target < start + max_span and not is_foreign_start(target)
        if kind == "jcc":
            if not in_body:
                return refuse("branch_out_of_body", ea)
            reach = max(reach, target)
        elif kind == "jmp" and in_body:
            reach = max(reach, target)
        if kind in ("ret", "jmp") and reach < nxt:
            return {"ok": True, "end": nxt, "insns": insns}
        ea = nxt


def is_padding(raw: bytes) -> bool:
    """True when ``raw`` is a concatenation of :data:`PADDING_SEQUENCES` (empty counts)."""
    ok = [False] * (len(raw) + 1)
    ok[0] = True
    for i in range(len(raw)):
        if ok[i]:
            for seq in PADDING_SEQUENCES:
                if raw.startswith(seq, i):
                    ok[i + len(seq)] = True
    return ok[len(raw)]


def gap_check(enc_start: int, cb: int, gap: bytes, heads, referenced) -> dict:
    """Check the bytes ``[enc_start, cb)`` an enclosing function would give up.

    ``heads`` are the defined items ``(ea, size)`` that start in the gap; ``referenced`` the gap
    addresses with a non-flow xref. Bytes before the first item crossing ``cb`` must be padding;
    from that item on they are the tail of a misdecoded instruction.
    """
    if len(gap) != cb - enc_start:
        return {"ok": False, "check": "gap_unreadable"}
    if referenced:
        return {"ok": False, "check": "gap_referenced", "at": sorted(referenced)}
    crossing = [h for h, size in heads if enc_start <= h < cb and h + size > cb]
    plain_end = min(crossing) if crossing else cb
    if not is_padding(gap[: plain_end - enc_start]):
        return {"ok": False, "check": "gap_not_padding", "bytes": gap.hex()}
    return {"ok": True, "misdecoded": min(crossing) if crossing else None}


def conflicting_items(items, decoded, cb: int, end: int) -> list[dict]:
    """Defined items that overlap ``[cb, end)`` and are not exactly a decoded instruction.

    ``items``: ``{"ea", "size", "code"}``; ``decoded``: instructions ``{"ea", "size"}``.
    """
    want = {(i["ea"], i["size"]) for i in decoded}
    return [it for it in items
            if it["ea"] < end and it["ea"] + it["size"] > cb
            and not (it["code"] and (it["ea"], it["size"]) in want)]


def plan_repair(cb: int, enclosing: tuple[int, int] | None, walk: dict, gap: dict | None,
                body_funcs) -> dict:
    """Decision for one callback that is not a function start.

    ``enclosing``: ``(start, end)`` of the function containing ``cb`` or None; ``body_funcs``: the
    starts of functions that contain any decoded instruction.
    """
    out = {"va": cb, "missing": "inside-function" if enclosing else "no-function",
           "enclosing": enclosing[0] if enclosing else None}
    if not walk["ok"]:
        return {**out, "status": "refused", "check": walk["check"], "at": walk["at"]}
    out["end"] = walk["end"]
    others = set(body_funcs) - ({enclosing[0]} if enclosing else set())
    if others:
        return {**out, "status": "refused", "check": "overlaps_function", "at": sorted(others)}
    if enclosing:
        if gap is None or not gap["ok"]:
            return {**out, "status": "refused", "check": (gap or {}).get("check", "gap_missing"),
                    "detail": {k: v for k, v in (gap or {}).items() if k not in ("ok", "check")}}
        if enclosing[1] != walk["end"]:
            return {**out, "status": "refused", "check": "end_mismatch", "at": enclosing[1]}
        return {**out, "status": "would-repair", "action": "set_func_start"}
    return {**out, "status": "would-repair", "action": "add_func"}


def undo_record(cb: int, action: str, lo: int, hi: int, items, functions, names, comments) -> dict:
    """Before-state of ``[lo, hi)`` sufficient to restore the listing by hand or by script."""
    return {"kind": "undo", "va": cb, "action": action, "range": [lo, hi],
            "items": sorted(items, key=lambda i: i["ea"]),
            "functions": sorted(functions, key=lambda f: f["start"]),
            "names": sorted(names, key=lambda n: n["ea"]),
            "comments": sorted(comments, key=lambda c: (c["ea"], c["repeatable"]))}


def bound_changes(before: dict[int, int], after: dict[int, int], ignore) -> list[dict]:
    """Function starts whose end changed, appeared or vanished, outside ``ignore``."""
    out = []
    for start in sorted((set(before) | set(after)) - set(ignore)):
        b, a = before.get(start), after.get(start)
        if b != a:
            out.append({"start": start, "before": b, "after": a})
    return out


def summarize(results) -> dict:
    by_status: dict[str, int] = {}
    by_check: dict[str, int] = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        if r["status"] in ("refused", "failed"):
            by_check[r["check"]] = by_check.get(r["check"], 0) + 1
    return {"kind": "summary", "callbacks": sum(by_status.values()), "by_status": by_status,
            "by_check": by_check}


def _dumps(rec) -> str:
    return json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# --- IDA side -------------------------------------------------------------------------------------

def _load_extractor(path: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location("extract_ida_for_repair", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Ida:
    def __init__(self):
        import ida_auto
        import ida_bytes
        import ida_funcs
        import ida_idp
        import ida_name
        import ida_ua
        import ida_xref
        import idautils
        import idc

        self.auto, self.bytes, self.funcs, self.idp = ida_auto, ida_bytes, ida_funcs, ida_idp
        self.name, self.ua, self.xref, self.utils, self.idc = ida_name, ida_ua, ida_xref, idautils, idc
        self.noflow = getattr(ida_xref, "XREF_NOFLOW", getattr(ida_xref, "XREF_FAR", 1))

    def decode(self, ea):
        ins = self.ua.insn_t()
        n = self.ua.decode_insn(ins, ea)
        if n <= 0:
            return None
        mnem = (ins.get_canon_mnem() or "").lower()
        op = ins.ops[0]
        target = op.addr if op.type in (self.ua.o_near, self.ua.o_far) else None
        if mnem in ("int3", "hlt", "ud2") or (mnem == "int" and ins.ops[0].value == 3):
            kind = "trap"
        elif self.idp.is_ret_insn(ins) or mnem in ("retn", "retf", "ret"):
            kind = "ret"
        elif mnem.startswith("jmp"):
            kind = "jmp" if target is not None else "jmp_indirect"
        elif self.idp.is_call_insn(ins):
            kind = "call"
        elif (mnem.startswith("j") or mnem.startswith("loop")) and target is not None:
            kind = "jcc"
        else:
            kind = "other"
        raw = self.bytes.get_bytes(ea, n) or b""
        return {"ea": ea, "size": n, "kind": kind, "target": target, "mnem": mnem, "bytes": raw.hex()}

    def func_bounds(self, ea):
        f = self.funcs.get_func(ea)
        return None if f is None else (f.start_ea, f.end_ea)

    def items(self, lo, hi) -> list[dict]:
        out = []
        ea = self.bytes.get_item_head(lo)
        while ea < hi:
            fl = self.bytes.get_flags(ea)
            size = max(1, self.bytes.get_item_size(ea))
            if self.bytes.is_code(fl) or self.bytes.is_data(fl):
                out.append({"ea": ea, "size": size, "code": bool(self.bytes.is_code(fl)), "flags": fl})
            ea += size
        return out

    def functions_near(self, lo, hi) -> dict[int, int]:
        out = {}
        for start in self.utils.Functions(max(0, lo - NEIGHBOURHOOD), hi + NEIGHBOURHOOD):
            f = self.funcs.get_func(start)
            if f is not None:
                out[f.start_ea] = f.end_ea
        return out

    def before_state(self, cb, action, lo, hi, items, enclosing):
        funcs = []
        if enclosing is not None:
            f = self.funcs.get_func(enclosing)
            funcs.append({"start": f.start_ea, "end": f.end_ea,
                          "chunks": [list(c) for c in self.utils.Chunks(f.start_ea)],
                          "comment": self.idc.get_func_cmt(f.start_ea, 0) or None,
                          "comment_repeatable": self.idc.get_func_cmt(f.start_ea, 1) or None})
        names, comments = [], []
        for ea in range(lo, hi):
            fl = self.bytes.get_flags(ea)
            if self.bytes.has_name(fl) or self.bytes.has_dummy_name(fl):
                names.append({"ea": ea, "name": self.name.get_name(ea),
                              "user": bool(self.bytes.has_user_name(fl))})
            for rpt in (0, 1):
                c = self.idc.get_cmt(ea, rpt)
                if c:
                    comments.append({"ea": ea, "repeatable": bool(rpt), "text": c})
        return undo_record(cb, action, lo, hi, items, funcs, names, comments)

    def referenced(self, lo, hi) -> list[int]:
        return [ea for ea in range(lo, hi)
                if any(True for _ in self.utils.XrefsTo(ea, self.noflow))]


def _assess(ida: _Ida, cb: int) -> tuple[dict, dict | None]:
    bounds = ida.func_bounds(cb)
    if bounds is not None and bounds[0] == cb:
        return {"va": cb, "status": "already-ok"}, None
    enc = bounds[0] if bounds else None

    def foreign(ea):
        b = ida.func_bounds(ea)
        return b is not None and b[0] == ea and b[0] != enc

    walk = decode_walk(cb, ida.decode, foreign)
    gap = None
    if bounds is not None:
        lo = bounds[0]
        heads = [(i["ea"], i["size"]) for i in ida.items(lo, cb)]
        gap = gap_check(lo, cb, ida.bytes.get_bytes(lo, cb - lo) or b"", heads, ida.referenced(lo, cb))
    body_funcs = {b[0] for b in (ida.func_bounds(i["ea"]) for i in walk["insns"]) if b is not None}
    plan = plan_repair(cb, bounds, walk, gap, body_funcs)
    plan["insns"] = [{k: i[k] for k in ("ea", "size", "mnem", "bytes")} for i in walk["insns"]]
    if plan["status"] != "would-repair":
        return plan, None
    end = walk["end"]
    lo = bounds[0] if bounds else cb
    items = ida.items(min(lo, ida.bytes.get_item_head(cb)), end)
    plan["conflicting"] = conflicting_items(items, walk["insns"], cb, end)
    return plan, {"walk": walk, "items": items, "lo": min([lo, cb] + [i["ea"] for i in items])}


def _apply(ida: _Ida, plan: dict, ctx: dict, out) -> dict:
    cb, end, enc = plan["va"], plan["end"], plan["enclosing"]
    lo = ctx["lo"]
    near_before = ida.functions_near(lo, end)
    undo = ida.before_state(cb, plan["action"], lo, end, ctx["items"], enc)
    out.write(_dumps(undo) + "\n")
    out.flush()
    for it in plan["conflicting"]:
        ida.bytes.del_items(it["ea"], ida.bytes.DELIT_SIMPLE, it["size"])
    for ins in ctx["walk"]["insns"]:
        if not ida.bytes.is_code(ida.bytes.get_flags(ins["ea"])) and ida.ua.create_insn(ins["ea"]) <= 0:
            return {**plan, "status": "failed", "check": "create_insn", "at": ins["ea"]}
    if plan["action"] == "set_func_start":
        rc = ida.funcs.set_func_start(enc, cb)
        if rc != ida.funcs.MOVE_FUNC_OK:
            return {**plan, "status": "failed", "check": "set_func_start", "rc": rc}
    elif not ida.funcs.add_func(cb):
        return {**plan, "status": "failed", "check": "add_func"}
    ida.auto.plan_and_wait(lo, end)
    got = ida.func_bounds(cb)
    if got is None or got[0] != cb:
        return {**plan, "status": "failed", "check": "readback_start", "got": got}
    if got[1] != end:
        return {**plan, "status": "failed", "check": "readback_end", "got": got}
    changes = bound_changes(near_before, ida.functions_near(lo, end), {cb} | ({enc} if enc is not None else set()))
    if changes:
        return {**plan, "status": "failed", "check": "readback_neighbours", "changes": changes}
    return {**plan, "status": "repaired"}


def main(out_path: str, apply: bool = False, extract_path: str | None = None) -> dict:
    ex = _load_extractor(extract_path or DEFAULT_EXTRACT_IDA)
    db = ex._Db("pc")
    table, inits = ex._ida_pc_table(db)
    callbacks = sorted({r["callback"] for r in table if r["callback"]})
    counts = {"table_records": len(table), "table_callbacks": len(callbacks), "initializers": len(inits)}
    if counts != ex.PC_EXPECTED or any(not r["proved"] for r in table):
        raise ValueError(f"handler table not as audited: {counts}, refusing to repair")
    header = db.header({"apply": bool(apply), "max_insns": MAX_INSNS, "max_span": MAX_SPAN,
                        "neighbourhood": NEIGHBOURHOOD, **counts})
    header.update({"script": "repair_functions", "script_version": SCRIPT_VERSION,
                   "extract_ida_version": ex.SCRIPT_VERSION})
    ida = _Ida()
    results = []
    tmp = f"{out_path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as out:
        out.write(_dumps(header) + "\n")
        for cb in callbacks:
            plan, ctx = _assess(ida, cb)
            if ctx is not None and apply:
                plan = _apply(ida, plan, ctx, out)
            res = {"kind": "result", **plan}
            results.append(res)
            out.write(_dumps(res) + "\n")
            out.flush()
        summary = summarize(results)
        summary["apply"] = bool(apply)
        out.write(_dumps(summary) + "\n")
    os.replace(tmp, out_path)
    return summary


def _default_extract_path() -> str:
    here = globals().get("__file__")
    if here:
        cand = os.path.join(os.path.dirname(os.path.abspath(here)), "extract_ida.py")
        if os.path.exists(cand):
            return cand
    return DEFAULT_EXTRACT_IDA


if "OUT" in globals():
    _SUMMARY = main(OUT, bool(globals().get("APPLY", False)),  # noqa: F821
                    globals().get("EXTRACT_IDA") or _default_extract_path())
    print(json.dumps(_SUMMARY))

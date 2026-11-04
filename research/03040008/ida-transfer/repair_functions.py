"""Repair the PC 03040008 handler-table callbacks that are not IDA function starts (spec 007 T004c/T004e).

Database writes run only as a headless batch job on the work copy, never through an ida-mcp worker
(a killed worker's writes are lost; ``docs/how-to/write-to-an-ida-database.md``)::

    idat -A -L<log> -S"repair_functions.py <OUT> [--apply] [--extract-ida <path>]" <work copy .i64>

The batch entry waits for auto-analysis, runs :func:`main`, prints ``repair_functions summary: {...}``
to the log and ends with ``idc.qexit(0)`` (IDA saves and packs the database). On an exception it
prints the traceback, marks the database not to be saved (``DBFL_KILL``) and exits with code 1.
A dry run (no ``--apply``) changes nothing. Inside IDA for a dry run only, one call also works::

    exec(open(path).read(), {"OUT": "D:/.../repair-dryrun.jsonl", "APPLY": False})

Optional global ``EXTRACT_IDA`` / ``--extract-ida``: path of ``extract_ida.py`` (the handler table is
read with its ``_ida_pc_table``; default: beside this file, else the repository path below).

v3 (T005c): after the table callbacks, the roots are the direct call targets (``call rel32``) of the
functions in ``extract_ida``'s scope (recomputed after the table phase) that are not function starts,
then the call targets of each root repaired (or, in a dry run, that would be repaired), up to
:data:`CALL_DEPTH` levels (:func:`repair_call_targets`); roots left beyond it are ``pending`` lines.
They go through the same checks, undo records and refusals as a callback.

For each proved table callback (computed from the table) that is not a function start:

1. decode linearly from the callback to the ``ret``/``jmp`` that ends the body (no pending
   in-body branch target), refusing undecodable bytes, traps, branches out of the body and running
   into another function's start (:func:`decode_walk`). Two exceptions: an indirect jump with IDA
   switch info whose case targets all lie in the body (its jump table outside the body), and a
   stray function of at most one instruction, without xrefs, lying wholly inside the body (it is
   deleted before the repair);
2. inside a function: the bytes between the enclosing start and the callback must be unreferenced
   and padding, the tail of an instruction that crosses the callback, or unreferenced junk when the
   enclosing start is not itself a table callback (:func:`gap_check`; junk items become
   unexplored); the enclosing function must have no tail chunks and end where the decoded body ends;
3. no decoded instruction may lie in another function (strays excepted).

Only when every check passes and ``APPLY`` is true: write the undo record (before-state of items,
the functions to be deleted with their chunks, names and comments over the affected range) to
``OUT`` and flush it, delete the enclosing function and any stray (``ida_funcs.del_func``) before
undefining anything (undefining a function's entry instruction deletes the function, which made the
T004d ``set_func_start`` repairs fail with ``MOVE_FUNC_NOFUNC``), undefine exactly the conflicting
items (and junk gap items), create the decoded instructions, create the function at the callback
(``ida_funcs.add_func`` with IDA choosing the end), wait for auto-analysis of the range, and read
back: the function starts at the callback, ends at the decoded body end, and no other function
nearby changed bounds.

``OUT`` gets a header, one ``result`` line per callback (``already-ok``, ``would-repair``,
``repaired``, ``refused`` with the failed check, or ``failed`` with the read-back check), one
``undo`` line before each applied repair, and a ``summary``. Nothing is ever forced: a refusal stays
for the coordinator. Names stay where they are (a name at a deleted enclosing start is recorded, not
moved). The pure helpers and :func:`_apply` are unit-tested in ``tests/test_repair_functions.py``
with fakes.
"""

from __future__ import annotations

import json
import os

SCRIPT_VERSION = "3"
CALL_DEPTH = 3  # levels of call-target roots: 1 = called from the scope, 2-3 = from repaired callees
DEFAULT_EXTRACT_IDA = "D:/ddon-data/research/03040008/ida-transfer/extract_ida.py"
MAX_INSNS = 4000
MAX_SPAN = 0x4000  # a branch target farther than this from the callback leaves the body
NEIGHBOURHOOD = 0x1000  # functions this close to the repaired range must keep their bounds
SUMMARY_PREFIX = "repair_functions summary: "

# Padding forms the compiler emits between functions (int3, nop and multi-byte nops).
PADDING_SEQUENCES = tuple(bytes.fromhex(h) for h in (
    "cc", "90", "6690", "8bff", "8bc0", "8bc9", "8bd2", "8bdb", "8bf6", "8bed", "8d4000", "8d4900",
    "8d5200", "8d5b00", "8d6d00", "8d7600", "8d642400", "8d742600", "8d9b00000000", "8da42400000000",
    "8db600000000", "8dbf00000000", "0f1f00", "0f1f4000", "0f1f440000", "660f1f440000",
    "0f1f8000000000", "0f1f840000000000",
))


# --- pure helpers -------------------------------------------------------------------------------

def decode_walk(start: int, decode, is_foreign_start, max_insns: int = MAX_INSNS,
                max_span: int = MAX_SPAN, stray_func=None, switch=None) -> dict:
    """Decode the body that begins at ``start``.

    ``decode(ea)`` returns None (undecodable) or ``{"ea", "size", "kind", "target"}`` with kind
    ``ret``, ``jmp`` (direct), ``jmp_indirect``, ``jcc``, ``call``, ``trap`` or ``other``;
    ``is_foreign_start(ea)`` is true where another function starts. The body ends at a ``ret`` or
    an unconditional ``jmp`` once no in-body branch target lies at or after the next address.

    ``stray_func(ea)`` (optional) returns ``(start, end)`` when the function starting at ``ea`` is
    a stray (:func:`is_stray`), else None; the walk then continues through it, and refuses at the
    end unless the stray lies wholly inside the body. ``switch(ea)`` (optional) returns IDA's switch
    info for an indirect jump, ``{"targets": [...], "table": ea, "table_size": n}``, or None.

    Returns ``{"ok": True, "end", "insns", "strays", "switches"}`` or
    ``{"ok": False, "check", "at", "insns"}``.
    """
    insns: list[dict] = []
    strays: list[tuple[int, int]] = []
    switches: list[dict] = []
    ea = start
    reach = start  # furthest in-body branch target seen

    def refuse(check, at):
        return {"ok": False, "check": check, "at": at, "insns": insns}

    def in_body(target):
        return target is not None and start <= target < start + max_span and not is_foreign_start(target)

    while True:
        if len(insns) >= max_insns:
            return refuse("too_long", ea)
        if ea != start and is_foreign_start(ea):
            bounds = stray_func(ea) if stray_func is not None else None
            if bounds is None:
                return refuse("runs_into_function", ea)
            strays.append(tuple(bounds))
        ins = decode(ea)
        if ins is None or ins.get("size", 0) <= 0:
            return refuse("undecodable", ea)
        if ins["kind"] == "trap":
            return refuse("trap_in_body", ea)
        kind, target = ins["kind"], ins.get("target")
        if kind == "jmp_indirect":
            sw = switch(ea) if switch is not None else None
            if sw is None or not sw.get("targets"):
                return refuse("indirect_jump", ea)
            if not all(in_body(t) for t in sw["targets"]):
                return refuse("switch_target_out_of_body", ea)
            reach = max(reach, max(sw["targets"]))
            switches.append({"ea": ea, **sw})
        insns.append(ins)
        nxt = ea + ins["size"]
        if kind == "jcc":
            if not in_body(target):
                return refuse("branch_out_of_body", ea)
            reach = max(reach, target)
        elif kind == "jmp" and in_body(target):
            reach = max(reach, target)
        if kind in ("ret", "jmp", "jmp_indirect") and reach < nxt:
            break
        ea = nxt
    end = nxt
    for s, e in strays:
        if e > end:
            return refuse("runs_into_function", s)
    for sw in switches:
        if not all(start <= t < end for t in sw["targets"]):
            return refuse("switch_target_out_of_body", sw["ea"])
        if sw.get("table") is not None and sw["table"] < end and sw["table"] + sw.get("table_size", 0) > start:
            return refuse("switch_table_in_body", sw["ea"])
    return {"ok": True, "end": end, "insns": insns, "strays": strays, "switches": switches}


def is_stray(insn_count: int, chunk_count: int, xrefs) -> bool:
    """A function IDA made on a single instruction (e.g. a body's own ``retn``) that nothing references."""
    return insn_count <= 1 and chunk_count <= 1 and not xrefs


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


def gap_check(enc_start: int, cb: int, gap: bytes, heads, referenced, enc_is_callback: bool) -> dict:
    """Check the bytes ``[enc_start, cb)`` an enclosing function would give up.

    ``heads`` are the defined items ``(ea, size)`` that start in the gap; ``referenced`` the gap
    addresses with a non-flow (code or data) xref; ``enc_is_callback`` whether ``enc_start`` is
    itself a handler-table callback. Bytes before the first item crossing ``cb`` must be padding;
    from that item on they are the tail of a misdecoded instruction. Otherwise the gap is accepted
    as junk (``"junk": True``, its items to become unexplored) only when nothing references it and
    the enclosing start is not a table callback.
    """
    if len(gap) != cb - enc_start:
        return {"ok": False, "check": "gap_unreadable"}
    if referenced:
        return {"ok": False, "check": "gap_referenced", "at": sorted(referenced)}
    crossing = [h for h, size in heads if enc_start <= h < cb and h + size > cb]
    plain_end = min(crossing) if crossing else cb
    misdecoded = min(crossing) if crossing else None
    if is_padding(gap[: plain_end - enc_start]):
        return {"ok": True, "misdecoded": misdecoded, "junk": False}
    if enc_is_callback:
        return {"ok": False, "check": "gap_not_padding", "bytes": gap.hex(), "enclosing_is_callback": True}
    return {"ok": True, "misdecoded": misdecoded, "junk": True, "bytes": gap.hex()}


def conflicting_items(items, decoded, cb: int, end: int) -> list[dict]:
    """Defined items that overlap ``[cb, end)`` and are not exactly a decoded instruction.

    ``items``: ``{"ea", "size", "code"}``; ``decoded``: instructions ``{"ea", "size"}``.
    """
    want = {(i["ea"], i["size"]) for i in decoded}
    return [it for it in items
            if it["ea"] < end and it["ea"] + it["size"] > cb
            and not (it["code"] and (it["ea"], it["size"]) in want)]


def plan_repair(cb: int, enclosing: tuple[int, int] | None, walk: dict, gap: dict | None,
                body_funcs, enc_chunks: int = 1) -> dict:
    """Decision for one callback that is not a function start.

    ``enclosing``: ``(start, end)`` of the function containing ``cb`` or None; ``body_funcs``: the
    starts of functions that contain any decoded instruction; ``enc_chunks``: the enclosing
    function's chunk count (tails would be lost by deleting it).
    """
    out = {"va": cb, "missing": "inside-function" if enclosing else "no-function",
           "enclosing": enclosing[0] if enclosing else None}
    if not walk["ok"]:
        return {**out, "status": "refused", "check": walk["check"], "at": walk["at"]}
    out["end"] = walk["end"]
    strays = sorted(s for s, _ in walk.get("strays", ()))
    others = set(body_funcs) - ({enclosing[0]} if enclosing else set()) - set(strays)
    if others:
        return {**out, "status": "refused", "check": "overlaps_function", "at": sorted(others)}
    delete = ([enclosing[0]] if enclosing else []) + strays
    if enclosing:
        if gap is None or not gap["ok"]:
            return {**out, "status": "refused", "check": (gap or {}).get("check", "gap_missing"),
                    "detail": {k: v for k, v in (gap or {}).items() if k not in ("ok", "check")}}
        if enclosing[1] != walk["end"]:
            return {**out, "status": "refused", "check": "end_mismatch", "at": enclosing[1]}
        if enc_chunks != 1:
            return {**out, "status": "refused", "check": "enclosing_has_tails", "at": enclosing[0]}
        return {**out, "status": "would-repair", "action": "replace_func", "delete_funcs": delete,
                "gap_junk": bool(gap.get("junk"))}
    return {**out, "status": "would-repair", "action": "add_func", "delete_funcs": delete}


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


def is_call_rel32(ins: dict) -> bool:
    """A direct ``call rel32`` (opcode ``E8``, no prefix) as decoded by ``_Ida.decode``."""
    return (ins.get("kind") == "call" and ins.get("target") is not None
            and (ins.get("bytes") or "").lower().startswith("e8"))


def call_target_roots(insns, is_func_start, done=()) -> dict[int, list[int]]:
    """Call-target roots: target -> sorted call sites of the ``call rel32`` in ``insns`` whose target
    is not a function start and not already handled (``done``)."""
    out: dict[int, list[int]] = {}
    for ins in insns:
        if is_call_rel32(ins) and ins["target"] not in done and not is_func_start(ins["target"]):
            out.setdefault(ins["target"], []).append(ins["ea"])
    return {t: sorted(s) for t, s in out.items()}


def repair_call_targets(ida, first: dict[int, list[int]], callbacks, apply: bool, out,
                        max_level: int = CALL_DEPTH) -> tuple[list[dict], dict[int, list[int]]]:
    """Assess (and with ``apply`` repair) call-target roots level by level.

    Level 1 is ``first`` (targets called from the functions in scope); the ``call rel32`` targets in
    the decoded body of every root that is repaired (or would be, in a dry run) and that are not
    function starts form the next level, up to ``max_level``, until no new root appears. Each root is
    handled once, with the same checks, undo records and refusals as a table callback
    (:func:`_assess`, :func:`_apply`). Returns the ``result`` records and the roots left beyond
    ``max_level`` (target -> call sites).
    """
    def is_start(ea):
        b = ida.func_bounds(ea)
        return b is not None and b[0] == ea

    done = set(callbacks)
    results: list[dict] = []
    roots = {t: s for t, s in first.items() if t not in done}
    level = 1
    while roots and level <= max_level:
        nxt: dict[int, list[int]] = {}
        for target in sorted(roots):
            done.add(target)
            plan, ctx = _assess(ida, target, callbacks)
            if ctx is not None and apply:
                plan = _apply(ida, plan, ctx, out)
            res = {"kind": "result", "root": "call_target", "level": level, "call_sites": roots[target], **plan}
            results.append(res)
            out.write(_dumps(res) + "\n")
            out.flush()
            if ctx is not None and res["status"] in ("would-repair", "repaired"):
                for t, sites in call_target_roots(ctx["walk"]["insns"], is_start, done).items():
                    nxt.setdefault(t, []).extend(sites)
        roots = {t: sorted(s) for t, s in nxt.items() if t not in done}
        level += 1
    return results, roots


def call_target_summary(calls, scope_functions: int, pending: int) -> dict:
    """Counts of the call-target phase: by status, failed check and level."""
    s = summarize(calls)
    return {"roots": s["callbacks"], "by_status": s["by_status"], "by_check": s["by_check"],
            "by_level": {str(lv): sum(1 for r in calls if r["level"] == lv) for lv in range(1, CALL_DEPTH + 1)},
            "scope_functions": scope_functions, "pending_beyond_depth": pending}


def parse_batch_args(argv) -> dict:
    """``idc.ARGV`` of a batch run (``argv[0]`` is the script) to ``main`` keyword arguments."""
    import argparse

    ap = argparse.ArgumentParser(prog="repair_functions.py", exit_on_error=False)
    ap.add_argument("out")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--extract-ida")
    ns = ap.parse_args(list(argv[1:]))
    return {"out_path": ns.out, "apply": ns.apply, "extract_path": ns.extract_ida}


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
        import ida_nalt
        import ida_name
        import ida_ua
        import ida_xref
        import idautils
        import idc

        self.auto, self.bytes, self.funcs, self.idp = ida_auto, ida_bytes, ida_funcs, ida_idp
        self.name, self.ua, self.xref, self.utils, self.idc = ida_name, ida_ua, ida_xref, idautils, idc
        self.nalt = ida_nalt
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

    def chunk_count(self, start) -> int:
        return sum(1 for _ in self.utils.Chunks(start))

    def stray(self, ea):
        """``(start, end)`` of the function at ``ea`` when it is a stray (:func:`is_stray`)."""
        b = self.func_bounds(ea)
        if b is None or b[0] != ea:
            return None
        n = sum(1 for _ in self.utils.Heads(b[0], b[1]))
        if is_stray(n, self.chunk_count(ea), self.referenced(b[0], b[1])):
            return b
        return None

    def switch(self, ea):
        si = self.nalt.get_switch_info(ea)
        if si is None:
            return None
        cases = self.xref.calc_switch_cases(ea, si)
        if cases is None:
            return None
        targets = sorted({int(t) for t in cases.targets})
        return {"targets": targets, "table": int(si.jumps),
                "table_size": int(si.get_jtable_size()) * int(si.get_jtable_element_size())}

    def func_insns(self, start) -> list[dict]:
        """Decoded instructions of the function starting at ``start`` (all chunks)."""
        return [d for d in (self.decode(ea) for ea in self.utils.FuncItems(start)) if d is not None]

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

    def before_state(self, cb, action, lo, hi, items, func_starts):
        funcs = []
        for start in func_starts:
            f = self.funcs.get_func(start)
            if f is None:
                continue
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


def _assess(ida: _Ida, cb: int, callbacks=frozenset()) -> tuple[dict, dict | None]:
    bounds = ida.func_bounds(cb)
    if bounds is not None and bounds[0] == cb:
        return {"va": cb, "status": "already-ok"}, None
    enc = bounds[0] if bounds else None

    def foreign(ea):
        b = ida.func_bounds(ea)
        return b is not None and b[0] == ea and b[0] != enc

    walk = decode_walk(cb, ida.decode, foreign, stray_func=ida.stray, switch=ida.switch)
    gap = None
    if bounds is not None:
        lo = bounds[0]
        heads = [(i["ea"], i["size"]) for i in ida.items(lo, cb)]
        gap = gap_check(lo, cb, ida.bytes.get_bytes(lo, cb - lo) or b"", heads, ida.referenced(lo, cb),
                        lo in callbacks)
    body_funcs = {b[0] for b in (ida.func_bounds(i["ea"]) for i in walk["insns"]) if b is not None}
    plan = plan_repair(cb, bounds, walk, gap, body_funcs, ida.chunk_count(enc) if enc is not None else 1)
    plan["insns"] = [{k: i[k] for k in ("ea", "size", "mnem", "bytes")} for i in walk["insns"]]
    if walk["ok"] and walk["switches"]:
        plan["switches"] = walk["switches"]
    if plan["status"] != "would-repair":
        return plan, None
    end = walk["end"]
    lo = bounds[0] if bounds else cb
    items = ida.items(min(lo, ida.bytes.get_item_head(cb)), end)
    plan["conflicting"] = conflicting_items(items, walk["insns"], cb, end)
    if plan.get("gap_junk"):
        plan["gap_items"] = [it for it in items if lo <= it["ea"] < cb and it not in plan["conflicting"]]
    return plan, {"walk": walk, "items": items, "lo": min([lo, cb] + [i["ea"] for i in items])}


def _apply(ida, plan: dict, ctx: dict, out) -> dict:
    """Apply one ``would-repair`` plan. Order matters: functions are deleted before any item is
    undefined, because undefining a function's entry instruction makes IDA delete the function."""
    cb, end = plan["va"], plan["end"]
    lo = ctx["lo"]
    delete = list(plan.get("delete_funcs", ()))
    near_before = ida.functions_near(lo, end)
    undo = ida.before_state(cb, plan["action"], lo, end, ctx["items"], delete)
    out.write(_dumps(undo) + "\n")
    out.flush()
    for start in delete:
        if not ida.funcs.del_func(start):
            return {**plan, "status": "failed", "check": "del_func", "at": start}
    for it in plan["conflicting"] + plan.get("gap_items", []):
        ida.bytes.del_items(it["ea"], ida.bytes.DELIT_SIMPLE, it["size"])
    for ins in ctx["walk"]["insns"]:
        if not ida.bytes.is_code(ida.bytes.get_flags(ins["ea"])) and ida.ua.create_insn(ins["ea"]) <= 0:
            return {**plan, "status": "failed", "check": "create_insn", "at": ins["ea"]}
    if not ida.funcs.add_func(cb):
        return {**plan, "status": "failed", "check": "add_func"}
    ida.auto.plan_and_wait(lo, end)
    got = ida.func_bounds(cb)
    if got is None or got[0] != cb:
        return {**plan, "status": "failed", "check": "readback_start", "got": got}
    if got[1] != end:
        return {**plan, "status": "failed", "check": "readback_end", "got": got}
    changes = bound_changes(near_before, ida.functions_near(lo, end), {cb} | set(delete))
    if changes:
        return {**plan, "status": "failed", "check": "readback_neighbours", "changes": changes}
    return {**plan, "status": "repaired"}


def main(out_path: str, apply: bool = False, extract_path: str | None = None) -> dict:
    ex = _load_extractor(extract_path or DEFAULT_EXTRACT_IDA)
    db = ex._Db("pc")
    table, inits, _reason, *_ = ex.pc_roots(db)
    callbacks = sorted({r["callback"] for r in table if r["callback"]})
    counts = {"table_records": len(table), "table_callbacks": len(callbacks), "initializers": len(inits)}
    if counts != ex.PC_EXPECTED or any(not r["proved"] for r in table):
        raise ValueError(f"handler table not as audited: {counts}, refusing to repair")
    header = db.header({"apply": bool(apply), "max_insns": MAX_INSNS, "max_span": MAX_SPAN,
                        "neighbourhood": NEIGHBOURHOOD, "call_depth": CALL_DEPTH,
                        "scope_depth": ex.DEFAULT_DEPTH, **counts})
    header.update({"script": "repair_functions", "script_version": SCRIPT_VERSION,
                   "extract_ida_version": ex.SCRIPT_VERSION})
    ida = _Ida()
    cbset = frozenset(callbacks)
    results = []
    tmp = f"{out_path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as out:
        out.write(_dumps(header) + "\n")
        for cb in callbacks:
            plan, ctx = _assess(ida, cb, cbset)
            if ctx is not None and apply:
                plan = _apply(ida, plan, ctx, out)
            res = {"kind": "result", "root": "table", **plan}
            results.append(res)
            out.write(_dumps(res) + "\n")
            out.flush()
        # call-target roots; the scope is recomputed after the table repairs (as extract_ida sees it)
        _t, _i, reason, *_ = ex.pc_roots(db)
        dist, _missing = ex.plan_scope(reason, db.func_start, lambda va: ex._ida_callees(db, va),
                                       ex.DEFAULT_DEPTH)

        def is_start(ea):
            b = ida.func_bounds(ea)
            return b is not None and b[0] == ea

        first: dict[int, list[int]] = {}
        for va in sorted(dist):
            for t, sites in call_target_roots(ida.func_insns(va), is_start, cbset).items():
                first.setdefault(t, []).extend(sites)
        calls, pending = repair_call_targets(ida, {t: sorted(s) for t, s in first.items()}, cbset, apply, out)
        for t in sorted(pending):
            out.write(_dumps({"kind": "pending", "va": t, "level": CALL_DEPTH + 1, "call_sites": pending[t]}) + "\n")
        summary = summarize(results)
        summary["apply"] = bool(apply)
        summary["call_targets"] = call_target_summary(calls, len(dist), len(pending))
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


def batch(argv, run=None, kill=None, qexit=None, wait=None) -> int:
    """Headless entry: parse ``argv``, run, print the summary line, exit IDA.

    The hooks default to IDA (``ida_auto.auto_wait``, ``DBFL_KILL``, ``idc.qexit``); tests pass fakes.
    Returns the exit code passed to ``qexit``.
    """
    import traceback

    code = 1
    try:
        kw = parse_batch_args(argv)
        kw["extract_path"] = kw["extract_path"] or _default_extract_path()
        if wait is not None:
            wait()
        summary = (run or main)(**kw)
        print(SUMMARY_PREFIX + json.dumps(summary, sort_keys=True), flush=True)
        code = 0
    except BaseException:  # noqa: BLE001 - any failure must still end the batch process
        traceback.print_exc()
        print(SUMMARY_PREFIX + json.dumps({"error": True, "saved": False}), flush=True)
        if kill is not None:
            kill()
    if qexit is not None:
        qexit(code)
    return code


def _ida_batch_hooks():
    import ida_auto
    import ida_loader
    import idc

    return {"wait": ida_auto.auto_wait, "qexit": idc.qexit,
            "kill": lambda: ida_loader.set_database_flag(ida_loader.DBFL_KILL)}


if "OUT" in globals():
    _SUMMARY = main(OUT, bool(globals().get("APPLY", False)),  # noqa: F821
                    globals().get("EXTRACT_IDA") or _default_extract_path())
    print(SUMMARY_PREFIX + json.dumps(_SUMMARY, sort_keys=True))
elif __name__ == "__main__":
    try:
        import idc as _idc
    except ImportError:
        _idc = None
    if _idc is not None and len(_idc.ARGV) >= 2:
        batch(list(_idc.ARGV), **_ida_batch_hooks())

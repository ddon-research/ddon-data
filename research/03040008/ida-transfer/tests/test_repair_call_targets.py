"""repair_functions.py v3 (T005c): direct call targets as roots, iterated; fakes, no IDA."""

from __future__ import annotations

import io
import json
from types import SimpleNamespace as NS

import repair_functions as rf


def _i(ea, size, kind, target=None, raw=None):
    if raw is None:
        raw = "e8" + "00" * (size - 1) if kind == "call" and target is not None else "90" * size
    return {"ea": ea, "size": size, "kind": kind, "target": target, "mnem": kind, "bytes": raw}


class _ProgIda:
    """Enough of ``_Ida`` for ``_assess`` and ``_apply`` over a hand-written program.

    ``prog``: ea -> decoded instruction; ``fn``: function start -> end; ``code``: defined code items
    ea -> size; ``raw``: ea -> byte; ``xrefs``: addresses with a non-flow xref; ``ends``: the end IDA
    picks when ``add_func`` creates a function at a start.
    """

    def __init__(self, prog, fn, code=None, raw=None, xrefs=(), ends=None):
        self.prog = {i["ea"]: i for i in prog}
        self.fn = dict(fn)
        self.code = dict(code or {})
        self.raw = dict(raw or {})
        self.xrefs = set(xrefs)
        self.ends = dict(ends or {})
        self.bytes = NS(DELIT_SIMPLE=0, del_items=self._del_items, get_flags=lambda ea: ea in self.code,
                        is_code=bool, get_item_head=lambda ea: ea, get_bytes=self._get_bytes)
        self.ua = NS(create_insn=self._create)
        self.funcs = NS(del_func=self._del_func, add_func=self._add_func)
        self.auto = NS(plan_and_wait=lambda lo, hi: None)

    def decode(self, ea):
        return self.prog.get(ea)

    def func_bounds(self, ea):
        for s, e in self.fn.items():
            if s <= ea < e:
                return (s, e)
        return None

    def func_insns(self, start):
        return [i for ea, i in sorted(self.prog.items()) if start <= ea < self.fn[start]]

    def stray(self, ea):
        return None

    def switch(self, ea):
        return None

    def chunk_count(self, start):
        return 1

    def items(self, lo, hi):
        return [{"ea": ea, "size": s, "code": True} for ea, s in sorted(self.code.items()) if lo <= ea < hi]

    def referenced(self, lo, hi):
        return sorted(ea for ea in self.xrefs if lo <= ea < hi)

    def functions_near(self, lo, hi):
        return dict(self.fn)

    def before_state(self, cb, action, lo, hi, items, func_starts):
        funcs = [{"start": s, "end": self.fn[s]} for s in func_starts]
        return rf.undo_record(cb, action, lo, hi, items, funcs, [], [])

    def _get_bytes(self, ea, n):
        return bytes(self.raw.get(a, 0x90) for a in range(ea, ea + n))

    def _del_items(self, ea, flags, size):
        for a in [a for a in self.code if ea <= a < ea + size]:
            del self.code[a]

    def _create(self, ea):
        self.code[ea] = self.prog[ea]["size"]
        return 1

    def _del_func(self, ea):
        return self.fn.pop(ea, None) is not None

    def _add_func(self, ea):
        if self.func_bounds(ea) is not None or ea not in self.ends:
            return False
        self.fn[ea] = self.ends[ea]
        return True


# Scope function F (0x100) calls 0x200, which calls 0x300; neither callee is a function (T005b: the
# element readers at 0x758000-0x77C000). 0x200 also calls F (a function start: not a root) and an
# import through `call [mem]` (FF 15: not a call rel32).
_CHAIN = [
    _i(0x100, 1, "other"), _i(0x101, 5, "call", 0x200), _i(0x106, 1, "ret"),
    _i(0x200, 1, "other"), _i(0x201, 5, "call", 0x300), _i(0x206, 5, "call", 0x100),
    _i(0x20B, 6, "call", None, raw="ff1500100000"), _i(0x211, 1, "ret"),
    _i(0x300, 2, "other"), _i(0x302, 1, "ret"),
]


def _chain_ida():
    return _ProgIda(_CHAIN, {0x100: 0x107}, code={0x100: 1, 0x101: 5, 0x106: 1}, ends={0x200: 0x212, 0x300: 0x303})


def test_is_call_rel32():
    assert rf.is_call_rel32(_i(0x10, 5, "call", 0x200))
    assert not rf.is_call_rel32(_i(0x10, 6, "call", None, raw="ff1500100000"))  # call [mem]
    assert not rf.is_call_rel32(_i(0x10, 6, "call", 0x200, raw="66e800000000"))  # prefixed: not rel32
    assert not rf.is_call_rel32(_i(0x10, 5, "jmp", 0x200, raw="e900000000"))


def test_call_target_roots_from_scope():
    ida = _chain_ida()
    roots = rf.call_target_roots(ida.func_insns(0x100), lambda ea: ea in ida.fn)
    assert roots == {0x200: [0x101]}
    assert rf.call_target_roots(ida.func_insns(0x100), lambda ea: ea in ida.fn, done={0x200}) == {}


def test_chain_of_two_undefined_callees_both_repaired():
    ida = _chain_ida()
    out = io.StringIO()
    first = rf.call_target_roots(ida.func_insns(0x100), lambda ea: ea in ida.fn)
    results, pending = rf.repair_call_targets(ida, first, frozenset(), True, out)
    assert [(r["va"], r["level"], r["status"]) for r in results] == [(0x200, 1, "repaired"), (0x300, 2, "repaired")]
    assert results[1]["call_sites"] == [0x201] and pending == {}
    assert ida.fn == {0x100: 0x107, 0x200: 0x212, 0x300: 0x303}
    kinds = [json.loads(line)["kind"] for line in out.getvalue().splitlines()]
    assert kinds == ["undo", "result", "undo", "result"]  # undo written before each repair


def test_chain_dry_run_follows_would_repair_and_changes_nothing():
    ida = _chain_ida()
    results, pending = rf.repair_call_targets(ida, {0x200: [0x101]}, frozenset(), False, io.StringIO())
    assert [(r["va"], r["status"]) for r in results] == [(0x200, "would-repair"), (0x300, "would-repair")]
    assert ida.fn == {0x100: 0x107}


def test_depth_limit_leaves_pending_roots():
    ida = _chain_ida()
    results, pending = rf.repair_call_targets(ida, {0x200: [0x101]}, frozenset(), False, io.StringIO(), max_level=1)
    assert [r["va"] for r in results] == [0x200] and pending == {0x300: [0x201]}


def test_table_callbacks_are_not_call_target_roots():
    ida = _chain_ida()
    results, _ = rf.repair_call_targets(ida, {0x200: [0x101]}, frozenset({0x200}), False, io.StringIO())
    assert results == []


def _inside_ida(xrefs, gap=b"\x55\x8b\xec\x83\xec\x08\x56\x57"):
    """Function 0x400..0x420; a call targets 0x408 inside it; the body from 0x408 ends at 0x420."""
    prog = [_i(0x408, 0x17, "other"), _i(0x41F, 1, "ret")]
    raw = {0x400 + k: b for k, b in enumerate(gap)}
    code = {0x400: 1, 0x401: 2, 0x403: 3, 0x406: 1, 0x407: 1, 0x408: 0x17, 0x41F: 1}
    return _ProgIda(prog, {0x400: 0x420}, code=code, raw=raw, xrefs=xrefs, ends={0x408: 0x420})


def test_call_target_inside_a_real_function_is_refused():
    # the enclosing start is called (code xref) and the gap is code: T004e rules refuse
    ida = _inside_ida(xrefs={0x400})
    results, pending = rf.repair_call_targets(ida, {0x408: [0x150]}, frozenset(), True, io.StringIO())
    assert len(results) == 1 and results[0]["status"] == "refused" and results[0]["check"] == "gap_referenced"
    assert ida.fn == {0x400: 0x420} and pending == {}


def test_call_target_inside_function_accepted_only_by_the_t004e_rules():
    # padding gap, nothing references the enclosing start: the T004e inside-function rules accept it
    ida = _inside_ida(xrefs=(), gap=b"\xcc" * 8)
    results, _ = rf.repair_call_targets(ida, {0x408: [0x150]}, frozenset(), False, io.StringIO())
    assert results[0]["status"] == "would-repair" and results[0]["action"] == "replace_func"


def test_call_target_summary():
    calls = [{"status": "repaired", "level": 1}, {"status": "refused", "check": "gap_referenced", "level": 1},
             {"status": "repaired", "level": 2}]
    assert rf.call_target_summary(calls, 900, 3) == {
        "roots": 3, "by_status": {"repaired": 2, "refused": 1}, "by_check": {"gap_referenced": 1},
        "by_level": {"1": 2, "2": 1, "3": 0}, "scope_functions": 900, "pending_beyond_depth": 3}


def test_script_version_bumped():
    assert rf.SCRIPT_VERSION == "3" and rf.CALL_DEPTH == 3

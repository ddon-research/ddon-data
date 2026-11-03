"""Pure parts of repair_functions.py, with fakes (no IDA)."""

from __future__ import annotations

import io
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

import repair_functions as rf


def test_module_import_does_not_run_main():
    assert "_SUMMARY" not in vars(rf)


def test_exec_without_out_defines_helpers_only():
    g: dict = {}
    exec(compile(Path(rf.__file__).read_text(encoding="utf-8"), "repair_functions.py", "exec"), g)
    assert "main" in g and "_SUMMARY" not in g


def _prog(*rows):
    """{ea: insn} from (ea, size, kind, target) rows."""
    return {ea: {"ea": ea, "size": size, "kind": kind, "target": target} for ea, size, kind, target in rows}


def _walk(prog, start, starts=(), **kw):
    return rf.decode_walk(start, prog.get, lambda ea: ea in starts, **kw)


def test_walk_straight_body_ends_at_ret():
    prog = _prog((0x10, 1, "other", None), (0x11, 5, "call", 0x900), (0x16, 3, "ret", None),
                 (0x19, 1, "trap", None))
    r = _walk(prog, 0x10)
    assert r["ok"] and r["end"] == 0x19 and [i["ea"] for i in r["insns"]] == [0x10, 0x11, 0x16]


def test_walk_continues_past_ret_while_a_branch_target_is_pending():
    prog = _prog((0x10, 2, "jcc", 0x15), (0x12, 1, "ret", None), (0x13, 2, "other", None),
                 (0x15, 1, "ret", None))
    r = _walk(prog, 0x10)
    assert r["ok"] and r["end"] == 0x16


def test_walk_backward_jmp_ends_body_and_tail_jmp_ends_body():
    loop = _prog((0x10, 2, "other", None), (0x12, 2, "jmp", 0x10))
    assert _walk(loop, 0x10)["end"] == 0x14
    tail = _prog((0x10, 2, "other", None), (0x12, 5, "jmp", 0x900))
    r = _walk(tail, 0x10, starts={0x900})
    assert r["ok"] and r["end"] == 0x17


@pytest.mark.parametrize(
    ("prog", "starts", "check", "at"),
    [(_prog((0x10, 2, "other", None)), (), "undecodable", 0x12),
     (_prog((0x10, 2, "other", None), (0x12, 1, "trap", None)), (), "trap_in_body", 0x12),
     (_prog((0x10, 2, "jmp_indirect", None)), (), "indirect_jump", 0x10),
     (_prog((0x10, 2, "other", None), (0x12, 1, "ret", None)), {0x12}, "runs_into_function", 0x12),
     (_prog((0x10, 2, "jcc", 0x08), (0x12, 1, "ret", None)), (), "branch_out_of_body", 0x10),
     (_prog((0x10, 2, "jcc", 0x20), (0x12, 1, "ret", None)), {0x20}, "branch_out_of_body", 0x10)],
)
def test_walk_refusals(prog, starts, check, at):
    r = _walk(prog, 0x10, starts)
    assert not r["ok"] and r["check"] == check and r["at"] == at


def test_walk_too_long():
    prog = {ea: {"ea": ea, "size": 1, "kind": "other", "target": None} for ea in range(0x10, 0x100)}
    r = _walk(prog, 0x10, max_insns=5)
    assert not r["ok"] and r["check"] == "too_long"


@pytest.mark.parametrize(
    ("raw", "ok"),
    [(b"", True), (b"\xcc\xcc\xcc", True), (b"\x8d\x49\x00", True), (b"\x8b\xff\xcc", True),
     (b"\x8d\xa4\x24\x00\x00\x00\x00\x90", True), (b"\x56", False), (b"\xcc\x8d\x49", False)],
)
def test_is_padding(raw, ok):
    assert rf.is_padding(raw) is ok


def test_gap_check_padding_and_misdecoded_tail():
    assert rf.gap_check(0x10, 0x13, b"\xcc\xcc\xcc", [], [], False)["ok"]
    # item at 0x10 crosses the callback at 0x13: its bytes are a misdecoded tail, not checked
    r = rf.gap_check(0x10, 0x13, b"\x05\x5d\x35", [(0x10, 5)], [], False)
    assert r == {"ok": True, "misdecoded": 0x10, "junk": False}
    # padding before a crossing item is still checked (refused when the enclosing start is a callback)
    assert rf.gap_check(0x10, 0x14, b"\xcc\x05\x5d\x35", [(0x11, 5)], [], True)["ok"]
    assert rf.gap_check(0x10, 0x14, b"\x56\x05\x5d\x35", [(0x11, 5)], [], True)["check"] == "gap_not_padding"


def test_gap_check_accepts_unreferenced_junk():
    # T004d 0x7C68E0: `push esi; push edi` at 0x7C68DE, nothing points at it, not a table callback
    r = rf.gap_check(0x10, 0x12, b"\x56\x57", [(0x10, 1), (0x11, 1)], [], False)
    assert r["ok"] and r["junk"] is True


@pytest.mark.parametrize(
    ("refs", "enc_is_callback", "check"),
    [([0x10], False, "gap_referenced"),  # a call/jump/data xref to the enclosing start
     ([0x11], False, "gap_referenced"),  # an xref into the gap
     ([], True, "gap_not_padding")],  # the enclosing start is itself a table callback
)
def test_gap_check_junk_near_misses_refused(refs, enc_is_callback, check):
    r = rf.gap_check(0x10, 0x12, b"\x56\x57", [(0x10, 1), (0x11, 1)], refs, enc_is_callback)
    assert not r["ok"] and r["check"] == check


@pytest.mark.parametrize(
    ("gap", "heads", "refs", "check"),
    [(b"\xcc\xcc", [], [0x11], "gap_referenced"),  # something points into the gap
     (b"\x56\x57", [(0x10, 1), (0x11, 1)], [], "gap_not_padding"),  # code before a callback start
     (b"\xcc", [], [], "gap_unreadable")],
)
def test_gap_check_refusals(gap, heads, refs, check):
    assert rf.gap_check(0x10, 0x12, gap, heads, refs, True)["check"] == check


def test_conflicting_items():
    decoded = [{"ea": 0x13, "size": 1}, {"ea": 0x14, "size": 2}, {"ea": 0x16, "size": 1}]
    items = [{"ea": 0x10, "size": 5, "code": True},  # crosses the callback
             {"ea": 0x14, "size": 2, "code": False},  # data where code decodes
             {"ea": 0x16, "size": 1, "code": True},  # matches a decoded instruction: kept
             {"ea": 0x17, "size": 4, "code": False},  # after the body: kept
             {"ea": 0x0C, "size": 2, "code": True}]  # gap padding before: kept
    assert [i["ea"] for i in rf.conflicting_items(items, decoded, 0x13, 0x17)] == [0x10, 0x14]


_OK_WALK = {"ok": True, "end": 0x40, "insns": [], "strays": [], "switches": []}


def test_plan_no_function_and_inside_function():
    assert rf.plan_repair(0x10, None, _OK_WALK, None, set()) == {
        "va": 0x10, "missing": "no-function", "enclosing": None, "end": 0x40,
        "status": "would-repair", "action": "add_func", "delete_funcs": []}
    p = rf.plan_repair(0x10, (0x0D, 0x40), _OK_WALK, {"ok": True, "misdecoded": None, "junk": True}, {0x0D})
    assert p["status"] == "would-repair" and p["action"] == "replace_func" and p["enclosing"] == 0x0D
    assert p["delete_funcs"] == [0x0D] and p["gap_junk"] is True


def test_plan_stray_is_deleted_not_an_overlap():
    walk = {**_OK_WALK, "strays": [(0x3D, 0x40)]}
    p = rf.plan_repair(0x10, None, walk, None, {0x3D})
    assert p["status"] == "would-repair" and p["delete_funcs"] == [0x3D]


def test_plan_refuses_enclosing_with_tail_chunks():
    p = rf.plan_repair(0x10, (0x0D, 0x40), _OK_WALK, {"ok": True}, {0x0D}, enc_chunks=2)
    assert p["status"] == "refused" and p["check"] == "enclosing_has_tails"


@pytest.mark.parametrize(
    ("enclosing", "walk", "gap", "funcs", "check"),
    [(None, {"ok": False, "check": "undecodable", "at": 0x11, "insns": []}, None, set(), "undecodable"),
     (None, _OK_WALK, None, {0x30}, "overlaps_function"),
     ((0x0D, 0x40), _OK_WALK, {"ok": True}, {0x0D, 0x30}, "overlaps_function"),
     ((0x0D, 0x40), _OK_WALK, {"ok": False, "check": "gap_referenced", "at": [0x0E]}, {0x0D}, "gap_referenced"),
     ((0x0D, 0x40), _OK_WALK, None, {0x0D}, "gap_missing"),
     ((0x0D, 0x50), _OK_WALK, {"ok": True}, {0x0D}, "end_mismatch")],
)
def test_plan_refusals(enclosing, walk, gap, funcs, check):
    p = rf.plan_repair(0x10, enclosing, walk, gap, funcs)
    assert p["status"] == "refused" and p["check"] == check


def test_undo_record_shape():
    u = rf.undo_record(0x13, "set_func_start", 0x10, 0x40,
                       [{"ea": 0x14, "size": 2, "code": False, "flags": 1}, {"ea": 0x10, "size": 5, "code": True,
                                                                             "flags": 2}],
                       [{"start": 0x10, "end": 0x40, "chunks": [[0x10, 0x40]], "comment": None,
                         "comment_repeatable": None}],
                       [{"ea": 0x10, "name": "OnPacket_X", "user": True}],
                       [{"ea": 0x14, "repeatable": True, "text": "b"}, {"ea": 0x14, "repeatable": False, "text": "a"}])
    assert set(u) == {"kind", "va", "action", "range", "items", "functions", "names", "comments"}
    assert u["kind"] == "undo" and u["range"] == [0x10, 0x40]
    assert [i["ea"] for i in u["items"]] == [0x10, 0x14]
    assert [c["text"] for c in u["comments"]] == ["a", "b"]


def test_bound_changes():
    before = {0x10: 0x40, 0x50: 0x60, 0x70: 0x80}
    after = {0x13: 0x40, 0x50: 0x66, 0x90: 0xA0}
    assert rf.bound_changes(before, after, {0x10, 0x13}) == [
        {"start": 0x50, "before": 0x60, "after": 0x66},
        {"start": 0x70, "before": 0x80, "after": None},
        {"start": 0x90, "before": None, "after": 0xA0}]
    assert rf.bound_changes(before, dict(before), ()) == []


def test_summarize():
    s = rf.summarize([{"status": "already-ok"}, {"status": "refused", "check": "undecodable"},
                      {"status": "refused", "check": "undecodable"}, {"status": "would-repair"}])
    assert s == {"kind": "summary", "callbacks": 4,
                 "by_status": {"already-ok": 1, "refused": 2, "would-repair": 1},
                 "by_check": {"undecodable": 2}}


# --- relaxations in the walk (T004e) ---------------------------------------------------------------

# body 0x10..0x17: other, other, retn 4 at 0x14 (3 bytes); IDA put a 3-byte nullsub on that retn
_STRAY_BODY = _prog((0x10, 2, "other", None), (0x12, 2, "other", None), (0x14, 3, "ret", None))


def test_walk_accepts_stray_function_inside_body():
    r = rf.decode_walk(0x10, _STRAY_BODY.get, lambda ea: ea == 0x14, stray_func=lambda ea: (0x14, 0x17))
    assert r["ok"] and r["end"] == 0x17 and r["strays"] == [(0x14, 0x17)]


@pytest.mark.parametrize(
    ("stray_func", "at"),
    [(None, 0x14),  # no stray predicate: as before
     (lambda ea: None, 0x14),  # the function has an xref or more than one instruction: not a stray
     (lambda ea: (0x14, 0x20), 0x14)],  # the function reaches past the body end
)
def test_walk_stray_near_misses_refused(stray_func, at):
    r = rf.decode_walk(0x10, _STRAY_BODY.get, lambda ea: ea == 0x14, stray_func=stray_func)
    assert not r["ok"] and r["check"] == "runs_into_function" and r["at"] == at


@pytest.mark.parametrize(
    ("insns", "chunks", "xrefs", "ok"),
    [(1, 1, [], True), (1, 1, [0x14], False), (2, 1, [], False), (1, 2, [], False)],
)
def test_is_stray(insns, chunks, xrefs, ok):
    assert rf.is_stray(insns, chunks, xrefs) is ok


# switch at 0x12 (jmp [eax*4+table]), case targets 0x19 and 0x1A (both ret), table at 0x40
_SWITCH_BODY = _prog((0x10, 2, "other", None), (0x12, 7, "jmp_indirect", None), (0x19, 1, "ret", None),
                     (0x1A, 1, "ret", None))


def _switch(targets, table=0x40):
    return lambda ea: {"targets": targets, "table": table, "table_size": 8} if ea == 0x12 else None


def test_walk_follows_switch_with_targets_in_body():
    r = rf.decode_walk(0x10, _SWITCH_BODY.get, lambda ea: False, switch=_switch([0x19, 0x1A]))
    assert r["ok"] and r["end"] == 0x1B and r["switches"][0]["ea"] == 0x12


@pytest.mark.parametrize(
    ("switch", "check"),
    [(None, "indirect_jump"),  # no switch info: as before
     (lambda ea: None, "indirect_jump"),
     (_switch([0x19, 0x5000]), "switch_target_out_of_body"),  # a case target outside the body
     (_switch([0x19, 0x08]), "switch_target_out_of_body"),  # a case target before the callback
     (_switch([0x19, 0x1A], table=0x14), "switch_table_in_body")],
)
def test_walk_switch_near_misses_refused(switch, check):
    r = rf.decode_walk(0x10, _SWITCH_BODY.get, lambda ea: False, switch=switch)
    assert not r["ok"] and r["check"] == check


# --- _apply order with an IDA fake ------------------------------------------------------------------

class _FakeIda:
    """Models the IDA behaviour T004d hit: undefining a function's entry instruction deletes the
    function, after which ``set_func_start`` returns ``MOVE_FUNC_NOFUNC`` (3)."""

    def __init__(self, funcs, code, add_end):
        self.fn = dict(funcs)
        self.code = dict(code)  # ea -> size
        self.add_end = add_end
        self.calls: list[tuple] = []
        self.undo_funcs = None
        self.bytes = NS(DELIT_SIMPLE=0, del_items=self._del_items, get_flags=lambda ea: ea in self.code,
                        is_code=bool)
        self.ua = NS(create_insn=self._create)
        self.funcs = NS(MOVE_FUNC_OK=0, set_func_start=self._set_start, del_func=self._del_func,
                        add_func=self._add_func)
        self.auto = NS(plan_and_wait=lambda lo, hi: None)

    def _del_items(self, ea, flags, size):
        self.calls.append(("del_items", ea))
        self.fn.pop(ea, None)  # IDA deletes a function whose entry instruction is undefined
        for a in [a for a in self.code if ea <= a < ea + size]:
            del self.code[a]

    def _create(self, ea):
        self.calls.append(("create_insn", ea))
        self.code[ea] = 1
        return 1

    def _set_start(self, enc, cb):
        self.calls.append(("set_func_start", enc))
        if enc not in self.fn:
            return 3
        self.fn[cb] = self.fn.pop(enc)
        return 0

    def _del_func(self, ea):
        self.calls.append(("del_func", ea))
        return self.fn.pop(ea, None) is not None

    def _add_func(self, ea):
        self.calls.append(("add_func", ea))
        if self.func_bounds(ea) is not None:
            return False
        self.fn[ea] = self.add_end
        return True

    def func_bounds(self, ea):
        for s, e in self.fn.items():
            if s <= ea < e:
                return (s, e)
        return None

    def functions_near(self, lo, hi):
        return dict(self.fn)

    def before_state(self, cb, action, lo, hi, items, func_starts):
        self.undo_funcs = [{"start": s, "end": self.fn[s]} for s in func_starts]
        return rf.undo_record(cb, action, lo, hi, items, self.undo_funcs, [], [])


def _inside_case():
    """T004d 0x7C3840: enclosing start 0x0F one byte before the callback 0x10, its first item
    (0x0F, 3) crosses the callback; the body 0x10..0x14 ends where the enclosing function ends."""
    insns = [{"ea": 0x10, "size": 3, "kind": "other"}, {"ea": 0x13, "size": 1, "kind": "ret"}]
    walk = {"ok": True, "end": 0x14, "insns": insns, "strays": [], "switches": []}
    gap = rf.gap_check(0x0F, 0x10, bytes([0x83]), [(0x0F, 3)], [], False)
    plan = rf.plan_repair(0x10, (0x0F, 0x14), walk, gap, {0x0F})
    items = [{"ea": 0x0F, "size": 3, "code": True}, {"ea": 0x12, "size": 2, "code": True}]
    plan["conflicting"] = rf.conflicting_items(items, insns, 0x10, 0x14)
    ida = _FakeIda({0x0F: 0x14, 0x30: 0x40}, {0x0F: 3, 0x12: 2}, add_end=0x14)
    return ida, plan, {"walk": walk, "items": items, "lo": 0x0F}


def test_apply_inside_function_deletes_then_adds():
    ida, plan, ctx = _inside_case()
    out = io.StringIO()
    r = rf._apply(ida, plan, ctx, out)
    assert r["status"] == "repaired", r
    assert ida.fn == {0x10: 0x14, 0x30: 0x40}
    # the function is deleted before any item is undefined, and created at the callback last
    assert ida.calls[0] == ("del_func", 0x0F) and ida.calls[-1] == ("add_func", 0x10)
    assert ("set_func_start", 0x0F) not in ida.calls
    # the undo record holds the deleted function and was written first
    assert ida.undo_funcs == [{"start": 0x0F, "end": 0x14}]
    assert json.loads(out.getvalue())["action"] == "replace_func"


def test_apply_stray_deleted_before_add_func():
    insns = [{"ea": 0x10, "size": 4, "kind": "other"}, {"ea": 0x14, "size": 3, "kind": "ret"}]
    walk = {"ok": True, "end": 0x17, "insns": insns, "strays": [(0x14, 0x17)], "switches": []}
    plan = rf.plan_repair(0x10, None, walk, None, {0x14})
    plan["conflicting"] = []
    ida = _FakeIda({0x14: 0x17}, {0x14: 3}, add_end=0x17)
    r = rf._apply(ida, plan, {"walk": walk, "items": [], "lo": 0x10}, io.StringIO())
    assert r["status"] == "repaired", r
    assert ida.fn == {0x10: 0x17}
    assert ida.calls.index(("del_func", 0x14)) < ida.calls.index(("add_func", 0x10))


def test_apply_junk_gap_items_become_unexplored():
    insns = [{"ea": 0x10, "size": 3, "kind": "other"}, {"ea": 0x13, "size": 1, "kind": "ret"}]
    walk = {"ok": True, "end": 0x14, "insns": insns, "strays": [], "switches": []}
    gap = rf.gap_check(0x0E, 0x10, bytes([0x56, 0x57]), [(0x0E, 1), (0x0F, 1)], [], False)
    plan = rf.plan_repair(0x10, (0x0E, 0x14), walk, gap, {0x0E})
    plan["conflicting"] = []
    plan["gap_items"] = [{"ea": 0x0E, "size": 1, "code": True}, {"ea": 0x0F, "size": 1, "code": True}]
    ida = _FakeIda({0x0E: 0x14}, {0x0E: 1, 0x0F: 1, 0x10: 3, 0x13: 1}, add_end=0x14)
    r = rf._apply(ida, plan, {"walk": walk, "items": [], "lo": 0x0E}, io.StringIO())
    assert r["status"] == "repaired", r
    assert 0x0E not in ida.code and 0x0F not in ida.code and ida.fn == {0x10: 0x14}


def test_apply_reports_failed_del_func():
    ida, plan, ctx = _inside_case()
    ida.funcs.del_func = lambda ea: False  # IDA refuses the deletion
    r = rf._apply(ida, plan, ctx, io.StringIO())
    assert r["status"] == "failed" and r["check"] == "del_func" and r["at"] == 0x0F


# --- batch entry ------------------------------------------------------------------------------------

def test_parse_batch_args():
    assert rf.parse_batch_args(["repair_functions.py", "D:/o.jsonl", "--apply"]) == {
        "out_path": "D:/o.jsonl", "apply": True, "extract_path": None}
    assert rf.parse_batch_args(["x", "o", "--extract-ida", "e.py"])["apply"] is False


def test_batch_runs_prints_summary_and_exits(capsys):
    seen, exits, killed = {}, [], []

    def run(**kw):
        seen.update(kw)
        return {"kind": "summary", "callbacks": 1}

    code = rf.batch(["repair_functions.py", "o.jsonl", "--apply"], run=run, qexit=exits.append,
                    kill=lambda: killed.append(1), wait=lambda: seen.setdefault("waited", True))
    assert code == 0 and exits == [0] and not killed
    assert seen["apply"] is True and seen["out_path"] == "o.jsonl" and seen["waited"]
    last = capsys.readouterr().out.strip().splitlines()[-1]
    assert last.startswith(rf.SUMMARY_PREFIX) and json.loads(last[len(rf.SUMMARY_PREFIX):])["callbacks"] == 1


def test_batch_failure_discards_and_exits_nonzero(capsys):
    exits, killed = [], []

    def run(**kw):
        raise ValueError("handler table not as audited")

    code = rf.batch(["repair_functions.py", "o.jsonl"], run=run, qexit=exits.append, kill=lambda: killed.append(1))
    assert code == 1 and exits == [1] and killed == [1]
    assert json.loads(capsys.readouterr().out.strip().splitlines()[-1][len(rf.SUMMARY_PREFIX):])["error"]

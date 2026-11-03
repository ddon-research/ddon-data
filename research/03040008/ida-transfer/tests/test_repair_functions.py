"""Pure parts of repair_functions.py, with fakes (no IDA)."""

from __future__ import annotations

from pathlib import Path

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
    assert rf.gap_check(0x10, 0x13, b"\xcc\xcc\xcc", [], [])["ok"]
    # item at 0x10 crosses the callback at 0x13: its bytes are a misdecoded tail, not checked
    r = rf.gap_check(0x10, 0x13, b"\x05\x5d\x35", [(0x10, 5)], [])
    assert r == {"ok": True, "misdecoded": 0x10}
    # padding before a crossing item is still checked
    assert rf.gap_check(0x10, 0x14, b"\xcc\x05\x5d\x35", [(0x11, 5)], [])["ok"]
    assert rf.gap_check(0x10, 0x14, b"\x56\x05\x5d\x35", [(0x11, 5)], [])["check"] == "gap_not_padding"


@pytest.mark.parametrize(
    ("gap", "heads", "refs", "check"),
    [(b"\xcc\xcc", [], [0x11], "gap_referenced"),  # something points into the gap
     (b"\x56\x57", [(0x10, 1), (0x11, 1)], [], "gap_not_padding"),  # real code, not padding
     (b"\xcc", [], [], "gap_unreadable")],
)
def test_gap_check_refusals(gap, heads, refs, check):
    assert rf.gap_check(0x10, 0x12, gap, heads, refs)["check"] == check


def test_conflicting_items():
    decoded = [{"ea": 0x13, "size": 1}, {"ea": 0x14, "size": 2}, {"ea": 0x16, "size": 1}]
    items = [{"ea": 0x10, "size": 5, "code": True},  # crosses the callback
             {"ea": 0x14, "size": 2, "code": False},  # data where code decodes
             {"ea": 0x16, "size": 1, "code": True},  # matches a decoded instruction: kept
             {"ea": 0x17, "size": 4, "code": False},  # after the body: kept
             {"ea": 0x0C, "size": 2, "code": True}]  # gap padding before: kept
    assert [i["ea"] for i in rf.conflicting_items(items, decoded, 0x13, 0x17)] == [0x10, 0x14]


_OK_WALK = {"ok": True, "end": 0x40, "insns": []}


def test_plan_no_function_and_inside_function():
    assert rf.plan_repair(0x10, None, _OK_WALK, None, set()) == {
        "va": 0x10, "missing": "no-function", "enclosing": None, "end": 0x40,
        "status": "would-repair", "action": "add_func"}
    p = rf.plan_repair(0x10, (0x0D, 0x40), _OK_WALK, {"ok": True, "misdecoded": None}, {0x0D})
    assert p["status"] == "would-repair" and p["action"] == "set_func_start" and p["enclosing"] == 0x0D


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

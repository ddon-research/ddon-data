"""apply_transfer.py with a fake IDA (no IDA here; the real run is T007b)."""

from __future__ import annotations

import copy
import io
import json
import re
from pathlib import Path

import pytest

import apply_transfer as at

HERE = Path(__file__).resolve().parent.parent
REAL = HERE / "manifest" / "transfer"
HEAD = (f"# 007 T006 transfer, PC 03040008 <- PS4 02020005; 2 accepted pairs; inputs: pc-ida.jsonl source "
        f"{at.PC_SHA256}; ps4-dwarf.jsonl source x")
WORK = "D:/research/DDON-binaries/IDA9.5/ddon-data-007work/2022_01_29_DDO_DUMP_FIX.exe.i64"


# --- fake IDA --------------------------------------------------------------------------------------

class FakeIda:
    def __init__(self, protos_by_parse=None):
        self.sha = at.PC_SHA256
        self.path = WORK
        self.names: dict[int, tuple[str, bool]] = {}
        self.funcs: set[int] = set()
        self.types: dict[int, tuple[str, bool]] = {}
        self.guessed: dict[int, str] = {}
        self.cmts: dict[int, str] = {}
        self.ltypes: dict[str, dict] = {}
        self.protos_by_parse = protos_by_parse or {}
        self.calls: list[tuple] = []
        self.log_fh: io.StringIO | None = None
        self.undo_seen_before_write: list[bool] = []
        self.mangle_name = None
        self.parse_fails: set[str] = set()
        self.decompile_fails: dict[int, str] = {}
        self.printed_by_parse: dict[str, str] = {}  # what IDA prints after applying a parse (default: the row)

    def _write(self, what, key):
        self.calls.append((what, key))
        if self.log_fh is not None:
            k = key if isinstance(key, str) else f"{key:#x}"
            recs = [json.loads(x) for x in self.log_fh.getvalue().splitlines() if x]
            self.undo_seen_before_write.append(any(r.get("kind") == "undo" and r["key"] == k for r in recs))

    def state(self):
        return copy.deepcopy((self.names, self.types, self.cmts, self.ltypes))

    def input_sha256(self):
        return self.sha

    def idb_path(self):
        return self.path

    def counts(self):
        return {"names": sum(1 for _n, u in self.names.values() if u),
                "typed_functions": sum(1 for _t, u in self.types.values() if u),
                "local_types": len(self.ltypes)}

    def get_name(self, ea):
        return self.names.get(ea, (f"sub_{ea:X}", False))[0]

    def has_user_name(self, ea):
        return self.names.get(ea, ("", False))[1]

    def name_ea(self, name):
        return next((ea for ea, (n, u) in self.names.items() if n == name and u), None)

    def set_name(self, ea, name):
        self._write("set_name", ea)
        if name == "":
            self.names.pop(ea, None)
        else:
            self.names[ea] = (self.mangle_name(name) if self.mangle_name else name, True)
        return True

    def func_start(self, ea):
        return ea if ea in self.funcs else None

    def get_type(self, ea):
        return self.types[ea][0] if ea in self.types else self.guessed.get(ea, "int __cdecl()")

    def is_userti(self, ea):
        return self.types.get(ea, ("", False))[1]

    def type_blob(self, ea):
        return ["blob", self.get_type(ea)] if self.is_userti(ea) else None

    def parse_prototype(self, plan):
        if plan["parse"] in self.parse_fails:
            return None, "parse_decl refused"
        return {"parse": plan["parse"], "text": self.protos_by_parse[plan["parse"]]}, None

    def apply_prototype(self, ea, tif):
        self._write("apply_tinfo", ea)
        self.types[ea] = (self.printed_by_parse.get(tif["parse"], tif["text"]), True)
        return True

    # a fake tinfo_t is the printed text (stored types) or a parse_prototype dict
    def func_tinfo(self, ea):
        return self.types[ea][0] if ea in self.types else None

    def func_parts(self, tif):
        text = tif["text"] if isinstance(tif, dict) else tif
        m = re.fullmatch(r"(?P<ret>.*?)\s*(?P<cc>__\w+)\((?P<args>.*)\)", text.strip())
        if not m:
            return None
        return {"cc": m["cc"], "ret": _fake_type(m["ret"]),
                "args": [_fake_arg(a) for a in at.split_args(m["args"])]}

    def type_equal(self, a, b):
        return a == b

    def restore_type(self, ea, blob):
        self._write("restore_type", ea)
        if blob is None:
            self.types.pop(ea, None)
        else:
            self.types[ea] = (blob[1], True)
        return True

    def get_func_cmt(self, ea):
        return self.cmts.get(ea, "")

    def set_func_cmt(self, ea, text):
        self._write("set_func_cmt", ea)
        if text:
            self.cmts[ea] = text
        else:
            self.cmts.pop(ea, None)
        return True

    def local_type(self, name):
        t = self.ltypes.get(name)
        return None if t is None else {**t, "blob": copy.deepcopy(t)}

    def declare_forward(self, name):
        self._write("declare_forward", name)
        self.ltypes[name] = {"forward": True}
        return None

    def define_struct(self, d):
        self._write("define_struct", d.name)
        self.ltypes[d.name] = {"forward": False, "size": d.size,
                               "members": d.row_members()}
        return None

    def delete_local_type(self, name):
        self._write("delete_local_type", name)
        return self.ltypes.pop(name, None) is not None

    def restore_local_type(self, name, before):
        self._write("restore_local_type", name)
        self.ltypes[name] = copy.deepcopy(before["blob"])
        return True

    def decompile(self, ea):
        return self.decompile_fails.get(ea)


_KEYWORDS = {"int", "char", "bool", "void", "__int8", "__int16", "__int32", "__int64", "_DWORD", "unsigned",
             "signed", "short", "long", "float", "double"}


def _fake_type(t: str) -> str:
    """Type identity as IDA has it: ``struct `` is a printing detail, spacing too."""
    t = re.sub(r"\bstruct\s+", "", t)
    return re.sub(r"\s*\*\s*", "*", " ".join(t.split())).strip()


def _fake_arg(a: str) -> tuple[str, str]:
    m = re.fullmatch(r"(?P<t>.*?[\s*])(?P<n>[A-Za-z_]\w*)", a.strip())
    if m and m["t"].strip() and m["n"] not in _KEYWORDS:
        return _fake_type(m["t"]), m["n"]
    return _fake_type(a), ""


# --- a small manifest ------------------------------------------------------------------------------

TYPES_H = """// header
// Generated by transfer.py

struct CPacket;
struct MtTypedArray<CDataA>;

#pragma pack(push, 1)
struct MtArray // PC size 0x8
{
  void *__vftable; // +0x0 4 vptr
  unsigned int mLength; // +0x4 4
};

struct MtTypedArray<CDataA> // PC size 0x8
{
  MtArray baseclass_0; // +0x0 8 base MtArray
};

struct CDataB // PC size 0xc
{
  unsigned __int8 m_ucX; // +0x0 1
  unsigned __int8 gap1[3];
  MtTypedArray<CDataA> m_list; // +0x4 8
};
#pragma pack(pop)
"""

PROTO_A = "int __cdecl(CPacket *packet, MtTypedArray<CDataA> *ar)"
PROTO_B = "bool __thiscall(CDataB *this, unsigned __int8 job)"


def _tsv(path: Path, cols, rows):
    lines = [HEAD, "\t".join(cols)] + ["\t".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def make_manifest(d: Path, types_h: str = TYPES_H, type_status=None) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    _tsv(d / "names.tsv", ["pc_va", "action", "name", "current", "source", "basis", "reason"], [
        ["0x1000", "set", "nPacket::Read_CDataA_", "sub_1000", "ps4-symbol", "b", "default name"],
        ["0x2000", "set", "CDataB::job", "sub_2000", "ps4-symbol", "b", "default name"],
        ["0x3000", "set", "cSeed::OnPacket_X", "sub_3000", "pc-string", "tier0", "default name"],
        ["0x2ffd", "remove-label", "", "cSeed::OnPacket_X", "T004f", "stale", "T004f"],
    ])
    _tsv(d / "prototypes.tsv", ["pc_va", "action", "decl", "current", "basis", "notes", "types", "enums"], [
        ["0x1000", "set", PROTO_A, "int __cdecl(int, int)", "b", "-", "CPacket MtTypedArray<CDataA>", "-"],
        ["0x2000", "set", PROTO_B, "char __thiscall(_DWORD *this, int)", "b", "ecx this", "CDataB", "-"],
    ])
    _tsv(d / "comments.tsv", ["pc_va", "action", "comment", "existing"], [
        ["0x1000", "set", "PS4 02020005: nPacket::Read<CDataA>; paired by element-reader.", ""],
        ["0x2000", "set", "PS4 02020005: CDataB::job; paired by x.", "old"],
    ])
    status = type_status or {}
    _tsv(d / "types.tsv", ["type", "kind", "status", "basis"], [
        ["CPacket", "opaque", "declared", "-"],
        ["MtArray", "struct", status.get("MtArray", "embedded"), "reason MtArray"],
        ["MtTypedArray<CDataA>", "struct", "accepted", "-"],
        ["CDataB", "struct", status.get("CDataB", "accepted"), "reason CDataB"],
    ])
    _tsv(d / "skipped.tsv", ["rule", "item", "candidate", "action", "reason"], [
        ["names", "0x4000", "cSeed::OnPacket_Y", "conflict", "current non-default name"],
        ["names", "0x775310", "nPacket::Read_Z_", "equal", "already"],
    ])
    (d / "types.h").write_text(HEAD.replace("#", "//", 1) + "\n" + types_h, encoding="utf-8", newline="\n")
    return d


def fake_for(manifest: dict) -> FakeIda:
    special = at.special_names(at.parse_types_h(manifest["types_h"]), manifest)
    ida = FakeIda({at.prototype_plan(r["decl"], special)["parse"]: r["decl"] for r in manifest["prototypes"]})
    ida.funcs = {0x1000, 0x2000, 0x3000}
    ida.names[0x2ffd] = ("cSeed::OnPacket_X", True)
    ida.guessed[0x1000] = "int __cdecl(int, int)"
    ida.guessed[0x2000] = "char __thiscall(_DWORD *this, int)"
    ida.cmts[0x2000] = "old"
    return ida


@pytest.fixture
def man(tmp_path):
    return at.load_manifest(str(make_manifest(tmp_path / "m")))


def run(ida, manifest, apply=True):
    fh = io.StringIO()
    ida.log_fh = fh
    summary = at.run_apply(ida, manifest, apply, at.Log(fh))
    ida.log_fh = None
    return summary, [json.loads(x) for x in fh.getvalue().splitlines()]


def results(recs, step=None):
    return {r["key"]: r for r in recs if r.get("kind") == "result" and (step is None or r["step"] == step)}


# --- the real T006 manifest ------------------------------------------------------------------------

@pytest.mark.skipif(not (REAL / "types.h").exists(), reason="T006 manifest not present")
def test_real_manifest_loads_and_every_row_plans():
    m = at.load_manifest(str(REAL))
    assert (len(m["names"]), len(m["labels"]), len(m["prototypes"]), len(m["comments"])) == (1079, 3, 1011, 1119)
    assert len(m["conflicts"]) == 61
    decls = at.parse_types_h(m["types_h"])
    kinds = [d.kind for d in decls]
    assert (kinds.count("struct"), kinds.count("opaque")) == (91, 90)  # T006b, T006c: 6 lea-only out
    special = at.special_names(decls, m)
    assert sum("<" in n for n in special) >= 84
    plans = [at.prototype_plan(r["decl"], special) for r in m["prototypes"]]
    assert all("<" not in p["parse"] for p in plans)
    for d in decls:
        if d.kind == "struct":
            assert d.name in m["types"]


# --- pure parts -----------------------------------------------------------------------------------

def test_types_h_parse_members_and_flags():
    decls = {d.name: d for d in at.parse_types_h(TYPES_H) if d.kind == "struct"}
    mt = decls["MtArray"].members
    assert mt[0].vptr and mt[0].ptr == 1 and mt[0].type == "void"
    b = decls["CDataB"].members
    assert [(m.name, m.offset, m.size) for m in b] == [("m_ucX", 0, 1), ("gap1", 1, 3), ("m_list", 4, 8)]
    assert decls["MtTypedArray<CDataA>"].members[0].base
    assert decls["CDataB"].refs() == {"unsigned __int8", "MtTypedArray<CDataA>"}


def test_types_h_layout_not_contiguous_fails_closed():
    bad = TYPES_H.replace("unsigned __int8 gap1[3];\n", "")
    with pytest.raises(ValueError, match="m_list at 0x4, expected 0x1"):
        at.parse_types_h(bad)


def test_types_h_size_mismatch_and_unknown_line_fail_closed():
    with pytest.raises(ValueError, match="size 0x10"):
        at.parse_types_h(TYPES_H.replace("CDataB // PC size 0xc", "CDataB // PC size 0x10"))
    with pytest.raises(ValueError, match="unexpected"):
        at.parse_types_h(TYPES_H + "enum E { A };\n")


def test_prototype_plan_patches_template_pointer():
    p = at.prototype_plan(PROTO_A, ["MtTypedArray<CDataA>"])
    assert p == {"parse": "int __cdecl __t007_f(CPacket *packet, void *ar);",
                 "patch": [(1, "MtTypedArray<CDataA>", 1)]}
    assert at.prototype_plan(PROTO_B, ["MtTypedArray<CDataA>"])["patch"] == []


def test_prototype_plan_refuses_template_by_value():
    with pytest.raises(ValueError, match="by value"):
        at.prototype_plan("int __cdecl(MtTypedArray<CDataA> ar)", ["MtTypedArray<CDataA>"])


def test_merged_comment_keeps_existing():
    assert at.merged_comment("", "ours") == "ours"
    assert at.merged_comment("theirs", "ours") == "theirs\n----\nours"
    assert at.merged_comment("theirs\n----\nours", "ours") is None


def test_unescape_inverts_transfer_cells():
    assert at._unescape(r"a\nb\tc\\n") == "a\nb\tc\\n"


def test_manifest_from_another_pc_source_fails_closed(tmp_path):
    d = make_manifest(tmp_path / "m")
    p = d / "comments.tsv"
    text = p.read_text(encoding="utf-8").replace(at.PC_SHA256, "0" * 64)
    p.write_text(text, encoding="utf-8", newline="\n")
    with pytest.raises(ValueError, match="comments.tsv"):
        at.load_manifest(str(d))


def test_precheck_refuses_other_database_and_non_work_copy(man):
    ida = fake_for(man)
    ida.sha = "0" * 64
    with pytest.raises(ValueError, match="not the PC"):
        run(ida, man)
    ida = fake_for(man)
    ida.path = "D:/research/DDON-binaries/IDA9.5/PC_DDON_03040008/2022_01_29_DDO_DUMP_FIX.exe.i64"
    with pytest.raises(ValueError, match="ddon-data-007work"):
        run(ida, man)


# --- apply ----------------------------------------------------------------------------------------

def test_dry_run_writes_nothing(man):
    ida = fake_for(man)
    before = ida.state()
    summary, recs = run(ida, man, apply=False)
    assert ida.state() == before and ida.calls == []
    assert not [r for r in recs if r["kind"] == "undo"]
    st = summary["steps"]
    assert st["names"] == {"would-set": 3} and st["prototypes"] == {"would-set": 2}
    assert st["types"] == {"would-declare": 1, "would-define": 3}


def test_apply_writes_everything_and_undo_precedes_each_write(man):
    ida = fake_for(man)
    summary, recs = run(ida, man)
    st = summary["steps"]
    assert st["types"] == {"declared": 1, "defined": 3}
    assert st["remove-label"] == {"removed": 1}
    assert st["names"] == {"set": 3} and st["prototypes"] == {"set": 2} and st["comments"] == {"set": 2}
    assert st["conflict-names"] == {"conflict": 1}
    assert ida.get_name(0x3000) == "cSeed::OnPacket_X" and not ida.has_user_name(0x2ffd)
    assert ida.cmts[0x2000] == "old\n----\nPS4 02020005: CDataB::job; paired by x."
    assert ida.types[0x1000] == (PROTO_A, True)
    assert ida.ltypes["CDataB"]["members"][2] == ("m_list", 4, 8, "", "MtTypedArray<CDataA>")
    assert len(ida.undo_seen_before_write) == len(ida.calls) > 0 and all(ida.undo_seen_before_write)
    assert 0x4000 not in ida.names  # the conflict row is reported, never written


def test_second_apply_is_a_no_op(man):
    ida = fake_for(man)
    run(ida, man)
    after_first = ida.state()
    ida.calls.clear()
    summary, recs = run(ida, man)
    assert ida.state() == after_first and ida.calls == []
    assert not [r for r in recs if r["kind"] == "undo"]
    for step, st in summary["steps"].items():
        assert set(st) == ({"conflict"} if step.startswith("conflict") else {"already"}), (step, st)


def test_name_used_at_another_address_is_refused(man):
    ida = fake_for(man)
    ida.names[0x9000] = ("CDataB::job", True)
    _s, recs = run(ida, man)
    r = results(recs, "names")["0x2000"]
    assert r["status"] == "refused" and r["check"] == "name-used-elsewhere" and r["at"] == "0x9000"
    assert ida.get_name(0x2000) == "sub_2000"


def test_removed_label_frees_its_name_but_a_refused_one_does_not(man):
    ida = fake_for(man)
    ida.names[0x2ffd] = ("someone_else", True)  # the label changed since T006: not removed
    ida.names[0x2ffe] = ("cSeed::OnPacket_X", True)
    _s, recs = run(ida, man)
    assert results(recs, "remove-label")["0x2ffd"]["check"] == "current-changed"
    assert results(recs, "names")["0x3000"]["check"] == "name-used-elsewhere"


def test_current_name_changed_is_refused(man):
    ida = fake_for(man)
    ida.names[0x1000] = ("my_name", True)
    _s, recs = run(ida, man)
    r = results(recs, "names")["0x1000"]
    assert r["status"] == "refused" and r["db"] == "my_name" and r["row"] == "sub_1000"


def test_existing_different_local_type_is_refused_with_dependents(man):
    ida = fake_for(man)
    ida.ltypes["MtArray"] = {"forward": False, "size": 8, "members": [("x", 0, 8)]}
    _s, recs = run(ida, man)
    t = results(recs, "types")
    assert t["MtArray"]["status"] == "refused" and t["MtArray"]["check"] == "different-local-type"
    assert t["MtArray"]["existing"] == {"size": 8, "members": [["x", 0, 8]]}
    assert t["MtTypedArray<CDataA>"]["check"] == "embeds-refused-type"
    assert t["CDataB"]["types"] == ["MtTypedArray<CDataA>"]
    assert ida.ltypes["MtArray"]["members"] == [("x", 0, 8)]
    p = results(recs, "prototypes")
    assert p["0x1000"]["check"] == "uses-refused-type" and p["0x2000"]["check"] == "uses-refused-type"


def test_existing_different_local_type_replaced_only_with_a_replace_row(tmp_path):
    m = at.load_manifest(str(make_manifest(tmp_path / "m", type_status={"MtArray": "replace"})))
    ida = fake_for(m)
    ida.ltypes["MtArray"] = {"forward": False, "size": 8, "members": [("x", 0, 8)]}
    _s, recs = run(ida, m)
    r = results(recs, "types")["MtArray"]
    assert r["status"] == "replaced" and r["reason"] == "reason MtArray"
    assert [u for u in recs if u["kind"] == "undo" and u["key"] == "MtArray"][0]["before"]["members"] == [["x", 0, 8]]


def test_existing_equal_type_and_forward_decl(man):
    ida = fake_for(man)
    ida.ltypes["MtArray"] = {"forward": False, "size": 8, "members": [("__vftable", 0, 4), ("mLength", 4, 4)]}
    ida.ltypes["CDataB"] = {"forward": True}
    _s, recs = run(ida, man)
    t = results(recs, "types")
    assert t["MtArray"]["status"] == "already" and t["CDataB"]["status"] == "defined"


def test_existing_comment_kept(man):
    ida = fake_for(man)
    run(ida, man)
    assert ida.cmts[0x2000].startswith("old\n----\n")


def test_failed_read_back_reports_both_values_without_retry(man):
    ida = fake_for(man)
    ida.mangle_name = lambda n: n.replace("::", "__")
    _s, recs = run(ida, man)
    r = results(recs, "names")["0x2000"]
    assert r == {"kind": "result", "step": "names", "key": "0x2000", "status": "failed", "check": "read-back",
                 "db": "CDataB__job", "row": "CDataB::job"}
    assert ida.calls.count(("set_name", 0x2000)) == 1


def test_prototype_parse_failure_is_refused_before_any_write(man):
    ida = fake_for(man)
    special = at.special_names(at.parse_types_h(man["types_h"]), man)
    ida.parse_fails = {at.prototype_plan(PROTO_B, special)["parse"]}
    _s, recs = run(ida, man)
    r = results(recs, "prototypes")["0x2000"]
    assert r["status"] == "refused" and r["check"] == "parse"
    assert not [u for u in recs if u["kind"] == "undo" and u["step"] == "prototypes" and u["key"] == "0x2000"]
    assert 0x2000 not in ida.types


def test_user_prototype_or_changed_current_is_refused(man):
    ida = fake_for(man)
    ida.types[0x1000] = ("int __cdecl(int, int)", True)
    ida.guessed[0x2000] = "int __thiscall(void *this)"
    _s, recs = run(ida, man)
    p = results(recs, "prototypes")
    assert p["0x1000"]["check"] == "user-prototype" and p["0x2000"]["check"] == "current-changed"


# --- verify and undo ------------------------------------------------------------------------------

def _verify(ida, man, apply_recs):
    fh = io.StringIO()
    s = at.run_verify(ida, man, apply_recs, at.Log(fh))
    return s, [json.loads(x) for x in fh.getvalue().splitlines()]


def test_verify_after_apply_is_clean_and_counts_match(man):
    ida = fake_for(man)
    _s, recs = run(ida, man)
    s, vrecs = _verify(ida, man, recs)
    assert s["counts_ok"] is True
    for step, st in s["steps"].items():
        assert set(st) == {"ok"}, (step, st)
    counts = [r for r in vrecs if r["kind"] == "counts"][0]
    assert counts["applied_delta"] == {"names": 2, "typed_functions": 2, "local_types": 4}


def test_verify_finds_a_change_outside_the_rows_and_a_decompile_failure(man):
    ida = fake_for(man)
    _s, recs = run(ida, man)
    ida.names[0x7777] = ("stray", True)
    ida.decompile_fails[0x1000] = "bad"
    s, vrecs = _verify(ida, man, recs)
    assert s["counts_ok"] is False
    assert results(vrecs, "decompile")["0x1000"] == {"kind": "result", "step": "decompile", "key": "0x1000",
                                                      "status": "failed", "error": "bad"}


def test_verify_reports_a_row_not_in_the_database(man):
    ida = fake_for(man)
    _s, recs = run(ida, man)
    ida.cmts[0x1000] = ""
    s, vrecs = _verify(ida, man, recs)
    assert results(vrecs, "comments")["0x1000"]["status"] == "mismatch"


def test_verify_needs_an_apply_log(man):
    ida = fake_for(man)
    _s, recs = run(ida, man, apply=False)
    with pytest.raises(ValueError, match="not an apply log"):
        _verify(ida, man, recs)


def test_undo_restores_the_before_state(man):
    ida = fake_for(man)
    ida.ltypes["CDataB"] = {"forward": True}
    before = ida.state()
    _s, recs = run(ida, man)
    assert ida.state() != before
    fh = io.StringIO()
    s = at.run_undo(ida, man, recs, at.Log(fh))
    assert ida.state() == before
    assert set(s["steps"]["names"]) == {"restored"} and set(s["steps"]["types"]) == {"restored"}


# --- batch entry ----------------------------------------------------------------------------------

def _batch(argv, run_fn):
    calls = []
    code = at.batch(argv, run=run_fn, kill=lambda: calls.append("kill"), qexit=lambda c: calls.append(("qexit", c)))
    return code, calls


def test_batch_modes_save_only_on_apply_and_undo():
    ok = lambda **kw: {"kind": "summary", "mode": kw["mode"]}  # noqa: E731
    assert _batch(["s", "dir", "out"], ok) == (0, ["kill", ("qexit", 0)])
    assert _batch(["s", "dir", "out", "--apply"], ok) == (0, [("qexit", 0)])
    assert _batch(["s", "dir", "out", "--undo", "a.jsonl"], ok) == (0, [("qexit", 0)])
    assert _batch(["s", "dir", "out", "--verify", "--apply-log", "a.jsonl"], ok) == (0, ["kill", ("qexit", 0)])


def test_batch_error_kills_and_exits_1():
    def boom(**_kw):
        raise ValueError("x")

    assert _batch(["s", "dir", "out", "--apply"], boom) == (1, ["kill", ("qexit", 1)])
    assert _batch(["s", "dir", "out", "--verify"], boom)[0] == 1  # --verify without --apply-log
    assert _batch(["s", "dir", "out", "--apply", "--verify", "--apply-log", "a"], boom)[0] == 1


def test_main_writes_out_atomically(tmp_path):
    d = make_manifest(tmp_path / "m")
    m = at.load_manifest(str(d))
    ida = fake_for(m)
    out = tmp_path / "dry.jsonl"
    s = at.main(str(d), str(out), "dry-run", ida=ida)
    recs = [json.loads(x) for x in out.read_text(encoding="utf-8", newline="\n").splitlines()]
    assert recs[0]["kind"] == "header" and recs[0]["manifest_sha256"]["types.h"] == m["sha256"]["types.h"]
    assert recs[-1] == s and not (tmp_path / "dry.jsonl.tmp").exists()


# --- IDA's vptr / base-class member conventions (T007c) ---------------------------------------------

TYPES_H_IDA = """// header

struct CPacket;

#pragma pack(push, 1)
struct MtObject // PC size 0x4
{
  void *__vftable; // +0x0 4 vptr
};

struct CPacketDataBase // PC size 0x4
{
  MtObject baseclass_0; // +0x0 4 base MtObject
};

struct MtArray // PC size 0x14
{
  MtObject baseclass_0; // +0x0 4 base MtObject
  unsigned int mLength; // +0x4 4
  unsigned int mBufsiz; // +0x8 4
  bool mAutoDelete; // +0xc 1
  unsigned __int8 gapD[3];
  MtObject *mpArray; // +0x10 4
};

struct MtTypedArray<CDataA> // PC size 0x14
{
  MtArray baseclass_0; // +0x0 20 base MtArray
};

struct CDataB // PC size 0x18
{
  CPacketDataBase baseclass_0; // +0x0 4 base CPacketDataBase
  MtTypedArray<CDataA> m_list; // +0x4 20
};
#pragma pack(pop)
"""

# the three T007b work-copy types (dumps/apply-dryrun.jsonl ``existing``), as the adapter reads them
T007B = {
    "MtObject": {"forward": False, "size": 4, "members": [("_vptr$MtObject", 0, 4, "vptr", "")]},
    "CPacketDataBase": {"forward": False, "size": 4, "members": [("", 0, 4, "base", "MtObject")]},
    "MtArray": {"forward": False, "size": 20, "members": [
        ("", 0, 4, "base", "MtObject"), ("mLength", 4, 4, "", "unsigned int"), ("mBufsiz", 8, 4, "", "unsigned int"),
        ("mAutoDelete", 12, 1, "", "bool"), ("mpArray", 16, 4, "", "")]},
}


@pytest.fixture
def man_ida(tmp_path):
    return at.load_manifest(str(make_manifest(tmp_path / "m", types_h=TYPES_H_IDA)))


def test_t007b_types_are_already_and_their_dependents_written(man_ida):
    ida = fake_for(man_ida)
    ida.ltypes.update(copy.deepcopy(T007B))
    _s, recs = run(ida, man_ida)
    t = results(recs, "types")
    assert {k: t[k]["status"] for k in T007B} == dict.fromkeys(T007B, "already")
    assert t["MtTypedArray<CDataA>"]["status"] == "defined" and t["CDataB"]["status"] == "defined"
    assert {r["status"] for r in results(recs, "prototypes").values()} == {"set"}
    assert ida.ltypes["MtArray"] == T007B["MtArray"]  # left as IDA had it


def test_ida_conventions_without_flags_are_equal():
    d = {x.name: x for x in at.parse_types_h(TYPES_H_IDA) if x.kind == "struct"}
    assert at.same_layout(4, [("vfptr", 0, 4)], d["MtObject"])
    assert at.same_layout(4, [("__vftable", 0, 4, "", "")], d["MtObject"])
    for name in ("baseclass_0", "", "MtObject"):
        assert at.same_layout(4, [(name, 0, 4, "", "MtObject")], d["CPacketDataBase"])
    assert not at.same_layout(4, [("", 0, 4)], d["CPacketDataBase"])  # base type unknown


def test_vptr_name_with_a_size_difference_is_refused(man_ida):
    ida = fake_for(man_ida)
    ida.ltypes["MtObject"] = {"forward": False, "size": 8, "members": [("_vptr$MtObject", 0, 8, "vptr", "")]}
    _s, recs = run(ida, man_ida)
    t = results(recs, "types")
    assert t["MtObject"]["status"] == "refused" and t["MtObject"]["check"] == "different-local-type"
    assert t["CPacketDataBase"]["check"] == "embeds-refused-type"


def test_base_of_another_type_at_the_same_offset_is_refused(man_ida):
    ida = fake_for(man_ida)
    ida.ltypes["CPacketDataBase"] = {"forward": False, "size": 4, "members": [("", 0, 4, "base", "MtString")]}
    _s, recs = run(ida, man_ida)
    t = results(recs, "types")
    assert t["CPacketDataBase"]["status"] == "refused" and t["CPacketDataBase"]["check"] == "different-local-type"
    assert t["CPacketDataBase"]["existing"]["members"] == [["", 0, 4, "base", "MtString"]]
    assert t["CDataB"]["check"] == "embeds-refused-type"


def test_other_differences_still_refuse():
    d = {x.name: x for x in at.parse_types_h(TYPES_H_IDA) if x.kind == "struct"}
    mt = [list(m) for m in T007B["MtArray"]["members"]]
    assert at.same_layout(20, mt, d["MtArray"])
    renamed = copy.deepcopy(mt)
    renamed[1][0] = "mLen"
    assert not at.same_layout(20, renamed, d["MtArray"])
    vptr_not_at_0 = copy.deepcopy(mt)
    vptr_not_at_0[1][:4] = ["_vptr$X", 4, 4, "vptr"]
    assert not at.same_layout(20, vptr_not_at_0, d["MtArray"])
    base_as_vptr = [("__vftable", 0, 4, "vptr", "")]
    assert not at.same_layout(4, base_as_vptr, d["CPacketDataBase"])
    assert not at.same_layout(4, [("_vptr$MtObject", 0, 4, "base", "MtObject")], d["MtObject"])
    assert not at.same_layout(20, mt[:-1], d["MtArray"])


def test_ida_convention_second_apply_is_a_no_op(man_ida):
    ida = fake_for(man_ida)
    ida.ltypes.update(copy.deepcopy(T007B))
    _s, recs = run(ida, man_ida)
    _s2, recs2 = run(ida, man_ida)
    assert {r["status"] for r in results(recs2).values() if r["step"] != "conflict-names"} == {"already"}


# --- prototypes compared as types (T007d) ------------------------------------------------------------

STRUCT_A = "int __cdecl(struct CPacket *packet, struct MtTypedArray<CDataA> *ar)"


def test_struct_prefixed_print_is_set_already_and_verified(man):
    ida = fake_for(man)
    special = at.special_names(at.parse_types_h(man["types_h"]), man)
    ida.printed_by_parse[at.prototype_plan(PROTO_A, special)["parse"]] = STRUCT_A
    _s, recs = run(ida, man)
    assert results(recs, "prototypes")["0x1000"]["status"] == "set"
    assert ida.types[0x1000] == (STRUCT_A, True)
    _s2, recs2 = run(ida, man)
    assert results(recs2, "prototypes")["0x1000"]["status"] == "already"
    assert not [u for u in recs2 if u["kind"] == "undo"]
    s, vrecs = _verify(ida, man, recs)
    assert results(vrecs, "prototypes")["0x1000"]["status"] == "ok" and s["steps"]["prototypes"] == {"ok": 2}


def _db_has(man, ea, text):
    ida = fake_for(man)
    ida.types[ea] = (text, True)
    _s, recs = run(ida, man)
    return results(recs, "prototypes")[f"{ea:#x}"]


def test_template_and_namespace_argument_equal():
    ida = FakeIda()
    row = {"text": PROTO_A}
    assert at.same_prototype(ida, STRUCT_A, row)
    assert at.same_prototype(ida, "int __cdecl(struct nA::B *p)", {"text": "int __cdecl(nA::B *p)"})
    assert not at.same_prototype(ida, "int __stdcall(struct nA::B *p)", {"text": "int __cdecl(nA::B *p)"})
    assert not at.same_prototype(ida, "char __cdecl(struct nA::B *p)", {"text": "int __cdecl(nA::B *p)"})
    assert not at.same_prototype(ida, "int __cdecl(struct nA::B *p, int)", {"text": "int __cdecl(nA::B *p)"})


def test_different_argument_type_is_not_already(man):
    r = _db_has(man, 0x1000, "int __cdecl(struct CPacket *packet, struct MtTypedArray<CDataB> *ar)")
    assert r["status"] == "refused" and r["check"] == "user-prototype"
    r = _db_has(man, 0x1000, "int __cdecl(struct CPacket **packet, struct MtTypedArray<CDataA> *ar)")
    assert r["check"] == "user-prototype"


def test_different_argument_name_is_not_already(man):
    r = _db_has(man, 0x1000, "int __cdecl(struct CPacket *pkt, struct MtTypedArray<CDataA> *ar)")
    assert r["status"] == "refused" and r["check"] == "user-prototype"


def test_read_back_with_another_type_fails(man):
    ida = fake_for(man)
    special = at.special_names(at.parse_types_h(man["types_h"]), man)
    ida.printed_by_parse[at.prototype_plan(PROTO_A, special)["parse"]] = STRUCT_A.replace("CDataA", "CDataB")
    _s, recs = run(ida, man)
    r = results(recs, "prototypes")["0x1000"]
    assert r["status"] == "failed" and r["db"] == STRUCT_A.replace("CDataA", "CDataB") and r["row"] == PROTO_A


def test_verify_reports_a_prototype_with_another_argument_name(man):
    ida = fake_for(man)
    _s, recs = run(ida, man)
    ida.types[0x2000] = ("bool __thiscall(CDataB *this, unsigned __int8 jobId)", True)
    _s2, vrecs = _verify(ida, man, recs)
    assert results(vrecs, "prototypes")["0x2000"]["status"] == "mismatch"


# --- an untransferred base compares by its class (T007f) ---------------------------------------------

TYPES_H_OPAQUE_BASE = TYPES_H_IDA.replace("""struct MtArray // PC size 0x14
{
  MtObject baseclass_0; // +0x0 4 base MtObject
""", """struct MtArray // PC size 0x14
{
  unsigned __int8 baseclass_0[4]; // +0x0 4 base MtObject (not transferred)
""")


@pytest.fixture
def man_opaque(tmp_path):
    assert TYPES_H_OPAQUE_BASE != TYPES_H_IDA
    return at.load_manifest(str(make_manifest(tmp_path / "m", types_h=TYPES_H_OPAQUE_BASE)))


def test_untransferred_base_is_parsed_with_its_class():
    d = {x.name: x for x in at.parse_types_h(TYPES_H_OPAQUE_BASE) if x.kind == "struct"}
    b = d["MtArray"].members[0]
    assert (b.base, b.base_of, b.type, b.count) == (True, "MtObject", "unsigned __int8", 4)
    assert d["CPacketDataBase"].members[0].base_of is None


def test_untransferred_base_not_rendered_as_bytes_fails_closed():
    bad = TYPES_H_OPAQUE_BASE.replace("unsigned __int8 baseclass_0[4]; // +0x0 4 base MtObject (not",
                                      "unsigned __int8 other[4]; // +0x0 4 base MtObject (not")
    with pytest.raises(ValueError, match="untransferred base"):
        at.parse_types_h(bad)


def test_t007e_untransferred_base_is_already_and_dependents_planned(man_opaque):
    ida = fake_for(man_opaque)
    ida.ltypes.update(copy.deepcopy(T007B))
    _s, recs = run(ida, man_opaque, apply=False)
    t = results(recs, "types")
    assert t["MtArray"]["status"] == "already"
    assert t["MtTypedArray<CDataA>"]["status"] == "would-define" and t["CDataB"]["status"] == "would-define"
    assert "refused" not in {r["status"] for r in results(recs, "prototypes").values()}
    _s, recs = run(ida, man_opaque)
    assert ida.ltypes["MtArray"] == T007B["MtArray"]  # the database's richer base is kept


def test_untransferred_base_of_another_class_is_refused(man_opaque):
    ida = fake_for(man_opaque)
    ida.ltypes.update(copy.deepcopy(T007B))
    ida.ltypes["MtArray"]["members"][0] = ("", 0, 4, "base", "MtString")
    _s, recs = run(ida, man_opaque, apply=False)
    t = results(recs, "types")
    assert t["MtArray"]["status"] == "refused" and t["MtArray"]["check"] == "different-local-type"
    assert t["MtTypedArray<CDataA>"]["check"] == "embeds-refused-type"


def test_untransferred_base_with_another_size_or_offset_is_refused():
    d = {x.name: x for x in at.parse_types_h(TYPES_H_OPAQUE_BASE) if x.kind == "struct"}
    mt = [list(m) for m in T007B["MtArray"]["members"]]
    assert at.same_layout(20, mt, d["MtArray"])
    row = d["MtArray"].members[0]
    assert not at.member_equal(at.existing_member(("", 0, 8, "base", "MtObject")), row)
    assert not at.member_equal(at.existing_member(("", 4, 4, "base", "MtObject")), row)
    assert not at.member_equal(at.existing_member(("x", 0, 4, "", "MtObject")), row)
    assert not at.member_equal(at.existing_member(("", 0, 4, "base", "unsigned __int8")), row)

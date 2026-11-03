"""007 T013c wave 2: member links, partial layouts, locals R1-R3 (synthetic dumps; the real run is in the
manifest), and the apply's locals step and forward-declaration fill (fake IDA)."""

from __future__ import annotations

import io
import json
from dataclasses import replace
from pathlib import Path

import pytest

import apply_transfer as at
from matcher.model import Access, Facts, Func
from transfer import locals as lmod
from transfer import wave2, wave2_run
from transfer.inputs import Ps4Fn
from transfer.layout import Layouts

HERE = Path(__file__).resolve().parent.parent
CLS = "nUserSession::CPacket_S2C_X_RES"
H, R, H4, R4 = 0x50, 0x100, 0x800, 0x900  # PC handler, PC reader, PS4 handler, PS4 reader
CODEC, CODEC4 = 0x8BC410, 0x1A0A000
TYPES = {
    "u32": {"tag": "typedef", "name": "u32", "target": "unsigned int"},
    "u8": {"tag": "typedef", "name": "u8", "target": "unsigned char"},
    "CPacket": {"tag": "class", "name": "CPacket", "size": 56, "members": []},
    CLS: {"tag": "class", "name": CLS, "size": 32, "members": [
        {"name": "m_a", "offset": 16, "size": 4, "type": "u32"},
        {"name": "m_b", "offset": 20, "size": 1, "type": "u8"},
        {"name": "m_c", "offset": 24, "size": 4, "type": "u32"}]},
}
READER_PARAMS = [{"name": "this", "type": f"{CLS}*", "artificial": True}, {"name": "pPacket", "type": "CPacket*"}]
HANDLER_PARAMS = [{"name": "this", "type": "cSeedGameSvConnection*", "artificial": True},
                  {"name": "pPacket", "type": "CPacket*"}]


def pcf(va, accesses=(), ecx=True):
    return Func(va=va, name=f"sub_{va:X}", side="pc", size=100, instructions=20, calls=[], ecx_read_before_write=ecx,
                ret_imm=(4,), accesses=tuple(accesses))


def obj(slot, disp, loc="ecx", arg=0):
    return wave2.Arg(slot, "obj", arg, loc, disp, None, 0x1)


def stack(slot, frame, def_ea=0x2):
    return wave2.Arg(slot, "stack", None, None, 0, frame, def_ea)


def world(codec_rows=((0x18, 16, "4"),), accesses=(), handler_args=None, ps4_handler_args=None, strings=True,
          dw_locals=None):
    """A PC handler H calling reader R (this = stack local), PS4 H4 calling R4; reader codec sites per
    ``codec_rows`` (PC disp, PS4 disp, width)."""
    facts = Facts(pc={H: pcf(H), R: pcf(R, accesses)}, ps4={}, table_callbacks=set(), table_group={H: 1})
    pc, ps4 = wave2.SideArgs(), wave2.SideArgs()
    rows = []
    for i, (x, y, w) in enumerate(codec_rows):
        pc.add(wave2.Site(0x110 + i, R, CODEC, {"0": obj("0", 0, "stack", 1), "1": obj("1", x)}, 8))
        ps4.add(wave2.Site(0x910 + i, R4, CODEC4, {"rdi": obj("rdi", 0, "rsi", 1), "rsi": obj("rsi", y, "rdi", 0)}))
        rows.append(wave2.CallsiteRow(0x110 + i, R, w, "nPacket::Read_u32", "agree", ((0x910 + i, R4),)))
    pc.add(wave2.Site(0x60, H, R, handler_args or {"ecx": stack("ecx", -0x40, 0x5c)}, 4))
    ps4.add(wave2.Site(0x860, H4, R4, ps4_handler_args or {"rdi": stack("rdi", -0x60, 0x85c)}))
    fns = {R4: Ps4Fn(R4, f"{CLS}::ReadPacket", "_Z", READER_PARAMS, "void"),
           H4: Ps4Fn(H4, "cSeedGameSvConnection::OnPacket_S2C_X_RES", "_Z", HANDLER_PARAMS, "void")}
    locs = dw_locals if dw_locals is not None else (wave2.DwLocal("packet", CLS, 77, ()),)
    dw = {H4: wave2.DwFn(H4, tuple(locs), frozenset()), R4: wave2.DwFn(R4, (), frozenset())}
    inp = wave2.Wave2Inputs(facts, pc, ps4, fns, dw, TYPES, {}, set(),
                            {H: "cSeedGameSvConnection::OnPacket_S2C_X_RES"} if strings else {}, {1: ["S2C"]})
    pairs = {(H, H4): "seed", (R, R4): "reader"}
    return inp, pairs, rows


def build(inp, pairs, rows):
    return wave2_run.build(inp, pairs, rows)


# --- member links and partial layouts ------------------------------------------------------------------

def test_codec_link_gives_partial_type_with_lower_bound_size_and_comment():
    res = build(*world(((0x18, 16, "4"), (0x1c, 20, "1"))))
    assert [(lk.pc_off, lk.member, lk.width) for lk in res.links] == [(0x18, "m_a", 4), (0x1c, "m_b", 1)]
    p = res.partial[CLS]
    assert p.status == "accepted" and [(m.offset, m.size, m.name) for m in p.members] == [(0x18, 4, "m_a"),
                                                                                        (0x1c, 1, "m_b")]
    assert p.size == 0x1d and not p.size_proved
    assert p.comment.startswith("Partial: 2 members linked by codec position") and "size: lower bound" in p.comment


def test_width_mismatch_refuses_the_class():
    res = build(*world(((0x18, 16, "2"),)))  # a u16 codec into the u32 m_a
    assert res.partial[CLS].status == "refused" and "width 2, member 4" in res.partial[CLS].reason


def test_two_members_at_one_offset_refuse_the_class():
    res = build(*world(((0x18, 16, "4"), (0x18, 24, "4"))))
    p = res.partial[CLS]
    assert p.status == "refused" and "m_a / m_c" in p.reason


def test_one_member_at_two_offsets_and_overlap_refuse():
    assert build(*world(((0x18, 16, "4"), (0x20, 16, "4")))).partial[CLS].status == "refused"
    res = build(*world(((0x18, 16, "4"), (0x1a, 20, "1"))))  # m_b linked inside m_a's bytes
    assert res.partial[CLS].status == "refused" and "overlaps" in res.partial[CLS].reason


def test_access_straddling_a_linked_member_refuses_and_gap_accesses_are_counted():
    gap = Access(0x120, "ecx", 0, 0x10, 4, "store")
    ok = build(*world(accesses=[gap, Access(0x121, "ecx", 0, 0x18, 4, "load")])).partial[CLS]
    assert ok.status == "accepted" and ok.gap_accesses == 1 and ok.width_checked == 1
    bad = build(*world(accesses=[Access(0x122, "ecx", 0, 0x1a, 4, "load")])).partial[CLS]
    assert bad.status == "refused" and "0x122" in bad.reason


def test_shift_only_class_gets_no_type():
    """Accesses alone (no codec or anchor link) never make members: no row at all."""
    res = build(*world(codec_rows=(), accesses=[Access(0x121, "ecx", 0, 0x18, 4, "load")]))
    assert res.links == [] and CLS not in res.partial


def test_packet_class_needs_a_pc_handler_string_witness():
    inp, pairs, rows = world()
    res = build(replace(inp, pc_strings={}), pairs, rows)
    assert res.links == [] and any("no PC handler string" in n.why for n in res.nolinks)
    res = build(replace(inp, pc_strings={}, witness_gate=False), pairs, rows)
    assert len(res.links) == 1


def test_owners_not_an_accepted_pair_give_no_link():
    inp, pairs, rows = world()
    res = build(inp, {(H, H4): "seed"}, rows)
    assert res.links == [] and {n.why for n in res.nolinks} == {"owners not an accepted pair"}


def test_shuffled_reader_control_vanishes():
    inp, pairs, rows = world()
    other = 0x990
    inp.ps4fn[other] = Ps4Fn(other, "nUserSession::CPacket_S2C_Y_RES::ReadPacket", "_Z",
                             [{"name": "this", "type": "nUserSession::CPacket_S2C_Y_RES*", "artificial": True}],
                             "void")
    pairs2 = {**pairs, (0x200, other): "reader"}
    inp.facts.pc[0x200] = pcf(0x200)
    sh = wave2_run.shuffled_readers(pairs2, 1)
    assert sh[(R, other)] == "reader" and (R, R4) not in sh
    res = build(inp, sh, wave2_run.shuffled_rows(inp, rows, pairs2, sh))
    assert res.links == [] and not [r for r in res.locals if r.status == "accepted"]


# --- locals ----------------------------------------------------------------------------------------------

def test_r3_names_and_retypes_the_packet_local():
    res = build(*world())
    (r,) = [x for x in res.locals if x.rule == "R3"]
    assert (r.status, r.name, r.pc_frame, r.retype, r.size, r.pc_def) == ("accepted", "packet", -0x40, CLS, 0x1c,
                                                                           0x5c)


def test_r3_without_a_partial_type_is_refused():
    res = build(*world(codec_rows=()))
    (r,) = [x for x in res.locals if x.rule == "R3"]
    assert r.status == "refused" and "size unverifiable" in r.why


def test_r3_with_two_stack_objects_passed_is_refused():
    res = build(*world(handler_args={"ecx": stack("ecx", -0x40), "0": stack("0", -0x80)}))
    (r,) = [x for x in res.locals if x.rule == "R3"]
    assert r.status == "refused" and "two stack objects" in r.why
    res = build(*world(ps4_handler_args={"rdi": stack("rdi", -0x60), "rsi": stack("rsi", -0x90)}))
    (r,) = [x for x in res.locals if x.rule == "R3"]
    assert r.status == "refused" and "two stack objects" in r.why


def test_r3_refuses_argument_slot_and_two_dwarf_locals_of_the_class():
    res = build(*world(handler_args={"ecx": stack("ecx", 8)}))
    assert [x.why for x in res.locals if x.rule == "R3"] == ["PC stack address is an incoming argument slot"]
    two = (wave2.DwLocal("packet", CLS, 1, ()), wave2.DwLocal("packet2", CLS, 2, ()))
    res = build(*world(dw_locals=two))
    assert [x.why for x in res.locals if x.rule == "R3"] == [f"2 DWARF locals of class {CLS}"]


def test_r3_inlined_reader_uses_the_inline_record():
    inp, pairs, rows = world()
    inp.ps4_args.by_owner[H4] = []
    inp.dwfn[H4] = replace(inp.dwfn[H4], inlined=frozenset({f"{CLS}::ReadPacket"}))
    (r,) = [x for x in build(inp, pairs, rows).locals if x.rule == "R3"]
    assert r.status == "accepted" and r.ps4_call == 0 and "inlined" in r.ps4_bind
    inp.dwfn[H4] = replace(inp.dwfn[H4], inlined=frozenset())
    (r,) = [x for x in build(inp, pairs, rows).locals if x.rule == "R3"]
    assert r.status == "refused" and "neither calls nor inlines" in r.why


def test_r2_binds_by_breg_at_the_call_and_checks_width():
    nret = wave2.DwLocal("nRet", "u32", 5, ((0x900, 0x920, "DW_OP_breg4 0"),))
    inp, pairs, rows = world(dw_locals=())
    inp.dwfn[R4] = wave2.DwFn(R4, (nret,), frozenset())
    inp.pc_args.sites[0x110] = replace(inp.pc_args.sites[0x110], args={"1": stack("1", -8)})
    inp.ps4_args.sites[0x910] = replace(inp.ps4_args.sites[0x910], args={"rsi": stack("rsi", -0x10)})
    r = lmod.r2_rows(inp, Layouts(TYPES), set(pairs), rows)
    assert [(x.status, x.name, x.size, x.pc_frame) for x in r] == [("accepted", "nRet", 4, -8)]
    # no stack values on PC (arg_bytes 0): counted, refused
    inp.pc_args.sites[0x110] = replace(inp.pc_args.sites[0x110], args={}, arg_bytes=0)
    r = lmod.r2_rows(inp, Layouts(TYPES), set(pairs), rows)
    assert r[0].status == "refused" and "arg_bytes 0" in r[0].why


def row(**kw):
    base = dict(pc_va=0x10, ps4_va=0x90, rule="R1", pc_call=0x11, ps4_call=0x91, callee=0x20, slot="0", name="v",
                dwarf_type="u32", dwarf_die=1, ps4_bind="-", pc_frame=-8, pc_def=None, size=4, retype="-",
                status="accepted", why="")
    base.update(kw)
    return lmod.LocalRow(**base)


def test_gate_refuses_conflicts_duplicates_and_locals_inside_a_retyped_object():
    out = lmod.gate([row(name="a"), row(name="b", pc_call=0x12)])
    assert {r.status for r in out} == {"refused"} and "conflict" in out[0].why
    out = lmod.gate([row(name="a"), row(name="a", pc_frame=-16)])
    assert {r.status for r in out} == {"refused"} and "duplicate" in out[0].why
    out = lmod.gate([row(name="a"), row(name="a", pc_call=0x12)])
    assert [r.status for r in out] == ["accepted", "duplicate"]
    out = lmod.gate([row(name="packet", pc_frame=-0x40, size=0x20, retype=CLS, rule="R3"),
                     row(name="x", pc_frame=-0x38)])
    assert {r.status for r in out} == {"refused"}


# --- apply: locals and forward declarations ----------------------------------------------------------------

HEAD = (f"# 007 T013c transfer wave 2, PC 03040008 <- PS4 02020005; 1 accepted pairs; inputs: pc-ida.jsonl source "
        f"{at.PC_SHA256}")
TYPES_H = f"""// {HEAD.lstrip('# ')}
#pragma pack(push, 1)
// {CLS}: Partial: 1 members linked by codec position (PS4 02020005 names); gaps are unknown Season 3 fields.
struct {CLS} // PC size 0x1c
{{
  unsigned __int8 gap0[24];
  unsigned int m_a; // +0x18 4 PS4 m_a
}};
#pragma pack(pop)
"""
LOCAL_COLS = ["pc_va", "ps4_va", "rule", "pc_call", "ps4_call", "callee", "slot", "name", "dwarf_type", "dwarf_die",
              "ps4_bind", "pc_frame", "pc_def", "size", "retype", "holdout_lost_in_rng", "status", "why"]


def wave2_dir(d: Path, locals_rows) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    (d / "types.h").write_text(TYPES_H.replace(f"// {HEAD.lstrip('# ')}", f"// {HEAD.lstrip('# ')}"),
                               encoding="utf-8")
    with (d / "types.tsv").open("w", encoding="utf-8", newline="") as fh:
        fh.write(HEAD + "\ntype\tkind\tstatus\tpc_size\n" + f"{CLS}\tstruct\tpartial\t0x1c\n")
    with (d / "locals.tsv").open("w", encoding="utf-8", newline="") as fh:
        fh.write(HEAD + "\n" + "\t".join(LOCAL_COLS) + "\n")
        for r in locals_rows:
            fh.write("\t".join(str(r.get(c, "-")) for c in LOCAL_COLS) + "\n")
    return d


def local(**kw):
    base = {"pc_va": "0x7d0d30", "ps4_va": "0x336950", "rule": "R3", "name": "packet", "pc_frame": "-72",
            "pc_def": "0x7d0d43", "size": "28", "retype": CLS, "status": "accepted"}
    base.update(kw)
    return base


class LvarIda:
    """The adapter's types and locals calls, in memory."""

    def __init__(self, lvars=None):
        self.ltypes = {CLS: {"forward": True}}  # wave 1 wrote the forward declaration
        self.lvars = lvars or {}
        self.writes = []

    def input_sha256(self):
        return at.PC_SHA256

    def idb_path(self):
        return "D:/x/ddon-data-007smoke/a.i64"

    def counts(self):
        return {"names": 0, "typed_functions": 0, "local_types": len(self.ltypes)}

    def local_type(self, name):
        t = self.ltypes.get(name)
        return None if t is None else dict(t, blob=dict(t))

    def declare_forward(self, name):
        self.ltypes[name] = {"forward": True}

    def define_struct(self, d):
        self.writes.append(("define", d.name))
        self.ltypes[d.name] = {"forward": False, "size": d.size, "members": d.row_members()}

    def set_type_comment(self, name, cmt):
        self.writes.append(("cmt", name, cmt))

    def find_lvar(self, ea, frame, def_ea):
        m = self.lvars.get((ea, frame))
        return {"ida_off": 100 + frame, "lea_off": 100 + frame, "matches": [dict(m)] if m else []}

    def set_lvar(self, ea, m, name, type_name):
        self.writes.append(("lvar", ea, name, type_name))
        k = next(k for k, v in self.lvars.items() if v["stkoff"] == m["stkoff"])
        self.lvars[k] = dict(self.lvars[k], name=name, type=type_name or self.lvars[k]["type"], user_name=True)

    def restore_local_type(self, name, before):
        self.ltypes[name] = dict(before["blob"])
        return True

    def unset_lvar(self, ea, before):
        k = next(k for k, v in self.lvars.items() if v["stkoff"] == before["stkoff"])
        self.lvars[k] = dict(before)
        return True


def lvar(**kw):
    base = {"name": "v5", "type": "_BYTE[16]", "width": 16, "is_arg": False, "user_name": False, "user_type": False,
            "stkoff": 40, "defea": 0x7d0d43, "ida_off": 28}
    base.update(kw)
    return base


def apply_run(ida, d: Path, mode="apply", **kw):
    out = d / f"{mode}.jsonl"
    at.main(str(d), str(out), mode, ida=ida, **kw)
    return [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]


def by_step(recs, step):
    return {r["key"]: r for r in recs if r.get("kind") == "result" and r["step"] == step}


def test_forward_declaration_is_filled_in_and_local_retyped(tmp_path):
    ida = LvarIda({(0x7d0d30, -72): lvar()})
    recs = apply_run(ida, wave2_dir(tmp_path / "m", [local()]))
    assert by_step(recs, "types")[CLS]["status"] == "defined"
    assert ida.ltypes[CLS]["size"] == 0x1c and ("cmt", CLS, at.parse_types_h(TYPES_H)[0].comment) in ida.writes
    r = by_step(recs, "locals")["0x7d0d30@-72"]
    assert r["status"] == "set" and ida.lvars[(0x7d0d30, -72)]["name"] == "packet"
    undo = [x for x in recs if x.get("kind") == "undo" and x["step"] == "locals"]
    assert undo and undo[0]["before"]["name"] == "v5"
    again = apply_run(ida, tmp_path / "m")
    assert by_step(again, "locals")["0x7d0d30@-72"]["status"] == "already"


def test_dry_run_plans_a_retype_to_a_type_it_would_define(tmp_path):
    ida = LvarIda({(0x7d0d30, -72): lvar()})
    recs = apply_run(ida, wave2_dir(tmp_path / "m", [local()]), "dry-run")
    assert by_step(recs, "locals")["0x7d0d30@-72"]["status"] == "would-set" and ida.writes == []


def test_local_with_a_user_name_or_wrong_width_is_refused(tmp_path):
    ida = LvarIda({(0x7d0d30, -72): lvar(user_name=True, name="mine")})
    recs = apply_run(ida, wave2_dir(tmp_path / "m", [local()]))
    assert by_step(recs, "locals")["0x7d0d30@-72"]["check"] == "user-name"
    assert ida.lvars[(0x7d0d30, -72)]["name"] == "mine"
    ida = LvarIda({(0x87caa0, -20): lvar(width=4, stkoff=8)})
    recs = apply_run(ida, wave2_dir(tmp_path / "n", [local(pc_va="0x87caa0", pc_frame="-20", size="20", retype="-",
                                                           name="sendFeedbackList", rule="R1")]))
    assert by_step(recs, "locals")["0x87caa0@-20"]["check"] == "width"


def test_local_lvar_lookup_fails_closed(tmp_path):
    d = wave2_dir(tmp_path / "m", [local()])
    assert by_step(apply_run(LvarIda(), d), "locals")["0x7d0d30@-72"]["check"] == "lvar-not-unique"
    ida = LvarIda({(0x7d0d30, -72): lvar(is_arg=True)})
    assert by_step(apply_run(ida, d), "locals")["0x7d0d30@-72"]["check"] == "argument"
    found = {"ida_off": 28, "lea_off": 32, "matches": [lvar()]}
    assert at.plan_local(local(), found, 28) == ("refused", {"check": "frame-mismatch", "ida_off": 28,
                                                             "lea_off": 32})
    assert at.plan_local(local(), {"ida_off": 28, "lea_off": None, "matches": [lvar()]}, 24)[1]["check"] == \
        "type-size"


def test_undo_restores_the_local(tmp_path):
    ida = LvarIda({(0x7d0d30, -72): lvar()})
    d = wave2_dir(tmp_path / "m", [local()])
    apply_run(ida, d)
    recs = apply_run(ida, d, "undo", apply_log=str(d / "apply.jsonl"))
    assert by_step(recs, "locals")["0x7d0d30@-72"]["status"] == "restored"
    assert ida.lvars[(0x7d0d30, -72)]["name"] == "v5"


def test_filter_selects_retyped_types_first_and_their_locals(tmp_path):
    d = wave2_dir(tmp_path / "m", [local(), local(pc_va="0x1", retype="-", name="x", pc_frame="-8")])
    m = at.load_manifest(str(d))
    decls, loc = at.select(m, at.parse_types_h(m["types_h"]), 1, 1)
    assert [x.name for x in decls] == [CLS] and len(loc) == 1
    assert at.parse_types_h(at.render_decls(decls))[0].comment == decls[0].comment
    decls, loc = at.select(m, at.parse_types_h(m["types_h"]), 0, 5)
    assert decls == [] and [r["name"] for r in loc] == ["x"]


def test_smoke_copy_mark_accepted_other_paths_refused():
    ida = LvarIda()
    assert at.precheck(ida)["idb_path"].endswith("a.i64")
    ida.idb_path = lambda: "D:/x/ddon-data-other/a.i64"
    with pytest.raises(ValueError):
        at.precheck(ida)


@pytest.mark.skipif(not (HERE / "manifest/transfer/wave2/locals.tsv").exists(), reason="wave 2 not run")
def test_real_wave2_manifest_loads_and_parses():
    m = at.load_manifest(str(HERE / "manifest/transfer/wave2"))
    decls = at.parse_types_h(m["types_h"])
    partial = [d for d in decls if m["types"].get(d.name, {}).get("status") == "partial"]
    assert partial and all(d.comment and d.comment.startswith("Partial: ") for d in partial)
    assert all(r["retype"] == "-" or r["retype"] in {d.name for d in partial} for r in m["locals"])


def test_log_is_jsonl():
    fh = io.StringIO()
    at.Log(fh).write({"kind": "x"})
    assert json.loads(fh.getvalue()) == {"kind": "x"}

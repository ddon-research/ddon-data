"""Wave 2 pipeline and writer: links, partial types, locals, precision (holdout) and the reader-shuffle control.

Outputs (``manifest/transfer/wave2/``): ``links.tsv`` (member links and the codec/anchor sites that give none,
with the reason), ``types.tsv`` + ``type_members.tsv`` + ``types.h`` (the accepted partial types; the wave-1
types they embed are repeated verbatim from wave 1's ``types.h`` so the apply checks them ``already``),
``locals.tsv``, ``precision.tsv``, ``control.tsv``, ``summary.tsv``.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field, replace
from pathlib import Path

from matcher import checks
from matcher import tier0 as t0mod

from . import locals as lmod
from . import wave2
from .layout import Layouts, Member
from .render import _decl
from .run import _write
from .typecheck import KNOWN_SIZES

Pair = tuple[int, int]
CODEC_READ = re.compile(r"nPacket::Read_(?:u8|s8|u16|s16|u32|s32|u64|s64|f32|f64|bool|MtString|bytes|cstr)")


@dataclass
class W2Result:
    links: list[wave2.Link]
    nolinks: list[wave2.NoLink]
    partial: dict[str, wave2.Partial]
    locals: list[lmod.LocalRow]
    precision: list[list] = field(default_factory=list)
    control: list[list] = field(default_factory=list)
    lost: dict[str, list[int]] = field(default_factory=dict)  # "type X" / "local ..." -> rng seeds


def build(inp: wave2.Wave2Inputs, pairs: dict[Pair, str], rows: list[wave2.CallsiteRow]) -> W2Result:
    layouts = Layouts(inp.types)
    ps = set(pairs)
    cl, cno = wave2.codec_links(inp, layouts, ps, rows)
    al, ano = wave2.anchor_links(inp, layouts, ps)
    links = cl + al
    sizes = {k: v for k, v in KNOWN_SIZES.items()}
    partial = wave2.partial_layouts(inp, layouts, links, sizes, wave2.class_params(inp, layouts, ps))
    loc = lmod.locals_rows(inp, layouts, pairs, rows, partial)
    return W2Result(links, cno + ano, partial, loc)


def accepted_types(res: W2Result) -> dict[str, tuple]:
    return {c: (p.size, tuple((m.offset, m.size, m.path) for m in p.members))
            for c, p in res.partial.items() if p.status == "accepted"}


def accepted_links(res: W2Result) -> dict[tuple[str, int], str]:
    return {(lk.cls, lk.pc_off): lk.member for lk in res.links}


def accepted_locals(res: W2Result) -> dict[tuple[int, int], str]:
    return {(r.pc_va, r.pc_frame): r.name for r in res.locals if r.status == "accepted"}


def _diff(full: dict, part: dict) -> tuple[int, int, int]:
    """(lost, contradicting, new) of a holdout or control run against the full run."""
    lost = sum(1 for k in full if k not in part)
    bad = sum(1 for k, v in part.items() if k in full and full[k] != v)
    new = sum(1 for k in part if k not in full)
    return lost, bad, new


def holdout(inp: wave2.Wave2Inputs, t0: dict[int, str], res: W2Result) -> None:
    """T005e's holdout (5 RNG seeds x 20% of the seeds withheld): the matcher pipeline and wave 2 rerun on its
    pairs and call sites; every full-run link, type and local must be absent or the same."""
    facts = inp.facts
    seeds, _ = t0mod.seed_candidates(facts, t0)
    prefixes = t0mod.group_prefixes(t0, facts)
    fl, ft, fo = accepted_links(res), accepted_types(res), accepted_locals(res)
    for rng in checks.RNG_SEEDS:
        withheld = checks.holdout(seeds, rng)
        part = checks.pipeline(facts, {k: v for k, v in seeds.items() if k not in withheld}, t0, prefixes)
        pr = build(inp, part.pairs(), wave2.callsite_rows(part.roles.callsites))
        pl, pt, po = accepted_links(pr), accepted_types(pr), accepted_locals(pr)
        for t in sorted(set(ft) - set(pt)):
            res.lost.setdefault(f"type {t}", []).append(rng)
        for k in sorted(set(fo) - set(po)):
            res.lost.setdefault(f"local {k[0]:#x} {k[1]}", []).append(rng)
        res.precision.append([rng, len(withheld), len(part.pairs()), len(fl), *_diff(fl, pl), len(ft), *_diff(ft, pt),
                              len(fo), *_diff(fo, po)])


def shuffled_readers(pairs: dict[Pair, str], rng: int) -> dict[Pair, str]:
    """The reader pairs with their PS4 side deranged (fixed RNG seed); every other pair unchanged."""
    readers = {pc: ps4 for (pc, ps4), r in pairs.items() if r == "reader"}
    der = checks.derangement(readers, rng)
    out = {p: r for p, r in pairs.items() if r != "reader"}
    out.update({(pc, ps4): "reader" for pc, ps4 in der.items()})
    return out


def shuffled_rows(inp: wave2.Wave2Inputs, rows: list[wave2.CallsiteRow], pairs: dict[Pair, str],
                  shuffled: dict[Pair, str]) -> list[wave2.CallsiteRow]:
    """Rule-3 rows of the reader pairs re-aligned by position against the deranged PS4 reader: the k-th PC codec
    site of the reader with the k-th PS4 ``nPacket::Read_*`` call of its new partner."""
    real = {pc: ps4 for (pc, ps4), r in pairs.items() if r == "reader"}
    fake = {pc: ps4 for (pc, ps4), r in shuffled.items() if r == "reader"}
    out = [r for r in rows if r.pc_function not in real or all(o != real[r.pc_function] for _, o in r.ps4)]
    for pc, ps4 in sorted(fake.items()):
        mine = sorted((r for r in rows if r.pc_function == pc and any(o == real[pc] for _, o in r.ps4)),
                      key=lambda r: r.pc_site)
        codec = sorted(s.site for s in inp.ps4_args.by_owner.get(ps4, [])
                       if s.target is not None and s.target in inp.facts.ps4
                       and CODEC_READ.fullmatch(inp.facts.ps4[s.target].name))
        for r, site in zip(mine, codec, strict=False):
            out.append(wave2.CallsiteRow(r.pc_site, pc, r.width, r.ps4_overload, r.status, ((site, ps4),)))
    return out


def control(inp: wave2.Wave2Inputs, pairs: dict[Pair, str], rows: list[wave2.CallsiteRow], res: W2Result) -> None:
    """The reader pairs' PS4 side deranged (5 RNG seeds): links on the shuffled reader classes, their types and the
    R3 locals must conflict or vanish. Run with the PC string witness (the rule as written) and without it."""
    fl, ft = accepted_links(res), accepted_types(res)
    f3 = {(r.pc_va, r.pc_frame): r.name for r in res.locals if r.status == "accepted" and r.rule == "R3"}
    for rng in checks.RNG_SEEDS:
        sh = shuffled_readers(pairs, rng)
        srows = shuffled_rows(inp, rows, pairs, sh)
        for gated in (True, False):
            cr = build(replace(inp, witness_gate=gated), sh, srows)
            readers = {p for p, r in sh.items() if r == "reader"}
            rl = [lk for lk in cr.links if (lk.pc_owner, lk.ps4_owner) in readers]
            cls = {lk.cls for lk in rl}
            ct = accepted_types(cr)
            c3 = {(r.pc_va, r.pc_frame): r.name for r in cr.locals if r.status == "accepted" and r.rule == "R3"}
            res.control.append([rng, "with witness" if gated else "without witness", len(readers), len(rl),
                                sum(1 for lk in rl if fl.get((lk.cls, lk.pc_off)) == lk.member), len(cls),
                                sum(1 for c in cls if cr.partial[c].status == "refused"),
                                sum(1 for c in cls if c in ct), sum(1 for c in cls if c in ct and ft.get(c) == ct[c]),
                                len(c3), sum(1 for k, v in c3.items() if f3.get(k) == v)])


# --- types.h ----------------------------------------------------------------------------------------

_BLOCK = re.compile(r"^(?:struct|union) (?P<name>[^\n]+?) // PC size 0x[0-9a-fA-F]+\n\{\n.*?^\};\n", re.M | re.S)


def wave1_blocks(text: str) -> dict[str, str]:
    return {m["name"]: m.group(0) for m in _BLOCK.finditer(text)}


def _deps(block: str, names: set[str]) -> list[str]:
    out = []
    for line in block.splitlines()[2:-1]:
        m = re.match(r"\s*(?P<type>[^*;]+?)\s+\w+(?:\[\d+\])?;", line)
        if m and m["type"].strip() in names:
            out.append(m["type"].strip())
    return out


def render(res: W2Result, inp: wave2.Wave2Inputs, layouts: Layouts, wave1_h: str, title: str
           ) -> tuple[str, list[list]]:
    blocks = wave1_blocks(wave1_h)
    emitted = set(inp.wave1)
    bodies: list[str] = []
    rows: list[list] = []
    need: list[str] = []
    for cls in sorted(c for c, p in res.partial.items() if p.status == "accepted"):
        p = res.partial[cls]
        lines = [f"// {cls}: {p.comment}", f"struct {cls} // PC size {p.size:#x}", "{"]
        pos = 0
        for m in p.members:
            if m.offset > pos:
                lines.append(f"  unsigned __int8 gap{pos:X}[{m.offset - pos}];")
            info = layouts.resolve(m.dwarf_type)
            lm = Member(m.name, m.offset, m.size, "struct" if info.kind == "struct" else info.kind, m.dwarf_type, info)
            d, note = _decl(lm, emitted, set(), layouts, set(), set())
            if info.kind == "struct" and info.name in blocks:
                need.append(info.name)
            lines.append(f"  {d}; // +{m.offset:#x} {m.size}" + (f" {note}" if note else "") + f" PS4 {m.path}")
            rows.append([cls, f"{m.offset:#x}", m.size, m.path, d, m.dwarf_type, m.links])
            pos = m.offset + m.size
        if pos < p.size:
            lines.append(f"  unsigned __int8 gap{pos:X}[{p.size - pos}];")
        lines.append("};")
        bodies.append("\n".join(lines) + "\n")
    done: list[str] = []

    def visit(n: str) -> None:
        if n in done or n not in blocks:
            return
        for d in _deps(blocks[n], set(blocks)):
            visit(d)
        done.append(n)

    for n in sorted(set(need)):
        visit(n)
    parts = [f"// {title}", "// Generated by transfer.py --wave2; partial PC 03040008 layouts from member links "
             "(PS4 02020005 names); wave-1 types repeated as written.", "", "#pragma pack(push, 1)"]
    parts += [f"// wave-1 type, unchanged\n{blocks[n]}" for n in done]
    parts += bodies
    parts.append("#pragma pack(pop)")
    return "\n".join(parts) + "\n", rows


# --- writer ---------------------------------------------------------------------------------------------

def write_all(out: Path, res: W2Result, inp: wave2.Wave2Inputs, wave1_h: str, head: str) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    layouts = Layouts(inp.types)
    counts: dict[str, int] = {}
    lrows = [[lk.cls, f"{lk.pc_off:#x}", lk.width, lk.member, lk.dwarf_type, f"{lk.ps4_off:#x}", lk.kind,
              f"{lk.pc_site:#x}", f"{lk.ps4_site:#x}", f"{lk.pc_owner:#x}", f"{lk.ps4_owner:#x}", "link"]
             for lk in sorted(res.links, key=lambda x: (x.cls, x.pc_off, x.pc_site, x.ps4_site))]
    lrows += [["-", "-", "-", "-", "-", "-", "-", f"{n.pc_site:#x}", f"{n.ps4_site:#x}", "-", "-", n.why]
              for n in sorted(res.nolinks, key=lambda x: (x.pc_site, x.ps4_site, x.why))]
    counts["links.tsv"] = _write(out / "links.tsv", head, ["class", "pc_offset", "width", "ps4_member", "dwarf_type",
                                                           "ps4_offset", "kind", "pc_site", "ps4_site", "pc_owner",
                                                           "ps4_owner", "outcome"], lrows)
    text, mrows = render(res, inp, layouts, wave1_h, head.lstrip("# "))
    (out / "types.h").write_text(text, encoding="utf-8", newline="\n")
    trows = []
    for cls, p in sorted(res.partial.items()):
        status = {"accepted": "partial", "refused": "refused", "wave-1": "wave-1"}[p.status]
        trows.append([cls, "struct", status, f"{p.size:#x}" if p.status != "wave-1" else "-",
                      "proved" if p.size_proved else "lower bound", len(p.members),
                      sum(1 for lk in res.links if lk.cls == cls), p.width_checked, p.gap_accesses,
                      p.indexed_unplaced, len(p.functions),
                      " ".join(f"{x:#x}" for x in sorted(p.evidence)[:10]) or "-",
                      " ".join(str(s) for s in res.lost.get(f"type {cls}", [])) or "-",
                      p.reason, p.comment if p.status == "accepted" else "-"])
    counts["types.tsv"] = _write(out / "types.tsv", head, ["type", "kind", "status", "pc_size", "size_kind",
                                                           "members", "links", "width_checked", "gap_accesses",
                                                           "indexed_unplaced", "functions", "evidence_vas",
                                                           "holdout_lost_in_rng", "basis", "comment"], trows)
    counts["type_members.tsv"] = _write(out / "type_members.tsv", head, ["type", "offset", "size", "ps4_member",
                                                                         "decl", "dwarf_type", "links"], mrows)
    orows = [[f"{r.pc_va:#x}", f"{r.ps4_va:#x}", r.rule, f"{r.pc_call:#x}", f"{r.ps4_call:#x}" if r.ps4_call else "-",
              f"{r.callee:#x}", r.slot, r.name, r.dwarf_type, r.dwarf_die, r.ps4_bind, r.pc_frame,
              f"{r.pc_def:#x}" if r.pc_def is not None else "-", r.size if r.size is not None else "-", r.retype,
              " ".join(str(s) for s in res.lost.get(f"local {r.pc_va:#x} {r.pc_frame}", [])) or "-",
              r.status, r.why or "-"] for r in res.locals]
    counts["locals.tsv"] = _write(out / "locals.tsv", head, ["pc_va", "ps4_va", "rule", "pc_call", "ps4_call",
                                                             "callee", "slot", "name", "dwarf_type", "dwarf_die",
                                                             "ps4_bind", "pc_frame", "pc_def", "size", "retype",
                                                             "holdout_lost_in_rng", "status", "why"], orows)
    counts["precision.tsv"] = _write(out / "precision.tsv", head, [
        "rng_seed", "withheld_seeds", "pairs", "links_full", "links_lost", "links_contradict", "links_new",
        "types_full", "types_lost", "types_contradict", "types_new", "locals_full", "locals_lost",
        "locals_contradict", "locals_new"], res.precision)
    counts["control.tsv"] = _write(out / "control.tsv", head, [
        "rng_seed", "variant", "reader_pairs_shuffled", "reader_class_links", "links_equal_to_real", "reader_classes",
        "classes_conflicted", "classes_accepted", "accepted_equal_to_real", "r3_locals", "r3_equal_to_real"],
        res.control)
    summ = summary(res)
    _write(out / "summary.tsv", head, ["key", "value"], [[k, v] for k, v in summ.items()])
    counts.update({f"summary {k}": v for k, v in summ.items()})
    return counts


def summary(res: W2Result) -> dict[str, int]:
    out: dict[str, int] = {}
    for k, v in sorted(Counter(lk.kind for lk in res.links).items()):
        out[f"links {k}"] = v
    out["link classes"] = len({lk.cls for lk in res.links})
    for k, v in sorted(Counter(n.why.split(" (")[0] for n in res.nolinks).items()):
        out[f"no link: {k}"] = v
    for k, v in sorted(Counter(p.status for p in res.partial.values()).items()):
        out[f"types {k}"] = v
    out["types partial with proved size"] = sum(1 for p in res.partial.values()
                                                if p.status == "accepted" and p.size_proved)
    for k, v in sorted(Counter((r.rule, r.status) for r in res.locals).items()):
        out[f"locals {k[0]} {k[1]}"] = v
    for k, v in sorted(Counter((r.rule, r.why.split(" (")[0].split(":")[0]) for r in res.locals
                               if r.status == "refused").items()):
        out[f"locals {k[0]} refused: {k[1]}"] = v
    out["holdout items lost (any rng)"] = len(res.lost)
    return out


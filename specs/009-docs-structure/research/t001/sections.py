"""009 T001: write T001-sections.tsv: one row per heading of every living doc, classified by hand below.

Every heading must have a row in M and every row in M must be a heading (asserts), and the line ranges of each
file must sum to its line count. Extra `[sub]` rows split research/03040008/packets/README.md, whose sections hold
several purposes under bold pseudo-headings.

usage (from D:/ddon-data): python -X utf8 -I specs/009-docs-structure/research/t001/sections.py
"""
import collections
import pathlib
import re

TAB = "\t"
NL = "\n"
T, HT, RF, EX, HI, ST = "tutorial", "how-to", "reference", "explanation", "history", "status"


def h(n):
    return "docs/how-to/" + n + ".md"


def r(n):
    return "docs/reference/" + n + ".md"


def e(n):
    return "docs/explanation/" + n + ".md"


KEEP = "keep"
SH = "spec-history"
M = {}
M["readme.adoc"] = {
    1: (EX, KEEP, "short root readme: what this is"),
    11: (EX, KEEP, "shorten; season repos and purpose stay"),
    31: (RF, r("repository-layout"), "root keeps a brief layout; drop the plan/ row (absent at top level)"),
    100: (EX, e("evidence-model"), "data-flow diagram; root keeps a short copy; downstream list goes to " + r("repository-layout")),
    117: (RF, r("tools-and-shell"), ""),
    130: (HT, h("extract-client-resources"), "empty parent heading"),
    132: (HT, h("extract-client-resources"), "also in AGENTS.md Workflows"),
    139: (HT, h("decode-a-resource-format"), "names research/README.adoc (index name is readme.adoc)"),
    150: (HT, h("decrypt-a-capture"), "tshark heuristics, expected plaintext, 15k depth, 40 s"),
    169: (RF, KEEP, "one line pointing at AGENTS.md"),
    176: (EX, KEEP, ""),
}
M["AGENTS.md"] = {
    1: (RF, KEEP, "agent guide stays canonical for agents"),
    12: (RF, r("repository-layout"), "table and inputs move; AGENTS.md keeps a pointer plus the never-move list; plan/ row stale; line 44 reader claims to correct"),
    55: (EX, e("evidence-model"), "keep the rules in AGENTS.md as binding one-liners and link"),
    69: (RF, KEEP, "agent rules; a human summary may sit in " + r("repository-layout")),
    85: (RF, KEEP, "agent rules; pages do not repeat them; toolchain summary in " + r("tools-and-shell")),
    115: (HT, KEEP, "shorten to links: extract-client-resources, decode-a-resource-format, decrypt-a-capture, apply-a-client-patch, query-ida-read-only, regenerate-elf-dumps; facts move there; line 126 names research/README.adoc; IDA bullet does not name pc-accepted"),
    148: (RF, r("conventions"), "Libraries first and Clone rules stay in AGENTS.md; naming rows move"),
    167: (RF, KEEP, "agent process, not for peers"),
    183: (HT, KEEP, "agent process"),
    209: (RF, KEEP, "subproject gates"),
}
M["CLAUDE.md"] = {
    1: (RF, KEEP, ""),
    5: (ST, KEEP, "line 7 says no active feature (spec 009 is open); line 12 names plan/*.md, absent"),
    16: (RF, KEEP, "IDA part summarized on " + h("query-ida-read-only") + "; add pc-accepted"),
    34: (RF, KEEP, "agent traps"),
    43: (RF, KEEP, "second entry links research/03040008/ida-transfer/README.md for recipes: repoint to " + h("write-to-an-ida-database")),
}
M[".specify/memory/constitution.md"] = {
    1: (EX, KEEP, "Spec Kit governance file; " + e("evidence-model") + " cites it"),
    7: (EX, KEEP, ""), 9: (EX, KEEP, ""), 16: (EX, KEEP, ""), 24: (EX, KEEP, ""), 30: (EX, KEEP, ""), 38: (EX, KEEP, ""),
    43: (RF, KEEP, "line 47: stable paths"), 51: (HT, KEEP, ""), 58: (RF, KEEP, ""),
}
t = h("decode-a-resource-format")
c0 = h("choose-a-resource-target")
M["research/readme.adoc"] = {
    1: (HT, KEEP, "replace by a short research/README: what the tree holds; the opening line is garbled (PS4 debug symbo automation)"),
    12: (HT, t, ""),
    14: (HT, t, "Ghidra listed as required; AGENTS.md prefers IDA MCP: the page leads with IDA"),
    20: (HT, t, ""),
    26: (HT, t, ""),
    28: (HT, c0, "grep commands; bare path ddon-extractor/..."),
    49: (HT, t, "archived Ghidra route; keep as the alternative, IDA first"),
    78: (RF, t, "conversion rules: a table in the page"),
    115: (HT, t, "relative to research/ as cwd"),
    143: (HT, t, ""),
    168: (RF, t, "failure table: array limit, version mismatch, early stop"),
    188: (RF, r("repository-layout"), "names README.adoc; stale tree"),
    200: (EX, KEEP, "LLM selling points, no fact a reader acts on: propose cutting; recorded here because no spec holds it"),
    216: (RF, t, "links"),
    223: (RF, t, "command summary; duplicates the steps"),
    246: (HT, c0, ""),
    248: (HT, c0, "script writes only a temp dir it removes"),
    273: (ST, c0, "03040008 re-run 2026-11-04: 186 supported, 145 not, 56% (matches); needs a dated example; 02030004 not re-run"),
    293: (HT, c0, ""),
}
p = "research/03040008/packets/README.md"
M[p] = {
    1: (RF, KEEP, "short directory README: what, producer, links; lines 4-6 are spec history"),
    8: (RF, r("packet-pattern-format"), "parent; split in [sub] rows"),
    140: (HT, h("export-packets-to-json"), "options to " + r("imhex-export-cli")),
    171: (EX, e("evidence-model"), "also " + e("packet-decoding-method") + "; the 36 older-pattern note stays as a limit"),
    183: (RF, r("packet-ids"), "parent; split in [sub] rows"),
    846: (RF, r("packet-open-questions"), "parent; 61 bullets as [sub] rows"),
}
a = "research/03040008/ida-transfer/README.md"
M[a] = {
    1: (RF, KEEP, "short directory README: scripts, gates, links"),
    7: (HT, h("write-to-an-ida-database"), "read path to " + h("query-ida-read-only") + "; lesson kept: a killed worker's writes are lost; T004d story cut"),
    31: (HT, h("transfer-annotations-ps4-to-pc"), "flags and refusals to " + r("ida-transfer-tools")),
    69: (RF, r("ida-transfer-tools"), "versioned section: merge into the current extractor schema; version history stays in 007 tasks"),
    103: (RF, r("ida-transfer-tools"), "as above"),
    146: (RF, r("ida-transfer-tools"), "as above; the rule (op_t, never operand text) on " + e("ida-transfer-method")),
    163: (RF, r("ida-transfer-tools"), "as above; extract/ package layout"),
    194: (EX, e("ida-transfer-method"), "gates and tiers; counts to spec-history (007 tasks)"),
    223: (EX, e("ida-transfer-method"), "role anchors; run counts to spec-history (007 T005e)"),
    303: (RF, r("ida-transfer-tools"), "manifest columns; rule reasons to " + e("ida-transfer-method")),
    358: (RF, r("ida-transfer-tools"), "layout rules with test names"),
    429: (EX, e("ida-transfer-method"), "wave 2 links; commands to " + h("transfer-annotations-ps4-to-pc") + "; published database name to " + r("inputs-and-builds")),
    476: (HT, h("transfer-annotations-ps4-to-pc"), "apply, undo log, verify; run counts spec-history (007 Close)"),
}
pr = "research/03040008/protections/README.md"
M[pr] = {
    1: (RF, KEEP, "path must stay (ddon-hook AGENTS.md:57, docs 08, 09, 14, 15); short index plus a section map"),
    15: (EX, e("client-lineage-and-protections"), "ddon-hook docs 09:206 cites §1: leave a §1 pointer"),
    30: (RF, r("client-patches"), "lineage diagram; also on the explanation page"),
    45: (RF, r("protection-inventory"), "mechanism table; f1c9 addresses, PC 03040008"),
    67: (EX, e("client-lineage-and-protections"), ""),
    77: (HI, SH, "T026 story: specs/003 and ddon-hook spec 009. Lesson (delayed integrity reaction) to " + e("client-lineage-and-protections")),
    96: (HT, h("triage-a-client-crash"), "ordered steps with stop rules; step 3's layer exists untracked: patches/2026_10_17_ddo_dump_fix_4.r2"),
    124: (HT, h("triage-a-client-crash"), "ddon-hook docs 14 and run_cycles.py:614 cite §5: leave a §5 pointer"),
    153: (HI, SH, "specs/003 R3 §7; the patches/README.md corrections are already applied (rows f1c9, v7, 100FPS): cut"),
}
kr = "evidence report, stays; cited as R1 §n by the README; external-references.jsonl has 14 rows naming it"
M["research/03040008/protections/R1-online.md"] = {
    k: (HT if k == 264 else EX, KEEP, kr if k == 1 else "")
    for k in (1, 27, 33, 56, 72, 94, 108, 136, 138, 173, 186, 198, 207, 220, 222, 238, 245, 251, 264, 298, 327)
}
M["research/03040008/protections/R2-static.md"] = {
    1: (RF, KEEP, "evidence report, stays; cited as R2 §n"),
    20: (RF, KEEP, "per-exe table feeds " + r("protection-inventory")),
    74: (EX, KEEP, ""), 103: (RF, KEEP, ""), 122: (RF, KEEP, ""), 137: (RF, KEEP, ""), 170: (RF, KEEP, ""), 193: (RF, KEEP, ""),
    214: (RF, KEEP, ""), 249: (HI, KEEP, "T026 ranking"), 284: (ST, KEEP, "not-run list"), 296: (RF, KEEP, ""),
}
M["research/03040008/protections/R3-patches.md"] = {
    1: (RF, KEEP, "evidence report, stays; cited as R3 §n"),
    38: (RF, KEEP, "feeds the lineage on " + r("client-patches")),
    86: (RF, KEEP, ""), 88: (RF, KEEP, ""), 102: (RF, KEEP, ""), 112: (RF, KEEP, ""), 118: (RF, KEEP, ""), 126: (RF, KEEP, ""),
    138: (RF, KEEP, ""), 151: (RF, KEEP, ""), 158: (RF, KEEP, ""), 169: (RF, KEEP, ""), 184: (RF, KEEP, ""), 199: (RF, KEEP, ""),
    218: (RF, KEEP, ""), 252: (EX, KEEP, ""),
    268: (RF, KEEP, "feeds " + r("protection-inventory")),
    289: (HI, KEEP, "discrepancies at spec 003"), 329: (ST, KEEP, ""), 343: (RF, KEEP, ""),
}
cp = r("client-patches")
M["patches/README.md"] = {
    1: (RF, KEEP, "short README; history prose to " + e("client-lineage-and-protections")),
    10: (RF, KEEP, "manual TOC: cut"),
    22: (HT, h("apply-a-client-patch"), "radiff2 generation to " + h("add-a-client-patch-layer")),
    53: (EX, h("apply-a-client-patch"), "order and base hash rule; UTF-16 note to " + cp + "; '10 of the 12' ignores the untracked 2026_10_17 layer (other work)"),
    65: (RF, cp, "hashes"), 76: (RF, cp, ""), 78: (RF, cp, ""), 93: (RF, cp, ""), 105: (RF, cp, ""),
}
kf = "other work: census only, no move; the README stays whole"
M["research/03040008/flags/README.md"] = {
    k: (v, KEEP, kf if k == 1 else "")
    for k, v in {1: EX, 7: EX, 9: EX, 21: RF, 33: RF, 42: EX, 57: HT, 59: RF, 66: RF, 93: RF, 102: HT, 119: HT, 153: HT, 170: RF,
                 194: EX, 196: EX, 216: EX, 230: RF, 238: HT}.items()
}
M["research/03040008/flags/TODO.md"] = {1: (ST, KEEP, kf)}
el = "binaries/PS4_02020005/elf-dumps/README.adoc"
d0 = r("elf-dumps")
pe = e("ps4-elf")
M[el] = {
    1: (RF, KEEP, "reconstructor AGENTS.md:8 and docs/reference/prerequisites.md:119 read it for the dump per use: file and §7 stay"),
    12: (RF, KEEP, "input identity; " + d0 + " links here"),
    25: (HT, h("regenerate-elf-dumps"), ""),
    27: (RF, h("regenerate-elf-dumps"), "tool versions"),
    38: (HT, h("regenerate-elf-dumps"), ""),
    50: (RF, d0, "provenance fields"),
    65: (RF, d0, "committed vs local"),
    75: (RF, KEEP, "table of categories: the lookup the outside reader wants"),
    131: (EX, pe, "parent"), 133: (EX, pe, "build PS4_02020005"), 151: (EX, pe, ""), 167: (EX, pe, ""), 178: (EX, pe, ""),
    195: (EX, pe, ""), 206: (EX, pe, ""), 215: (EX, pe, ""), 221: (EX, pe, ""), 246: (EX, pe, ""), 258: (EX, pe, ""), 269: (EX, pe, ""),
    276: (EX, KEEP, "AGENTS.md:144 cites § 5: tool preferences; link from " + d0),
    288: (RF, d0, "verification results at the dump date"),
    300: (HT, KEEP, "§7 Use stays (outside reader); regeneration commands by link"),
}
pd = e("plbatch-design")
M["research/imhex/plbatch/README.md"] = {
    1: (RF, KEEP, "short README"),
    9: (EX, pd, ""),
    16: (HT, h("build-plbatch"), "pin rationale to " + pd),
    48: (RF, r("plbatch-cli"), ""),
    79: (HI, pd, "one dated measurement backs the claim; the rest stays in specs/005 P7 and 006 T001d"),
    94: (EX, pd, ""),
}
ph = h("run-pharos")
M["research/pharos/README.md"] = {
    1: (HT, KEEP, "short README"), 3: (EX, ph, ""), 7: (HT, ph, ""), 16: (HT, ph, ""),
    22: (ST, ph, "heading says to be verified: state as unmeasured"),
    32: (RF, ph, ""), 47: (HT, ph, ""), 49: (HT, ph, ""), 53: (HT, ph, ""), 59: (HT, ph, ""), 66: (HT, ph, ""), 74: (RF, ph, ""),
}
rr = e("rng-race")
M["research/rng-race/README.md"] = {
    1: (EX, KEEP, "short README; path stays (ddon-hook tools/rng reads the directory)"),
    9: (EX, rr, "dated 2026-10-17; ddon-hook specs/013 went further: reconcile before writing the page (not read here)"),
    25: (ST, SH, "resume point of 2026-10-17; ddon-hook specs 009, 010, 013 record it; deployment facts stale"),
    40: (RF, r("inputs-and-builds"), "longplay videos"),
    49: (RF, KEEP, "Files table; single_race.log and *.exe ignored locally"),
}
M["research/rng-race/NOTES.md"] = {
    k: (HI, KEEP, "lab notes: evidence, stays" if k == 1 else ("facts feed " + rr if k in (8, 51) else "")) for k in (1, 8, 19, 28, 51, 64, 71, 80)
}
M["research/rng-race/IDEAS.md"] = {k: (ST, KEEP, "idea ledger: evidence, stays" if k == 1 else "") for k in (1, 8, 19, 33, 40)}
ct = h("convert-textures")
M["research/textures/how-to-extract-images.adoc"] = {
    1: (HT, ct, "adoc attributes only"), 5: (HT, ct, ""), 9: (HT, ct, ""), 18: (HT, ct, "scripts stay in research/textures"),
}
M["research/textures/texture-research.md"] = {1: (RF, KEEP, "scratch note: grep commands and FORMAT_ lists; no heading")}
M["research/rLandInfo-example.adoc"] = {
    1: (HT, t, "worked example section or companion page; needs clients and Ghidra, so not a tutorial"),
    12: (RF, t, ""), 21: (HT, t, ""), 55: (HT, t, ""), 98: (HT, t, ""), 151: (HT, t, ""), 170: (HT, t, ""),
    198: (EX, t, "lessons"),
    213: (RF, KEEP, "tree of paths: propose cutting, no fact beyond the steps"),
}
cr = r("community-resources")
M["research/wikis-and-resources.adoc"] = {
    k: (RF, cr, "external links, not checked" if k == 1 else "")
    for k in (1, 5, 9, 20, 22, 38, 48, 57, 68, 75, 94, 107, 111, 120, 133, 140, 146, 151, 159, 161, 164, 168, 171, 176, 180, 184)
}
kv = "survey report; path stays (ddon-hook docs 11:113, 13:91; external-references.jsonl has 10 rows naming it); ddon-hook-specific"
M["research/claude-vision-tokens.md"] = {k: (EX, KEEP, kv if k == 1 else "") for k in (1, 13, 80, 173, 213, 253, 342)}
M["research/external-references.md"] = {
    1: (RF, KEEP, "path stays (ddon-hook AGENTS.md:84-85; AGENTS.md:158); docs/index.md links it"),
    17: (RF, KEEP, "report index lists 2 topics; the jsonl report values also name specs/005, ida-transfer and ddon-hook specs: extend"),
}
M["research/03040008/quest-flag-data-source-mapping.adoc"] = {
    1: (RF, r("quest-flag-sources"), "no adoc heading; rough notes on where each flag command lives in client 03040008"),
}
ad = "packets/README-decrypt-annotate-streams.adoc"
ra = h("reannotate-streams")
M[ad] = {
    1: (RF, KEEP, "title stale (Parallel CLI Runner); becomes a short packets/README with links; AGENTS.md:131 and 3 scripts point here"),
    8: (HT, ra, ""), 13: (RF, ra, ""), 22: (RF, ra, ""),
    36: (HT, ra, "names ./run-parallel-packet.sh: absent; the script is decrypt-annotate-streams.sh (dirty, not edited)"),
    49: (HT, ra, ""),
    56: (HT, h("patch-the-arrowgene-cli"), "patch table to " + r("arrowgene-cli-patches") + "; reasons (Error stop, default key, first-packet recovery, frame collisions) to " + e("wire-protocol") + "; the 13,724-raw recovery story to spec-history (006 TC3)"),
    187: (HT, ra, ""),
    201: (HT, ra, "decrypt-export-streams.sh; JSON coverage facts to " + r("packet-pattern-format")),
    248: (HT, h("export-packets-to-json"), "selection and options to " + r("imhex-export-cli")),
    317: (HT, h("refresh-packet-statistics"), "output files listed"),
}

rows = []
chk = []
for d in M:
    t_ = pathlib.Path(d).read_text(encoding="utf-8", errors="replace").split(NL)
    if t_ and t_[-1] == "":
        t_ = t_[:-1]
    adoc = d.endswith(".adoc")
    f = None
    hs = []
    rawcount = 0
    for i, l in enumerate(t_, 1):
        s = l.rstrip("\r")
        hit = re.match(r"^(={1,6})\s+\S", s) if adoc else re.match(r"^(#{1,6})\s+\S", s)
        if hit:
            rawcount += 1
        m = re.match(r"^(```|~~~)", s)
        if m:
            f = m.group(1) if f is None else (None if s.startswith(f) else f)
            continue
        if adoc and re.match(r"^(----+|\.\.\.\.+)\s*$", s):
            f = s.strip() if f is None else (None if f == s.strip() else f)
            continue
        if f:
            continue
        if hit:
            hs.append((i, s[len(hit.group(1)):].strip()))
    first = hs[0][0] if hs else len(t_) + 1
    all_ = list(hs)
    if first > 1 and any(x.strip() for x in t_[: first - 1]):
        all_.insert(0, (1, "(preamble, no heading)"))
    if not all_:
        all_ = [(1, "(whole file, no heading)")]
    n = 0
    for j, (i, x) in enumerate(all_):
        end = all_[j + 1][0] - 1 if j + 1 < len(all_) else len(t_)
        ty, tg, no = M[d][i]
        rows.append((d, x.replace(TAB, " "), f"{i}-{end}", ty, tg, no))
        n += end - i + 1
    extra = set(M[d]) - {a_[0] for a_ in all_}
    assert not extra, (d, extra)
    assert n == len(t_), (d, n, len(t_))
    chk.append((d, len(t_), len(all_), len(hs), rawcount))

sub = [
    ("Include table", 13, 49, RF, r("packet-includes"), "35 rows; 36 include files on disk (CharacterData.hexpat has no row); the since-T notes are history: keep the content, cut the since"),
    ("Structure comment and marks", 51, 56, RF, r("packet-marks"), "V and I, the server-name rule; why to " + e("evidence-model")),
    ("Naming unknown fields by inference", 58, 84, HT, h("name-an-unknown-field"), "bases list; mark format to " + r("packet-marks") + "; T014c application count to spec-history (006 tasks)"),
    ("Header comment", 86, 103, RF, r("packet-pattern-format"), "packet-id, packet-select, packet-size; reason history to spec-history (005 R2 F2, 006 T002c)"),
    ("JSON conventions", 105, 114, RF, r("packet-pattern-format"), "root key, list and string shape, NaN rule, 65 nonfinite files"),
    ("RES error guard", 116, 123, EX, e("wire-protocol"), "rule also on " + r("packet-pattern-format") + "; 18.0.2 exception"),
    ("Exported checks", 125, 132, RF, r("packet-pattern-format"), "sourceOk, paddingSize, fits, msgFits; 63.11.16 exception"),
    ("What a fit proves", 134, 138, EX, e("packet-decoding-method"), "the fit rule"),
    ("Patterns: status meaning and report key", 185, 234, RF, r("packet-ids"), "legend: id-to-report-path key; the dated recount prose reduces to one date; G mark text to " + r("packet-marks")),
    ("Patterns: how value bases are counted", 235, 246, EX, e("packet-decoding-method"), "rule to " + r("packet-marks") + "; density formula; item and stage density facts"),
    ("Patterns: the per-id table", 248, 844, RF, r("packet-ids"), "595 rows move intact; see the report for generated columns; 31 n/m counts stale"),
]
for s in sub:
    rows.append((p, "[sub] " + s[0], f"{s[1]}-{s[2]}", s[3], s[4], s[5]))

src = pathlib.Path(p).read_text(encoding="utf-8").split(NL)
starts = [i for i in range(846, len(src)) if src[i].startswith("- **")]
last = len(src) if src[-1] else len(src) - 1
ends = starts[1:] + [last]
cl = collections.Counter()
for s_, en in zip(starts, ends):
    ti = re.match(r"- \*\*(.*?)\*\*", src[s_]).group(1)
    if "not patterned" in ti:
        ty, tg, no = HI, SH, "stale: every id listed has a pattern since spec 008; 006 research/season3-exclusive.tsv and the 006 batch reports keep the PC VAs"
        k = "not patterned (stale)"
    elif re.search(r"renames|Naming sweep|types added|Types added|no existing pattern|moved|already Season 3|one existing pattern|14\.10\.16 name", ti):
        ty, tg, no = HI, SH, "the named T..b or TC report and 006 tasks hold it; rename map: the (was ...) notes on " + r("packet-ids")
        k = "history of a batch"
    else:
        ty, tg, no = RF, r("packet-open-questions"), "re-check against spec 008 T007 names when moving; cite report sections through the id-to-report key"
        k = "open question"
    cl[k] += 1
    rows.append((p, "[sub] Open item: " + ti.replace(TAB, " ")[:110], f"{s_ + 1}-{en}", ty, tg, no))

out = pathlib.Path("specs/009-docs-structure/research/T001-sections.tsv")
with out.open("w", encoding="utf-8", newline=NL) as o:
    o.write(TAB.join(["file", "heading", "lines", "type", "target", "notes"]) + NL)
    for x in rows:
        o.write(TAB.join(x) + NL)

heading = [x for x in rows if not x[1].startswith("[sub]")]
print("rows", len(rows), "heading rows", len(heading), "sub", len(rows) - len(heading), dict(cl))
print("types", dict(collections.Counter(x[3] for x in heading)))
print("targets", dict(collections.Counter(KEEP if x[4] == KEEP else SH if x[4] == SH else "docs" for x in heading)))
for c_ in chk:
    print(*c_, sep=TAB)
print("docs", len(chk), "lines", sum(c_[1] for c_ in chk), "headings", sum(c_[3] for c_ in chk), "raw-regex", sum(c_[4] for c_ in chk))
pages = sorted({x[4] for x in rows if x[4].startswith("docs/")})
print(len(pages), *pages, sep=NL)

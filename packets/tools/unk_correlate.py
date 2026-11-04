"""Value correlation of the `unk_*` fields in the 03040008 packet patterns (spec 006 T014a).

For every unknown leaf field of the PS4-matched packet patterns (`*-pattern.cpp`, `include/*.hexpat`)
this collects, per session, the values the exported JSON (`packets/decrypted_json/`) holds, and
compares them with the value sets of the named fields of the same session. It writes one TSV row
per unknown (packet, key path) and a Markdown report. It names nothing: the output is a list of
candidates with counts (spec 006 "Naming unknown fields by inference", basis 2).

Inputs are bounded: the patterns name the packets; each session directory of the JSON tree is
scanned once and only files of patterned packets are read.

Usage (from the repository root):
    python -X utf8 -I packets/tools/unk_correlate.py \
        --tsv specs/006-packet-pattern-coverage/research/T014a-value-correlation.tsv \
        --md specs/006-packet-pattern-coverage/research/T014a-value-correlation.md

Stdlib only (json, collections, statistics are enough; measured runtime is in the report).
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import json
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# Thresholds (documented in the report).

INFORMATIVE_MIN_ABS = 256          # integers with |v| < 256 are too common to match by value
SENTINELS = {0xFFFF, 0xFFFFFFFF, 0x7FFFFFFF, 0xFFFFFFFFFFFFFFFF, 0x7FFFFFFFFFFFFFFF, -1}
STRING_MIN_LEN = 3                 # strings shorter than this are not informative
STRONG_SHARE = 0.8                 # share of informative distinct values found in the reference
STRONG_MIN_DISTINCT = 3            # informative distinct values needed for the strong tier
STRONG_MIN_AGREE = 2               # sessions where the session share is >= AGREE_SHARE
AGREE_SHARE = 0.5
MEDIUM_SHARE = 0.5
WEAK_SHARE = 0.2
SMALL_ENUM_MAX_DISTINCT = 16
EPOCH_PAST_YEARS = 10              # timestamp window: capture time - 10 y .. capture time + 2 y
EPOCH_FUTURE_YEARS = 2
TOP_MATCHES = 3
MAX_CHANCE_RATIO = 1 / 3         # chance share above share/3: the reference is too dense to tell

# JSON keys that carry structure or framing, never values worth matching.
META_KEYS = {"group", "id", "subId", "source", "packetcounter", "sourceOk", "paddingSize", "fits",
             "count", "length", "Error", "Result"}
# Keys that only wrap a value: the meaning comes from the nearest key above them.
GENERIC_KEYS = {"entries", "value", "m_unValue", "m_ucValue"}

FILE_RE = re.compile(r"^\d+_(?P<name>.+?)_(?P<ts>\d{4}-\d\d-\d\dT\d\d_\d\d_\d\d(?:\.\d+)?)"
                     r"(?P<tz>[-+]\d\d_\d\d)")
STRUCT_RE = re.compile(r"\bstruct\s+(\w+)\s*(?:<[^>{]*>)?\s*(?::\s*(\w+))?\s*\{")
FIELD_RE = re.compile(
    r"(?:^|(?<=[\s{:)]))"
    r"(?P<type>[A-Za-z_][\w:]*(?:<[^<>;]*(?:<[^<>;]*>)?[^<>;]*>)?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*(?P<arr>\[[^\]]*\])?\s*(?:@[^;]*)?(?:\[\[[^\]]*\]\])?\s*"
    r"(?:=[^;]*)?;")
KEYWORDS = {"return", "if", "else", "while", "for", "match", "fn", "break", "continue", "import",
            "using", "struct", "enum", "bitfield", "union", "namespace"}
ID_NAME_RE = re.compile(r"(Id|ID|UID|Uid|Idx|No)$")


# ---------------------------------------------------------------------------------------------
# Pattern parsing


@dataclass
class StructDef:
    name: str
    file: str
    base: str | None
    fields: dict[str, tuple[str, bool]] = field(default_factory=dict)  # name -> (type, is_array)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def parse_structs(text: str, file: str) -> list[StructDef]:
    text = strip_comments(text)
    out: list[StructDef] = []
    for m in STRUCT_RE.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end():i - 1]
        sd = StructDef(m.group(1), file, m.group(2))
        for line in body.splitlines():
            for fm in FIELD_RE.finditer(line):
                typ, name = fm.group("type"), fm.group("name")
                if typ in KEYWORDS or name in KEYWORDS:
                    continue
                sd.fields.setdefault(name, (typ, fm.group("arr") is not None))
        out.append(sd)
    return out


@dataclass
class PatternSet:
    packets: dict[str, str]                      # packet name -> pattern file name
    structs: dict[str, list[StructDef]]          # struct name -> definitions

    def struct(self, name: str, prefer_file: str) -> StructDef | None:
        defs = self.structs.get(name)
        if not defs:
            return None
        for d in defs:
            if d.file == prefer_file:
                return d
        return defs[0]

    def field_type(self, sd: StructDef, name: str, prefer: str) -> tuple[str, bool] | None:
        seen = set()
        while sd is not None and sd.name not in seen:
            seen.add(sd.name)
            if name in sd.fields:
                return sd.fields[name]
            sd = self.struct(sd.base, prefer) if sd.base else None
        return None


def load_patterns(pattern_dir: Path) -> PatternSet:
    packets: dict[str, str] = {}
    structs: dict[str, list[StructDef]] = defaultdict(list)
    files = sorted(pattern_dir.glob("*-pattern.cpp")) + sorted((pattern_dir / "include").glob("*.hexpat"))
    for path in files:
        rel = path.name if path.parent == pattern_dir else f"include/{path.name}"
        text = path.read_text(encoding="utf-8")
        if path.name.endswith("-pattern.cpp"):
            packets[path.name[: -len("-pattern.cpp")]] = rel
        for sd in parse_structs(text, rel):
            structs[sd.name].append(sd)
    return PatternSet(packets, dict(structs))


def template_arg(typ: str) -> str | None:
    m = re.match(r"MtTypedArray<\s*([\w:]+)\s*>$", typ)
    return m.group(1) if m else None


def declared_unknowns(ps: PatternSet) -> set[tuple[str, str, str]]:
    """(file, struct, field) of every value-bearing unk_ field (scalar, scalar array, scalar list)."""
    out = set()
    for defs in ps.structs.values():
        for sd in defs:
            for name, (typ, _arr) in sd.fields.items():
                if not name.startswith("unk"):
                    continue
                inner = template_arg(typ) or typ
                if inner not in ps.structs or inner in {"CDataCommonU32", "CDataCommonU8"}:
                    out.add((sd.file, sd.name, name))
    return out


# ---------------------------------------------------------------------------------------------
# JSON flattening


def flatten(obj, prefix: str = ""):
    """Yield (key path, value) for every scalar leaf; list levels add `[]` to the key."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for v in obj:
            yield from flatten(v, prefix + "[]")
    else:
        yield prefix, obj


def segments(path: str) -> list[str]:
    return [s.replace("[]", "") for s in path.split(".")]


def deciding_index(segs: list[str]) -> int:
    i = len(segs) - 1
    while i > 0 and segs[i] in GENERIC_KEYS:
        i -= 1
    return i


def is_meta(path: str) -> bool:
    return segments(path)[-1] in META_KEYS


def is_unknown(path: str) -> bool:
    segs = segments(path)
    return segs[deciding_index(segs)].startswith("unk")


def leaf_name(path: str) -> str:
    segs = segments(path)
    return segs[deciding_index(segs)]


def resolve(ps: PatternSet, packet: str, path: str) -> tuple[str, str, str]:
    """(defining file, struct, field) of the deciding segment of a packet key path, or '?'."""
    prefer = ps.packets.get(packet, "?")
    segs = segments(path)
    target = deciding_index(segs)
    if segs and segs[0] == "packet":
        segs, target = segs[1:], target - 1
    sd = ps.struct(packet, prefer)
    i = 0
    while sd is not None and i < len(segs):
        seg = segs[i]
        if i == target:
            return sd.file, sd.name, seg
        ft = ps.field_type(sd, seg, prefer)
        if ft is None:
            break
        typ = ft[0]
        inner = template_arg(typ)
        if inner is not None:
            typ = inner
            if i + 1 < len(segs) and segs[i + 1] == "entries":
                if i + 1 == target:
                    return sd.file, sd.name, seg
                i += 1
        nxt = ps.struct(typ, prefer)
        if nxt is None:
            return sd.file, sd.name, seg  # a scalar or an array of scalars decides
        sd = nxt
        i += 1
    return "?", "?", segs[target] if 0 <= target < len(segs) else path


# ---------------------------------------------------------------------------------------------
# Collection


def normalize(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float, str)):
        return v
    return None


def informative(v) -> bool:
    if isinstance(v, str):
        return len(v) >= STRING_MIN_LEN
    if isinstance(v, float) and not v.is_integer():
        return abs(v) >= INFORMATIVE_MIN_ABS
    return abs(v) >= INFORMATIVE_MIN_ABS and int(v) not in SENTINELS


def session_of(dirname: str, group: str) -> str:
    return dirname.split("_tcp-stream")[0] if group == "capture" else dirname


def capture_epoch(ts: str, tz: str) -> float:
    base = dt.datetime.strptime(ts.split(".")[0], "%Y-%m-%dT%H_%M_%S")
    sign = 1 if tz[0] == "+" else -1
    hh, mm = int(tz[1:3]), int(tz[4:6])
    offset = dt.timedelta(hours=hh, minutes=mm) * sign
    return base.replace(tzinfo=dt.timezone(offset)).timestamp()


@dataclass
class Corpus:
    # leaves[session][(packet, path)][value] = file id of the first occurrence
    leaves: dict[str, dict[tuple[str, str], dict]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    counts: dict[tuple[str, str], int] = field(default_factory=lambda: defaultdict(int))
    files: list[str] = field(default_factory=list)
    session_epoch: dict[str, float] = field(default_factory=dict)
    streams: int = 0
    skipped_unpatterned: int = 0
    bad_json: int = 0
    bad_examples: list = field(default_factory=list)
    packets_seen: set[str] = field(default_factory=set)


def collect(json_dir: Path, ps: PatternSet, group: str = "capture") -> Corpus:
    c = Corpus()
    for entry in sorted(os.scandir(json_dir), key=lambda e: e.name):
        if not entry.is_dir():
            continue
        c.streams += 1
        session = session_of(entry.name, group)
        for f in os.scandir(entry.path):
            m = FILE_RE.match(f.name)
            if not m or not f.name.endswith(".json"):
                continue
            name = m.group("name")
            if name not in ps.packets:
                c.skipped_unpatterned += 1
                continue
            if session not in c.session_epoch:
                c.session_epoch[session] = capture_epoch(m.group("ts"), m.group("tz"))
            try:
                with open(f.path, "rb") as fh:
                    data = json.load(fh)
            except (OSError, ValueError):
                c.bad_json += 1
                if len(c.bad_examples) < 3:
                    c.bad_examples.append(f"{entry.name}/{f.name}")
                continue
            fid = len(c.files)
            c.files.append(f"{entry.name}/{f.name}")
            c.packets_seen.add(name)
            per = c.leaves[session]
            for path, raw in flatten(data):
                if is_meta(path):
                    continue
                v = normalize(raw)
                if v is None:
                    continue
                key = (name, path)
                c.counts[key] += 1
                per[key].setdefault(v, fid)
    return c


# ---------------------------------------------------------------------------------------------
# Scoring


@dataclass
class Match:
    ref: str                 # reference label: Packet:path, or epoch pseudo-reference
    leaf: str                # reference leaf name
    matched: int             # (session, value) pairs found in the reference, same session
    total: int               # (session, value) pairs of the unknown considered
    agree: int               # sessions with session share >= AGREE_SHARE
    sessions: int            # sessions where the unknown has considered values
    other: int               # pairs found in the reference only in other sessions or also there
    examples: list = field(default_factory=list)
    chance: float = 0.0      # share expected by chance from the reference's value density

    @property
    def lift(self) -> float:
        return self.share - self.chance

    @property
    def share(self) -> float:
        return self.matched / self.total if self.total else 0.0

    @property
    def other_share(self) -> float:
        return self.other / self.total if self.total else 0.0


@dataclass
class Row:
    packet: str
    path: str
    defined_in: str
    struct: str
    field_name: str
    values: int
    distinct: int
    informative_distinct: int
    sessions: int
    vmin: object
    vmax: object
    flags: list[str]
    tier: str
    basis: str               # informative | all-nonbinary
    matches: list[Match]


def ref_class(leaf: str) -> str:
    return "id" if ID_NAME_RE.search(leaf) else "named"


def build_index(c: Corpus):
    """value -> {ref key: {session: first file id}} over named, non-meta leaves, plus per ref
    key the numeric density (distinct values / (max - min + 1)) and range."""
    idx: dict = defaultdict(lambda: defaultdict(dict))
    nums: dict = defaultdict(set)
    for session, per in c.leaves.items():
        for key, vals in per.items():
            if is_unknown(key[1]):
                continue
            for v, fid in vals.items():
                idx[v][key].setdefault(session, fid)
                if isinstance(v, int):
                    nums[key].add(v)
    density = {k: (len(vs) / (max(vs) - min(vs) + 1), min(vs), max(vs)) for k, vs in nums.items()}
    return idx, density


def score(c: Corpus, index, key: tuple[str, str], only_informative: bool) -> list[Match]:
    idx, density = index
    acc: dict = {}
    considered_ints: list = []
    total = 0
    per_session_total: dict[str, int] = {}
    per_session_hit: dict = defaultdict(lambda: defaultdict(int))
    epoch_hits = defaultdict(int)
    epoch_examples: list = []
    for session, per in c.leaves.items():
        vals = per.get(key)
        if not vals:
            continue
        considered = [v for v in vals if (informative(v) if only_informative else v not in (0, 1))]
        if not considered:
            continue
        per_session_total[session] = len(considered)
        considered_ints.extend(v for v in considered if isinstance(v, int))
        total += len(considered)
        ep = c.session_epoch.get(session)
        for v in considered:
            if ep is not None and isinstance(v, (int, float)) and not isinstance(v, bool):
                lo, hi = ep - EPOCH_PAST_YEARS * 365.25 * 86400, ep + EPOCH_FUTURE_YEARS * 365.25 * 86400
                for unit, scale in (("epoch_s", 1), ("epoch_ms", 1000)):
                    if lo * scale <= v <= hi * scale:
                        epoch_hits[(unit, session)] += 1
                        if len(epoch_examples) < 2:
                            epoch_examples.append((v, c.files[vals[v]], unit))
            for ref, sess in idx.get(v, {}).items():
                m = acc.get(ref)
                if m is None:
                    m = acc[ref] = Match(f"{ref[0]}:{ref[1]}", leaf_name(ref[1]), 0, 0, 0, 0, 0)
                if session in sess:
                    m.matched += 1
                    per_session_hit[ref][session] += 1
                    if len(m.examples) < 2:
                        m.examples.append((v, c.files[vals[v]], c.files[sess[session]]))
                if len(sess) > (1 if session in sess else 0):
                    m.other += 1
    out = []
    considered_ints.sort()
    for ref, m in acc.items():
        m.total, m.sessions = total, len(per_session_total)
        if ref in density and total:
            dens, lo, hi = density[ref]
            inside = bisect.bisect_right(considered_ints, hi) - bisect.bisect_left(considered_ints, lo)
            m.chance = inside * dens / total
        m.agree = sum(1 for s, n in per_session_hit[ref].items() if n / per_session_total[s] >= AGREE_SHARE)
        out.append(m)
    for unit in ("epoch_s", "epoch_ms"):
        hits = {s: n for (u, s), n in epoch_hits.items() if u == unit}
        if hits:
            m = Match(f"(timestamp {unit}, capture time -{EPOCH_PAST_YEARS} y/+{EPOCH_FUTURE_YEARS} y)",
                      unit, sum(hits.values()), total,
                      sum(1 for s, n in hits.items() if n / per_session_total[s] >= AGREE_SHARE),
                      len(per_session_total), 0,
                      [(v, f, "-") for v, f, u in epoch_examples if u == unit])
            out.append(m)
    # Rank: share, agreeing sessions, specificity (lower other share), then id-like names first.
    out.sort(key=lambda m: (-m.lift, -m.agree, m.other_share, ref_class(m.leaf) != "id", m.ref))
    best: dict[str, Match] = {}
    for m in out:
        best.setdefault(m.leaf, m)
    return list(best.values())[:TOP_MATCHES]


def stats_flags(values: list) -> tuple[list[str], object, object]:
    nums = [v for v in values if isinstance(v, (int, float))]
    flags = []
    distinct = set(values)
    if len(distinct) == 1:
        flags.append("constant")
    if nums and distinct <= {0, 1}:
        flags.append("0-1")
    elif nums and len(distinct) <= SMALL_ENUM_MAX_DISTINCT and all(abs(v) < INFORMATIVE_MIN_ABS for v in nums):
        flags.append("small-enum")
    if len(distinct) < 3:
        flags.append("lt3-distinct")
    vmin = min(nums) if nums else ""
    vmax = max(nums) if nums else ""
    return flags, vmin, vmax


def tier_of(m: Match | None, informative_distinct: int, basis: str) -> str:
    if m is None or m.share < WEAK_SHARE:
        return "unexplained"
    if m.chance > m.share * MAX_CHANCE_RATIO:
        return "weak"
    if basis == "informative" and informative_distinct >= STRONG_MIN_DISTINCT:
        if m.share >= STRONG_SHARE and m.agree >= STRONG_MIN_AGREE:
            return "strong"
        if m.share >= MEDIUM_SHARE:
            return "medium"
    return "weak"


def analyse(c: Corpus, ps: PatternSet) -> list[Row]:
    idx = build_index(c)
    unknown_keys = sorted({k for per in c.leaves.values() for k in per if is_unknown(k[1])})
    rows = []
    for key in unknown_keys:
        all_vals, sessions = [], 0
        for per in c.leaves.values():
            vals = per.get(key)
            if vals:
                sessions += 1
                all_vals.extend(vals.keys())
        distinct = set(all_vals)
        inf = {v for v in distinct if informative(v)}
        flags, vmin, vmax = stats_flags(list(distinct))
        basis = "informative" if len(inf) >= 1 else "all-nonbinary"
        matches = score(c, idx, key, basis == "informative")
        if len(inf) < STRONG_MIN_DISTINCT:
            flags.append("few-informative")
        if matches and matches[0].share > 0 and matches[0].other_share >= matches[0].share:
            flags.append("global-values")
        if matches and matches[0].chance > matches[0].share * MAX_CHANCE_RATIO:
            flags.append("dense-reference")
        file, struct, fname = resolve(ps, key[0], key[1])
        rows.append(Row(key[0], key[1], file, struct, fname, c.counts[key], len(distinct), len(inf),
                        sessions, vmin, vmax, flags, tier_of(matches[0] if matches else None, len(inf), basis),
                        basis, matches))
    return rows


# ---------------------------------------------------------------------------------------------
# Output

TSV_HEADER = ["tier", "defined_in", "struct", "field", "packet", "key_path", "sessions", "values",
              "distinct", "informative_distinct", "min", "max", "flags", "basis"]
for _i in range(1, TOP_MATCHES + 1):
    TSV_HEADER += [f"match{_i}", f"share{_i}", f"agree{_i}", f"other_share{_i}", f"chance{_i}"]

TIER_ORDER = {"strong": 0, "medium": 1, "weak": 2, "unexplained": 3, "no-data": 4}


def fmt_val(v) -> str:
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def write_tsv(rows: list[Row], nodata: list[tuple[str, str, str]], path: Path) -> None:
    lines = ["\t".join(TSV_HEADER)]
    for r in sorted(rows, key=lambda r: (TIER_ORDER[r.tier], -(r.matches[0].share if r.matches else 0),
                                         r.defined_in, r.packet, r.path)):
        cells = [r.tier, r.defined_in, r.struct, r.field_name, r.packet, r.path, str(r.sessions),
                 str(r.values), str(r.distinct), str(r.informative_distinct), str(r.vmin), str(r.vmax),
                 ",".join(r.flags), r.basis]
        for i in range(TOP_MATCHES):
            if i < len(r.matches):
                m = r.matches[i]
                cells += [m.ref, f"{m.matched}/{m.total}", f"{m.agree}/{m.sessions}", f"{m.other_share:.2f}",
                          f"{m.chance:.2f}"]
            else:
                cells += ["", "", "", "", ""]
        lines.append("\t".join(c.replace("\t", " ") for c in cells))
    for file, struct, fname in nodata:
        lines.append("\t".join(["no-data", file, struct, fname] + [""] * (len(TSV_HEADER) - 4)))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_md(rows: list[Row], nodata, info: dict, path: Path) -> None:
    by = defaultdict(list)
    for r in rows:
        by[r.tier].append(r)
    for t in by:
        by[t].sort(key=lambda r: (-(r.matches[0].share if r.matches else 0), -(r.matches[0].agree if r.matches else 0),
                                  r.defined_in, r.packet, r.path))
    L = []
    a = L.append
    a("# 006 T014a: value correlation of the unknown packet fields (client 03040008)")
    a("")
    a("Basis 2 of spec 006 \"Naming unknown fields by inference\": does an `unk_*` field hold, in the "
      "same session, the values of a named field? Nothing is renamed here; every candidate below is "
      "`I (value: n/m match <field> in <packet>)` material at best and needs the coincidence check "
      "the spec asks for (constants, 0/1 and small enums need more evidence).")
    a("")
    a("Produced by `packets/tools/unk_correlate.py` (stdlib only); one row per "
      "unknown (packet, key path) in `T014a-value-correlation.tsv`.")
    a("")
    a("## Inputs and run")
    a("")
    for k, v in info.items():
        a(f"- {k}: {v}")
    a("")
    a("## Method")
    a("")
    a("1. Patterns: every `*-pattern.cpp` names one packet; the struct declarations of the patterns "
      "and `include/*.hexpat` resolve each JSON key path to the struct and file that declare it "
      "(`defined_in`, `?` when the light parser cannot follow the path).")
    a("2. JSON: each stream directory of `packets/decrypted_json/` is scanned once; only files whose "
      "name carries a patterned packet are read. Each file is flattened to scalar leaves by key path "
      "(list levels as `[]`; `count`, `length` and the header and fit keys are dropped). A leaf is "
      "unknown when its deciding key (the nearest key that is not `entries`, `value`, `m_unValue` "
      "or `m_ucValue`) starts with `unk`; all other leaves are named reference fields.")
    a(f"3. Session = {info.get('session unit', 'capture')}: all values of a field within one session "
      "form its value set for that session.")
    a("4. Considered values of an unknown: the informative distinct values per session "
      f"(integers with |v| >= {INFORMATIVE_MIN_ABS}, excluding 0xFFFF, 0x7FFFFFFF, 0xFFFFFFFF, "
      f"all-ones u64 and -1; non-integral floats with |v| >= {INFORMATIVE_MIN_ABS}; strings of "
      f">= {STRING_MIN_LEN} characters). An unknown with no informative value is matched on all its "
      "values except 0 and 1 (`basis` all-nonbinary) and can reach the weak tier only.")
    a("5. Per reference field R (packet + key path) the score is `share` = (session, value) pairs of the "
      "unknown found in R's value set of the same session / all considered pairs; `agree` = sessions "
      f"whose own share is >= {AGREE_SHARE}; `other_share` = pairs that R holds in another session "
      "(a high other_share against share means a global catalogue value such as an item or stage "
      "id; a low one, a session-specific value such as a character id or UID). A pseudo-reference "
      f"tests timestamps: values within capture time -{EPOCH_PAST_YEARS} y/+{EPOCH_FUTURE_YEARS} y "
      "as epoch seconds or milliseconds.")
    a("6. Coincidence control: `chance` = the share expected if the unknown's integer values hit "
      "the reference at its density (distinct values / (max - min + 1)) inside its range. A "
      f"reference whose chance exceeds share x {MAX_CHANCE_RATIO:.2f} is too dense to tell "
      "(`dense-reference`; the row stays weak).")
    a(f"7. The best reference per leaf name is kept and the top {TOP_MATCHES} leaf names are reported, "
      "ranked by share - chance, agree, lower other_share, id-like name.")
    a("")
    a("Caveat on `other_share`: the captures mostly record one player account (inferred: the storage owner id 2144504 recurs in all 41 sessions), so its character and pawn "
      "ids recur in nearly every capture; for these ids other_share is high although they are "
      "session data. Specificity across sessions therefore cannot separate account ids from "
      "catalogue ids in this corpus; `chance` and the reference name carry that judgement.")
    a("")
    a("Tiers:")
    a("")
    a(f"- **strong**: >= {STRONG_MIN_DISTINCT} informative distinct values, share >= {STRONG_SHARE}, "
      f"agree >= {STRONG_MIN_AGREE} sessions.")
    a(f"- **medium**: >= {STRONG_MIN_DISTINCT} informative distinct values and share >= {MEDIUM_SHARE}, "
      "but not strong (usually a single session).")
    a(f"- **weak**: best share >= {WEAK_SHARE} otherwise (few informative values, or matched on small "
      "values only).")
    a(f"- **unexplained**: no reference reaches share {WEAK_SHARE}.")
    a("- **no-data**: a declared value-bearing unk field that no JSON file holds.")
    a("")
    a("Flags: `constant`, `0-1`, `small-enum` (<= 16 distinct values, all |v| < 256), `lt3-distinct`, "
      "`few-informative` (< 3 informative distinct values), `global-values` (other_share >= share), "
      "`dense-reference` (chance > share/3).")
    a("")
    counts = {t: len(by.get(t, [])) for t in ("strong", "medium", "weak", "unexplained")}
    counts["no-data"] = len(nodata)
    a("## Summary")
    a("")
    a("| Tier | Rows |")
    a("| --- | --- |")
    for t, n in counts.items():
        a(f"| {t} | {n} |")
    a("")

    def mline(m: Match) -> str:
        return (f"{m.ref} ({m.matched}/{m.total}, agree {m.agree}/{m.sessions}, other {m.other_share:.2f}, "
                f"chance {m.chance:.2f})")

    a("## Strong candidates")
    a("")
    a("Each with the best reference, the runners-up and two example value pairs (unknown file -> "
      "reference file, both in `packets/decrypted_json/`).")
    a("")
    for r in by.get("strong", []):
        m = r.matches[0]
        a(f"### {r.packet} `{r.path}`")
        a("")
        a(f"- declared: `{r.defined_in}` {r.struct}.{r.field_name}; values {r.values}, distinct "
          f"{r.distinct} (informative {r.informative_distinct}), sessions {r.sessions}, range "
          f"{r.vmin}..{r.vmax}; flags {','.join(r.flags) or '-'}")
        a(f"- best: **{m.leaf}** in {mline(m)}")
        for o in r.matches[1:]:
            a(f"- also: {o.leaf} in {mline(o)}")
        for v, uf, rf in m.examples[:2]:
            a(f"- example: {fmt_val(v)}: `{uf}` -> `{rf}`")
        a("")
    a("## Medium candidates")
    a("")
    a("| Packet | Key path | Declared | Distinct (inf.) | Best match | Share | Agree | Other | Chance | Flags |")
    a("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in by.get("medium", []):
        m = r.matches[0]
        a(f"| {r.packet} | `{r.path}` | `{r.defined_in}` {r.struct} | {r.distinct} ({r.informative_distinct}) | "
          f"{m.ref} | {m.matched}/{m.total} | {m.agree}/{m.sessions} | {m.other_share:.2f} | {m.chance:.2f} | {','.join(r.flags)} |")
    a("")
    a("## Weak candidates")
    a("")
    a("Matches too thin to name anything (few or small values, or a low share); listed for the "
      "consumer trace (basis 1).")
    a("")
    a("| Packet | Key path | Distinct (inf.) | Basis | Best match | Share | Agree | Flags |")
    a("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in by.get("weak", []):
        m = r.matches[0]
        a(f"| {r.packet} | `{r.path}` | {r.distinct} ({r.informative_distinct}) | {r.basis} | {m.ref} | "
          f"{m.matched}/{m.total} | {m.agree}/{m.sessions} | {','.join(r.flags)} |")
    a("")
    a("## Unexplained by correlation")
    a("")
    a("No named field of the same session holds their values at share >= "
      f"{WEAK_SHARE} (mostly constants, 0/1 flags and small enums).")
    a("")
    a("| Packet | Key path | Declared | Distinct | Range | Flags |")
    a("| --- | --- | --- | --- | --- | --- |")
    for r in by.get("unexplained", []):
        a(f"| {r.packet} | `{r.path}` | `{r.defined_in}` {r.struct} | {r.distinct} | {r.vmin}..{r.vmax} | "
          f"{','.join(r.flags)} |")
    a("")
    a("## Declared unknowns without data")
    a("")
    a("Value-bearing `unk_*` declarations that no exported JSON file holds (packet not captured, "
      "branch not taken, or a path the resolver could not follow).")
    a("")
    for file, struct, fname in nodata:
        a(f"- `{file}` {struct}.{fname}")
    a("")
    path.write_text("\n".join(L), encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------------------------


def run(pattern_dir: Path, json_dir: Path, group: str):
    if not pattern_dir.is_dir() or not json_dir.is_dir():
        raise SystemExit(f"unk_correlate: missing input directory: {pattern_dir} or {json_dir}")
    ps = load_patterns(pattern_dir)
    if not ps.packets:
        raise SystemExit(f"unk_correlate: no *-pattern.cpp in {pattern_dir}")
    c = collect(json_dir, ps, group)
    if not c.files:
        raise SystemExit("unk_correlate: no JSON file of a patterned packet found; refusing to "
                         "write an empty correlation")
    rows = analyse(c, ps)
    observed = {(r.defined_in, r.struct, r.field_name) for r in rows}
    nodata = sorted(declared_unknowns(ps) - observed)
    return ps, c, rows, nodata


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--patterns", type=Path, default=Path("packets/patterns/03040008"))
    ap.add_argument("--json", type=Path, default=Path("packets/decrypted_json"))
    ap.add_argument("--group", choices=("capture", "stream"), default="capture",
                    help="session unit: one capture file (all its TCP streams) or one TCP stream")
    ap.add_argument("--tsv", type=Path, required=True)
    ap.add_argument("--md", type=Path)
    args = ap.parse_args(argv)
    t0 = time.monotonic()
    ps, c, rows, nodata = run(args.patterns, args.json, args.group)
    elapsed = time.monotonic() - t0
    write_tsv(rows, nodata, args.tsv)
    info = {
        "build": "client 03040008 (PC), patterns in `packets/patterns/03040008/`",
        "patterns (packets)": len(ps.packets),
        "struct definitions parsed": sum(len(v) for v in ps.structs.values()),
        "stream directories scanned": c.streams,
        "sessions": len(c.leaves),
        "session unit": "one capture file (all its TCP streams: login and game server)"
        if args.group == "capture" else "one TCP stream",
        "JSON files read": len(c.files),
        "JSON files of unpatterned names skipped": c.skipped_unpatterned,
        "JSON files unreadable (invalid JSON, skipped)": str(c.bad_json)
        + (f" (e.g. `{c.bad_examples[0]}`)" if c.bad_examples else ""),
        "packets with JSON": len(c.packets_seen),
        "unknown (packet, key path) rows": len(rows),
        "declared value-bearing unk fields": len(declared_unknowns(ps)),
        "runtime": f"{elapsed:.0f} s (CPython {sys.version.split()[0]}, stdlib json)",
    }
    if args.md:
        write_md(rows, nodata, info, args.md)
    for k, v in info.items():
        print(f"{k}: {v}")
    tiers = defaultdict(int)
    for r in rows:
        tiers[r.tier] += 1
    print("tiers:", dict(tiers), "no-data:", len(nodata))
    return 0


if __name__ == "__main__":
    sys.exit(main())

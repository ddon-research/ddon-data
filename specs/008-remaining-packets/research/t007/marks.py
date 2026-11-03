"""008 T007: distinct values behind every `I (... value ...)` mark of the 008 patterns and includes.

For each mark comment (`// T00[345] I (...value...)`) the script finds the field it annotates, every JSON path
of that field in the captures of the patterns that reach its struct, and counts the values and distinct values.
For fields whose basis names item or stage ids it adds the chance that every distinct value lands in the id table
by luck (density of the table over the observed range, to the power of the distinct count; T006 itemdistinct.py).

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t007/marks.py [tsv-out]
"""
import glob
import json
import os
import re
import sys

PAT = os.path.join("research", "03040008", "packets")
JSN = os.path.join("packets", "decrypted_json")
INCLUDES_008 = ["SeasonDungeon.hexpat", "DailyMission.hexpat", "InfinityDelivery.hexpat", "ChainDungeon.hexpat",
                "Instance.hexpat"]

STRUCT_RE = re.compile(r"^struct\s+(\w+)(?:\s*:\s*\w+)?\s*\{", re.M)
MEMBER_RE = re.compile(r"^\s*(?:\}\s*else\s*)?(?:if\s*\([^)]*\)\s*\{\s*)?"
                       r"([A-Za-z_][\w:]*(?:<\s*[\w:]+\s*>)?)\s+([A-Za-z_]\w*)\s*(\[[^\]]*\])?\s*(?:=[^;]*)?;")
KEYWORDS = {"return", "import", "using", "if", "else"}


def parse_structs(path):
    """struct name -> list of (line_no, type, name, comment_text)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out = {}
    cur = None
    pending = []
    for no, raw in enumerate(lines, 1):
        m = STRUCT_RE.match(raw)
        if m:
            cur = out.setdefault(m.group(1), [])
            pending = []
            continue
        if cur is None:
            continue
        if raw.startswith("};"):
            cur = None
            continue
        code, _, tail = raw.partition("//")
        if not code.strip():
            if tail:
                pending.append((no, tail.strip()))
            else:
                pending = []
            continue
        mm = MEMBER_RE.match(code)
        if mm and mm.group(1) not in KEYWORDS:
            cmt = pending + ([(no, tail.strip())] if tail else [])
            cur.append((no, mm.group(1), mm.group(2), cmt))
        pending = []
    return out


def elem_type(t):
    m = re.match(r"MtTypedArray<\s*([\w:]+)\s*>", t)
    return (m.group(1), True) if m else (t, False)


def top_struct(path):
    m = re.search(r"^(\w+)\s+packet\s*@\s*0x00\s*;", open(path, encoding="utf-8").read(), re.M)
    return m.group(1) if m else None


def packet_id(path):
    m = re.search(r"^// packet-id:\s*(\S+)", open(path, encoding="utf-8").read(), re.M)
    return m.group(1) if m else None


def json_files(pid):
    g, i, s = pid.split(".")
    return glob.glob(os.path.join(JSN, "*", "*.%s_%s_%s.json" % (g, i, s)))


def nodes(o, keys):
    """values at path keys (lists and {count, entries} transparently expanded)."""
    if isinstance(o, list):
        for e in o:
            yield from nodes(e, keys)
        return
    if isinstance(o, dict) and set(o) == {"count", "entries"}:
        for e in o["entries"]:
            yield from nodes(e, keys)
        return
    if not keys:
        yield o
        return
    if isinstance(o, dict) and keys[0] in o:
        yield from nodes(o[keys[0]], keys[1:])


def atoms(o):
    """distinguishable values of one node: list elements one by one, strings by text, structs serialized."""
    if isinstance(o, dict) and set(o) == {"count", "entries"}:
        for e in o["entries"]:
            yield from atoms(e)
        return
    if isinstance(o, dict) and set(o) == {"length", "value"}:
        yield o["value"]
        return
    if isinstance(o, dict) and len(o) == 1:
        yield next(iter(o.values()))
        return
    if isinstance(o, (dict, list)):
        yield json.dumps(o, sort_keys=True, ensure_ascii=False)
        return
    yield o


def id_set(path, keys):
    s = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in keys and isinstance(v, int):
                    s.add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.load(open(path, encoding="utf-8")))
    return s


ITEMS = id_set(os.path.join("client", "03040008", "base", "etc", "itemlist.ipa.json"), ("ItemId", "Id", "ItemID"))
STAGES = id_set(os.path.join("client", "03040008", "base", "scr", "stage_list.slt.json"), ("StageId",))


def chance(vals, table):
    ints = [v for v in vals if isinstance(v, int)]
    if not ints:
        return None, None
    lo, hi = max(1, min(ints)), max(ints)
    dens = sum(1 for k in range(lo, hi + 1) if k in table) / max(1, hi - lo + 1)
    hit = sum(1 for v in set(ints) if v in table)
    return hit, dens ** len(set(ints))


def main():
    inc_structs = {}
    for f in glob.glob(os.path.join(PAT, "include", "*.hexpat")):
        for k, v in parse_structs(f).items():
            inc_structs.setdefault(k, (f, v))
    pats = [f for f in glob.glob(os.path.join(PAT, "*-pattern.cpp"))
            if "specs/008-remaining-packets" in open(f, encoding="utf-8").read(400)]
    # (file, struct) -> list of (pid, prefix keys)
    reach = {}
    for f in pats:
        local = {k: (f, v) for k, v in parse_structs(f).items()}
        pid = packet_id(f)
        top = top_struct(f)
        if not pid or not top:
            continue

        def visit(sname, prefix, depth):
            src = local.get(sname) or inc_structs.get(sname)
            if not src or depth > 12:
                return
            reach.setdefault((src[0], sname), []).append((pid, prefix))
            for _, t, n, _ in src[1]:
                et, _ = elem_type(t)
                visit(et, prefix + [n], depth + 1)
        visit(top, [], 0)
    targets = pats + [os.path.join(PAT, "include", i) for i in INCLUDES_008]
    rows = []
    cache = {}
    for f in targets:
        for sname, members in parse_structs(f).items():
            for no, t, name, cmt in members:
                text = " ".join(c for _, c in cmt)
                if not re.search(r"T00[345] I \(", text) or "value" not in text:
                    continue
                vals = []
                pids = set()
                for pid, prefix in reach.get((f, sname), []):
                    pids.add(pid)
                    if pid not in cache:
                        cache[pid] = [json.load(open(j, encoding="utf-8"))["packet"] for j in json_files(pid)]
                    for p in cache[pid]:
                        for nd in nodes(p, prefix + [name]):
                            vals.extend(atoms(nd))
                d = set(json.dumps(v, ensure_ascii=False) if not isinstance(v, (int, str)) else v for v in vals)
                low = text.lower()
                tbl = None
                if "item" in low and ("id" in low or "itemlist" in low):
                    tbl = ("item", ITEMS)
                elif "stage" in low:
                    tbl = ("stage", STAGES)
                hit = p_ch = None
                if tbl:
                    flat = set()
                    for v in d:
                        if isinstance(v, str) and v.startswith("{"):
                            o = json.loads(v)
                            for k in ("StageId", "ItemId", "ItemID"):
                                if isinstance(o.get(k), int):
                                    flat.add(o[k])
                        else:
                            flat.add(v)
                    hit, p_ch = chance(list(flat), tbl[1])
                rows.append((os.path.relpath(f, PAT).replace("\\", "/"), cmt[0][0], no, sname, name,
                             ",".join(sorted(pids)), len(vals), len(d),
                             "" if tbl is None else "%s in=%s p=%.2g" % (tbl[0], hit, p_ch if p_ch is not None else -1),
                             "|".join(str(x) for x in sorted(d, key=str)[:6])[:80], text))
    out = open(sys.argv[1], "w", encoding="utf-8", newline="\n") if len(sys.argv) > 1 else sys.stdout
    out.write("file\tcomment_line\tline\tstruct\tfield\tpids\tn\tdistinct\tchance\tsample\tmark\n")
    for r in rows:
        out.write("\t".join(re.sub(r"[\t\r\n]+", " ", str(x)) for x in r) + "\n")
    print("marks: %d" % len(rows), file=sys.stderr)


if __name__ == "__main__":
    main()

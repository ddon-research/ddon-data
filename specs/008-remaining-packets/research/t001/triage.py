"""008 T001 step 2: per uncovered id, the PC code facts, the captures' fit, the 006 notes and the Arrowgene lead.

Run from D:/ddon-data:
    python -X utf8 -I specs/008-remaining-packets/research/t001/inventory.py INV.json
    python -X utf8 -I specs/008-remaining-packets/research/t001/triage.py INV.json OUT.tsv [DETAIL.txt]
Stdlib only. Reads (never writes): research/03040008/ida-transfer/dumps/pc-ida.jsonl (v6, PC 03040008,
image base 0x400000, VAs), packets/decrypted_raw, specs/006-packet-pattern-coverage/research/season3-exclusive.tsv,
D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline (PacketId.cs, Entity/PacketStructure, Entity/Structure).

PC side (V where the dump proves it, the list shape is inferred, see LIST below):
- S2C: handler = the `table` record's callback for (g,id,sub); the walk enters the handler.
- C2S: sender = every function whose call to WritePacket 0x8BCBB0 carries const stack slots 1,2,3 = g,id,sub.
- Codec tree: codec leaves in call-site order (codec widths from the dump's `codec` field, the four
  variable-length codecs by VA as matcher/codecs.py), entering every dumped callee except the skip list
  and callees whose codec_distance is null. Indirect calls are counted, never entered.
- LIST (I, own heuristic): a read-4 leaf whose next call (or the one after) is the allocator 0x8BC2E0 is a
  count, and so is a read-4 whose next call is a non-entered helper called again later in the same function
  (the MtTypedArray resize; lists of inline elements allocate nothing, e.g. 0x757F20); the element is the
  rest of that function's events up to the next call of that helper, else to the function's end. Writers carry no allocator, so a C2S fit
  that fails plain is retried with "first write-4 of each entered callee = count".
Fit: body from 0x09; decode ends within the last 15 bytes (006 rule), no overrun. RES: the PC reader reads
s32 Error + s32 Result itself; a file whose Error != 0 is counted as `err`, not fitted.
"""
import csv
import json
import os
import re
import struct
import sys
from collections import Counter, defaultdict

DUMP = os.path.join("research", "03040008", "ida-transfer", "dumps", "pc-ida.jsonl")
RAW = os.path.join("packets", "decrypted_raw")
S006 = os.path.join("specs", "006-packet-pattern-coverage", "research", "season3-exclusive.tsv")
AG = os.environ.get("ARROWGENE", "D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline")
AGS = AG + "/Arrowgene.Ddon.Shared"
SLACK = 15
WRITE_PACKET = 0x8BCBB0
ALLOC = 0x8BC2E0
SKIP = {0x878860, 0x8BC2E0, 0x8BC340, 0x8BCBB0}
SKIP_NAME = re.compile(r"getAllocator|^_*(?:mem|str)[a-z_]*$|callOnPacketFunc|WritePacket")
VARIABLE = {0x8BC5B0: ("read", "S"), 0x8BC710: ("read", "B"), 0x8BC790: ("write", "S"), 0x8BCA30: ("write", "C")}
MAXD = 10


def load_dump():
    F, T, S = {}, {}, defaultdict(list)
    with open(DUMP, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            k = r["kind"]
            if k == "function":
                r.pop("object_accesses", None)
                r.pop("annotations", None)
                F[r["va"]] = r
            elif k == "table":
                T[(r["group"], r["id"], r["sub"])] = r
            elif k == "header":
                hdr = r
    for va, r in F.items():
        for c in r["calls"]:
            if c.get("target") == WRITE_PACKET:
                cs = dict((s, v) for s, v in c.get("const_stack") or [])
                if all(s in cs for s in (1, 2, 3)):
                    S[(cs[1], cs[2], cs[3])].append((va, c["site"]))
    return F, T, S, hdr


def codec(F, va):
    if va in VARIABLE:
        return VARIABLE[va]
    r = F.get(va)
    if r and r.get("codec"):
        return r["codec"]["dir"], str(r["codec"]["width"])
    return None


def events(F, va, mode, stack, stat):
    """Nested events of function va: ('t', tok) | ('call', va, kids) | ('list', va, kids)."""
    r = F.get(va)
    if r is None:
        return []
    calls = r["calls"]
    out = []
    raw = []  # (kind, payload, target)
    for c in calls:
        t = c.get("target")
        if not isinstance(t, int):
            stat["indirect"] += 1
            raw.append(("ind", None, None))
            continue
        cd = codec(F, t)
        if cd:
            raw.append(("t", cd[1], t) if cd[0] == mode else ("x", None, t))
            continue
        g = F.get(t)
        if t in SKIP or g is None or SKIP_NAME.search(g["name"]) or g.get("codec_distance") is None:
            raw.append(("o", None, t))
            continue
        if t in stack or len(stack) >= MAXD:
            stat["recursion"] += 1
            raw.append(("o", None, t))
            continue
        stat["funcs"].add(t)
        kids = events(F, t, mode, stack + (t,), stat)
        raw.append(("call", kids, t) if kids else ("o", None, t))
    i = 0
    while i < len(raw):
        k, p, t = raw[i]
        if k == "t" and p == "4" and mode == "read":
            nxt = [x[2] for x in raw[i + 1:i + 3]]
            h1 = raw[i + 1] if i + 1 < len(raw) else None
            again = (h1 is not None and h1[0] == "o" and h1[2] not in (None, ALLOC)
                     and any(x[2] == h1[2] for x in raw[i + 2:]))
            if ALLOC in nxt or again:
                helper = raw[i + 1][2] if raw[i + 1][2] != ALLOC else None
                j = i + 1 + (nxt.index(ALLOC) + 1 if ALLOC in nxt else 1)
                end = len(raw)
                if helper is not None:
                    for m in range(j, len(raw)):
                        if raw[m][2] == helper:
                            end = m
                            break
                kids = conv(raw[j:end])
                if not kids and ALLOC not in nxt:
                    out.extend(conv([raw[i]]))  # a repeated helper around nothing: no list
                    i += 1
                    continue
                out.append(("list", va, kids))
                stat["lists"] += 1
                i = end
                continue
        out.extend(conv([raw[i]]))
        i += 1
    return out


def conv(raw):
    o = []
    for k, p, t in raw:
        if k == "t":
            o.append(("t", p))
        elif k == "call":
            o.append(("call", t, p))
    return o


def render(ev):
    s = []
    for e in ev:
        if e[0] == "t":
            s.append(e[1])
        elif e[0] == "call":
            s.append("%x{%s}" % (e[1], render(e[2])))
        else:
            s.append("L[%s]" % render(e[2]))
    return " ".join(s)


def shape(ev):
    """Token shape without VAs or call brackets: widths, S/C, L[...]."""
    s = []
    for e in ev:
        if e[0] == "t":
            s.append("S" if e[1] == "C" else e[1])
        elif e[0] == "call":
            x = shape(e[2])
            if x:
                s.append(x)
        else:
            s.append("L[%s]" % shape(e[2]))
    return " ".join(s)


def leaves(ev):
    n = 0
    for e in ev:
        n += 1 if e[0] == "t" else leaves(e[2])
    return n


def list_candidates(ev, acc=None):
    """Entered callees whose first event is a 4 (writer list candidates), by VA."""
    acc = [] if acc is None else acc
    for e in ev:
        if e[0] in ("call", "list"):
            if e[0] == "call" and e[2] and e[2][0] == ("t", "4") and e[1] not in acc:
                acc.append(e[1])
            list_candidates(e[2], acc)
    return acc


def writer_lists(ev, chosen):
    """C2S retry: each entered callee in ``chosen`` = its first 4 is a count, the rest the element."""
    o = []
    for e in ev:
        if e[0] == "call":
            kids = writer_lists(e[2], chosen)
            if e[1] in chosen:
                o.append(("list", e[1], kids[1:]))
            else:
                o.append(("call", e[1], kids))
        elif e[0] == "list":
            o.append(("list", e[1], writer_lists(e[2], chosen)))
        else:
            o.append(e)
    return o


class Over(Exception):
    pass


def dec(b, p, ev):
    for e in ev:
        if e[0] == "t":
            tok = e[1]
            if tok in "1248":
                p += int(tok)
            elif tok in "SC":  # C (Write_cstr): u16 length + bytes on the wire (I, captures 12.5.1)
                if p + 2 > len(b):
                    raise Over
                p += 2 + struct.unpack(">H", b[p:p + 2])[0]
            else:
                raise Over  # B / C: length unknown to this walk
            if p > len(b):
                raise Over
        elif e[0] == "call":
            p = dec(b, p, e[2])
        else:
            if p + 4 > len(b):
                raise Over
            n = struct.unpack(">I", b[p:p + 4])[0]
            p += 4
            if n > 5000:
                raise Over
            for _ in range(n):
                p = dec(b, p, e[2])
    return p


def fit(files, ev, is_res):
    ok = err = bad = 0
    for path in files:
        with open(path, "rb") as f:
            b = f.read()
        if is_res and len(b) >= 13 and struct.unpack(">i", b[9:13])[0] != 0:
            err += 1
            continue
        try:
            p = dec(b, 9, ev)
            if len(b) - p <= SLACK:
                ok += 1
            else:
                bad += 1
        except Over:
            bad += 1
    return ok, err, bad


# ---------------- Arrowgene lead ----------------
AG_TOK = {"WriteByte": "1", "WriteBool": "1", "WriteSByte": "1", "WriteUInt16": "2", "WriteInt16": "2",
          "WriteUInt32": "4", "WriteInt32": "4", "WriteFloat": "4", "WriteUInt64": "8", "WriteInt64": "8",
          "WriteDouble": "8", "WriteMtString": "S"}


def ag_index():
    ids = {}
    pid = os.path.join(AGS, "Network", "PacketId.cs")
    rx = re.compile(r'new PacketId\((\d+),\s*(\d+),\s*(\d+),\s*"([A-Z0-9_]+)",\s*ServerType\.(\w+)')
    with open(pid, encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            m = rx.search(line)
            if m:
                side = "L" if m.group(5) == "Login" else "G"
                cm = line.split("//", 1)[1].strip() if "//" in line.split(")", 1)[-1] else ""
                ids[(side, "%s.%s.%s" % m.group(1, 2, 3))] = (m.group(4), n, cm)
    classes = {}  # class name -> (file, write_line, statements, props)
    pkt = {}  # PacketId NAME -> class name
    for sub in ("Entity/PacketStructure", "Entity/Structure"):
        for dp, _, fs in os.walk(os.path.join(AGS, sub)):
            for fn in fs:
                if not fn.endswith(".cs"):
                    continue
                path = os.path.join(dp, fn)
                with open(path, encoding="utf-8-sig", errors="replace") as f:
                    lines = f.read().split("\n")
                parse_cs(path, lines, classes, pkt)
    return ids, classes, pkt


def parse_cs(path, lines, classes, pkt):
    props = {}
    cur = None
    for i, line in enumerate(lines):
        m = re.search(r"\bclass\s+(\w+)", line)
        if m and "Serializer" not in m.group(1):
            cur = m.group(1)
        m = re.search(r"PacketId\s+Id\s*=>\s*PacketId\.([A-Z0-9_]+)", line)
        if m and cur:
            pkt.setdefault(m.group(1), cur)
        m = re.search(r"public\s+([\w<>\[\], ?.]+?)\s+(\w+)\s*\{\s*get", line)
        if m:
            props[m.group(2)] = m.group(1).replace(" ", "")
        m = re.search(r"void\s+Write\s*\(\s*IBuffer\s+\w+\s*,\s*(\w+)\s+\w+\s*\)", line)
        if m:
            cls = m.group(1)
            ind = len(line) - len(line.lstrip())
            body = []
            j = i + 1
            while j < len(lines):
                L = lines[j]
                if L.strip() == "}" and len(L) - len(L.lstrip()) == ind:
                    break
                if L.strip() not in ("{", ""):
                    body.append((j + 1, L.strip()))
                j += 1
            rel = os.path.relpath(path, AG).replace("\\", "/")
            classes.setdefault(cls, (rel, i + 1, body, props))


def ag_fields(classes, cls, depth=0):
    """(field text list, token events or None when a statement is not understood)."""
    if cls not in classes or depth > 6:
        return ["?" + cls], None
    rel, ln, body, props = classes[cls]
    out, ev = [], []
    for n, st in body:
        m = re.match(r"(\w+)\s*(?:<\s*([\w.]+)\s*>)?\s*\(\s*\w+\s*,\s*(?:\([\w ]+\)\s*)?([\w.\[\]]+)", st)
        if not m:
            out.append("{%s}" % st[:40])
            ev = None
            continue
        fn, targ, arg = m.group(1), m.group(2), m.group(3)
        fld = arg.split(".", 1)[-1]
        if fn == "WriteServerResponse":
            out.append("RES")
            if ev is not None:
                ev += [("t", "4"), ("t", "4")]
        elif fn in AG_TOK:
            out.append("%s %s" % (fn[5:], fld))
            if ev is not None:
                ev.append(("t", AG_TOK[fn]))
        elif fn in ("WriteEntityList", "WriteEntity"):
            t = targ or props.get(fld, "?")
            t = re.sub(r"^(?:List|IList)<(.+)>$", r"\1", t).split(".")[-1]
            sub_f, sub_ev = ag_fields(classes, t, depth + 1)
            if fn == "WriteEntityList":
                out.append("list<%s> %s" % (t, fld))
                if ev is not None and sub_ev is not None:
                    ev.append(("list", 0, sub_ev))
                else:
                    ev = None
            else:
                out.append("%s %s" % (t, fld))
                if ev is not None and sub_ev is not None:
                    ev.append(("call", 0, sub_ev))
                else:
                    ev = None
        elif fn == "WriteMtStringList":
            out.append("list<MtString> %s" % fld)
            if ev is not None:
                ev.append(("list", 0, [("t", "S")]))
        else:
            out.append("{%s}" % st[:40])
            ev = None
    return out, ev


# IDA reads on the private copy ddon-data-t001 of the accepted PC 03040008 database (T001 report § 4), V.
_t = lambda x: ("t", x)  # noqa: E731
IDA = {
    "50.0.16": ([("call", 0x75E6E0, [("list", 0x75E6E0, [_t("1")] + [_t("1")] * 1024)])],
                "0x75E6E0: u32 count; each element Read_u8 then a 0x400-iteration Read_u8 loop (inline fixed array)"),
    "63.2.16": ([("call", 0x806610, [_t("1"), _t("1"), _t("4"), _t("4"), _t("4"), _t("4"),
                                     ("list", 0x762B40, [_t("1"), _t("4"), _t("S")])])],
                "handler 0x7D1BE0 is no function in the dump; it calls reader 0x806610 (bool u8 u32x4, list 0x762B40)"),
    "29.23.16": ([], "handler 0x7D5730 is `return 1` (8 bytes): body ignored"),
    "45.4.1": ([], "sender 0x83F5A0 (no function in the database; called from 0x87869B in sub_878650): "
                   "WritePacket(45,4,1) at 0x83F613, then cSeedServerConnection::Send: empty body"),
}
SENDER_EXTRA = {(45, 4, 1): 0x83F5A0}

# Batches (T001 report § 5): by group and shared PC structures.
BATCH = {}
for _b, _ids in {
    "B1": "62.26.16 62.12.16 62.18.1 62.18.2 62.16.16 62.14.16 62.15.16 62.20.1 62.20.2 62.22.16 62.23.16 "
          "62.24.1 62.24.2 62.33.1 62.33.2 62.34.1 62.34.2 62.35.1 62.35.2 62.40.16",
    "B2": "11.121.1 11.121.2 11.123.1 11.123.2 11.5.1 11.5.2 11.122.1 11.122.2 11.7.16 11.118.16 11.88.16 "
          "11.68.16 14.11.16 14.14.1 14.14.2",
    "B3": "62.38.16 62.39.16 62.10.1 62.10.2 62.8.1 62.8.2 62.9.1 62.9.2 62.0.1 62.0.2 62.1.1 62.1.2 62.7.1 "
          "62.7.2 62.27.16 12.5.1 12.5.2 12.9.16",
    "B4": "72.0.1 72.0.2 72.1.16 72.2.1 72.2.2 72.3.1 72.3.2 59.0.1 59.0.2 59.4.1 59.4.2 59.8.1 59.8.2 59.9.1 "
          "59.9.2 71.22.1 71.22.2",
    "B5": "70.0.1 70.0.2 60.0.2 28.24.16 28.34.1 28.34.2 28.23.1 28.23.2 24.6.16 45.3.1 45.3.2 45.4.1 45.4.2 "
          "31.53.1 31.53.2 61.2.1 61.2.2 64.0.1",
    "B6": "63.2.16 63.10.16 63.7.16 63.0.16 63.1.16 63.3.16 63.5.16 63.6.16 13.23.16 13.16.1 13.16.2 13.17.1 "
          "13.17.2",
    "B7": "50.0.16 27.10.1 27.10.2 41.8.1 41.8.2 41.5.1 41.5.2 65.3.1 65.3.2 2.5.16 29.23.16 34.0.1 34.0.2 "
          "10.14.16",
}.items():
    for _i in _ids.split():
        BATCH[_i] = _b


def main(inv_path, out_path, detail_path=None):
    with open(inv_path, encoding="utf-8") as f:
        inv = json.load(f)
    rows = [r for r in inv["rows"] if not r["covered"]]
    F, T, S, hdr = load_dump()
    s006 = {}
    with open(S006, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            s006[r["id"]] = r
    ag_ids, ag_cls, ag_pkt = ag_index()
    files = defaultdict(list)
    want = {r["id"] for r in rows}
    for d in os.scandir(RAW):
        if d.is_dir():
            for e in os.scandir(d.path):
                m = re.search(r"\.(\d+)_(\d+)_(\d+)$", e.name)
                if m and "%s.%s.%s" % m.groups() in want and not e.name.split("_", 2)[1] in ("C2L", "L2C"):
                    files["%s.%s.%s" % m.groups()].append(e.path)
    cols = ["id", "batch", "raw_name", "dir", "files", "streams", "body_min", "body_max", "pc_role", "pc_va", "pc_func",
            "pc_onpacket", "readers", "width_seq", "leaves", "lists", "indirect", "fit_ok", "fit_err", "fit_bad",
            "fit_variant", "ida_note", "s006_status", "s006_report", "s006_layout", "ag_name", "ag_packetid_line", "ag_struct",
            "ag_fields", "ag_fit", "ag_vs_pc"]
    out = []
    det = []
    for r in sorted(rows, key=lambda r: -r["files"]):
        g, i, s = (int(x) for x in r["id"].split("."))
        name = max(r["names"], key=r["names"].get)
        d = name.split("_", 1)[0]
        is_res = name.endswith("_RES") or s == 2
        stat = {"indirect": 0, "recursion": 0, "lists": 0, "funcs": set()}
        roots = []
        onp = ""
        if d == "S2C":
            t = T.get((g, i, s))
            role = "handler"
            if t:
                roots = [t["callback"]]
        else:
            role = "sender"
            roots = sorted({va for va, _ in S.get((g, i, s), [])}) or (
                [SENDER_EXTRA[(g, i, s)]] if (g, i, s) in SENDER_EXTRA else [])
        mode = "read" if d == "S2C" else "write"
        ev = []
        for va in roots:
            fr = F.get(va)
            if fr:
                for st in fr.get("strings") or []:
                    if "OnPacket_" in st["text"]:
                        onp = st["text"].split("::", 1)[-1]
            ev = events(F, va, mode, (va,), stat) if va in F else []
            break  # first root; extra senders listed in pc_va
        # readers: the root's direct callees holding codecs
        rd = [hex(e[1]) for e in ev if e[0] in ("call", "list")]
        variant = "plain"
        fo = fe = fb = 0
        fl = files[r["id"]]
        if ev:
            fo, fe, fb = fit(fl, ev, is_res and mode == "read")
            if fb and mode == "write":
                cand = list_candidates(ev)[:6]
                best = None
                for mask in range(1, 1 << len(cand)):
                    ch = {c for k, c in enumerate(cand) if mask >> k & 1}
                    ev2 = writer_lists(ev, ch)
                    o2, e2, b2 = fit(fl, ev2, False)
                    if o2 > fo and (best is None or o2 > best[0]):
                        best = (o2, e2, b2, ev2, ch)
                if best:
                    fo, fe, fb, ev = best[0], best[1], best[2], best[3]
                    variant = "writer-lists " + ",".join("%x" % c for c in sorted(best[4]))
        elif roots and roots[0] not in F:
            variant = "root not a function in the dump"
        elif roots:
            fo, fe, fb = fit(fl, [], is_res and mode == "read")
            variant = "no reads"
        else:
            variant = "no PC root"
        idanote = ""
        if r["id"] in IDA:
            ev, idanote = IDA[r["id"]]
            fo, fe, fb = fit(fl, ev, is_res and mode == "read")
            variant = "IDA read"
        x = s006.get(r["id"], {})
        ag = ag_ids.get(("G", r["id"]))
        agf, agev, agst = "", None, ""
        if ag:
            cls = ag_pkt.get(ag[0])
            if cls and cls in ag_cls:
                agst = "%s:%d (%s)" % (ag_cls[cls][0], ag_cls[cls][1], cls)
                fl_, agev = ag_fields(ag_cls, cls)
                agf = "; ".join(fl_)
            else:
                agst = "no structure"
        agfit = ""
        if agev is not None:
            a, e_, b_ = fit(fl, agev, is_res)
            agfit = "%d/%d (err %d)" % (a, a + b_, e_)
        agcmp = ""
        if agev is not None:
            agcmp = "same" if shape(agev) == shape(ev) else "differs: " + shape(agev)
        fname = F[roots[0]]["name"] if roots and roots[0] in F else ""
        out.append({
            "id": r["id"], "batch": BATCH.get(r["id"], "?"), "raw_name": name, "dir": d, "files": r["files"], "streams": len(r["streams"]),
            "body_min": r["body_min"], "body_max": r["body_max"], "pc_role": role,
            "pc_va": " ".join(hex(v) for v in roots) or "-", "pc_func": fname, "pc_onpacket": onp,
            "readers": " ".join(rd), "width_seq": render(ev), "leaves": leaves(ev), "lists": stat["lists"],
            "indirect": stat["indirect"], "fit_ok": fo, "fit_err": fe, "fit_bad": fb, "fit_variant": variant,
            "ida_note": idanote, "s006_status": x.get("status", ""), "s006_report": x.get("report", ""),
            "s006_layout": x.get("pc_layout", ""), "ag_name": ag[0] if ag else "",
            "ag_packetid_line": ("Arrowgene.Ddon.Shared/Network/PacketId.cs:%d" % ag[1]) if ag else "",
            "ag_struct": agst, "ag_fields": agf, "ag_fit": agfit, "ag_vs_pc": agcmp})
        det.append("%s %s roots=%s funcs=%d\n  %s" % (r["id"], name, out[-1]["pc_va"], len(stat["funcs"]),
                                                     render(ev)))
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for o in out:
            w.writerow({k: str(v).replace("\t", " ") for k, v in o.items()})
    if detail_path:
        with open(detail_path, "w", encoding="utf-8") as f:
            f.write("\n".join(det) + "\n")
    print("rows", len(out), "dump", hdr["input_sha256"][:16], "script", hdr.get("script_version"))


if __name__ == "__main__":
    main(*sys.argv[1:])

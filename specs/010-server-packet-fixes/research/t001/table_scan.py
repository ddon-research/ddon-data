"""010 T001: PacketId.cs of the clean clone (e2411fe8f9) against the PC 03040008 handler table and the patterns.

Inputs, read only: Arrowgene.Ddon.Shared/Network/PacketId.cs, research/03040008/ida-transfer/dumps/pc-ida.jsonl
(gitignored dump of 2022_01_29_DDO_DUMP_FIX.exe, rows kind=table and kind=function), docs/reference/packet-ids.md,
docs/reference/packet-handler-tables.md (login list).
Run: python -X utf8 -I table_scan.py
"""
import collections
import json
import re

R = "D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean/"
D = "D:/ddon-data/"
src = open(R + "Arrowgene.Ddon.Shared/Network/PacketId.cs", encoding="utf-8-sig").read().split("\n")
pat = re.compile(
    r'public static readonly PacketId (\w+)\s*=\s*new PacketId\((\d+),\s*(\d+),\s*(\d+),\s*"([^"]*)",\s*ServerType\.(\w+),\s*PacketSource\.(\w+)(?:,\s*"([^"]*)")?\)'
)
ids = []
for n, l in enumerate(src, 1):
    m = pat.search(l)
    if m:
        ids.append(dict(f=m[1], g=int(m[2]), i=int(m[3]), s=int(m[4]), name=m[5], st=m[6], src=m[7], orig=m[8], line=n))
    elif "public static readonly PacketId" in l:
        print("UNPARSED", n, l[:120])
print("declared", len(ids), collections.Counter(x["st"] for x in ids))
txt = "\n".join(src)
il = txt.index("InitializeLoginPacketIds()")
ig = txt.index("InitializeGamePacketIds()")
login = re.findall(r"AddPacketIdEntry\(packetIds, (\w+)\)", txt[il:ig])
game = re.findall(r"AddPacketIdEntry\(packetIds, (\w+)\)", txt[ig:])
print("login list", len(login), "game list", len(game))
byf = {x["f"]: x for x in ids}
print("in no list", [(x["f"], x["line"]) for x in ids if x["f"] not in login and x["f"] not in game])
print("dup in lists", [k for k, v in collections.Counter(login).items() if v > 1], [k for k, v in collections.Counter(game).items() if v > 1])
for nm, lst, st in (("login", login, "Login"), ("game", game, "Game")):
    print("wrong list", nm, [f for f in lst if f in byf and byf[f]["st"] != st])
d = collections.defaultdict(list)
for x in ids:
    d[(x["st"], x["g"], x["i"], x["s"])].append(x)
print("dup keys", [(k, [a["f"] for a in v]) for k, v in d.items() if len(v) > 1])
print("field != name")
for x in ids:
    if x["f"] != x["name"]:
        print("  ", x["line"], f"{x['g']}.{x['i']}.{x['s']}", x["f"], x["name"], x["src"])
want = {"C2S": "Client", "C2L": "Client", "S2C": "Server", "L2C": "Server"}
print("--- source vs name prefix")
for x in ids:
    w = want.get(x["name"][:3])
    if w and w != x["src"]:
        print("  ", x["line"], f"{x['g']}.{x['i']}.{x['s']}", x["name"], x["src"])
    fw = want.get(x["f"][:3])
    if fw and w and fw != w:
        print("   field/name direction", x["line"], x["f"], x["name"])
print("--- sub vs suffix")
sf = {"REQ": 1, "RES": 2, "NTC": 16}
for x in ids:
    suf = x["name"].rsplit("_", 1)[-1]
    if suf in sf and sf[suf] != x["s"]:
        print("  ", x["line"], f"{x['g']}.{x['i']}.{x['s']}", x["name"], x["src"])
    if suf not in sf:
        print("   nosuffix", x["line"], f"{x['g']}.{x['i']}.{x['s']}", x["name"], x["src"])
    if x["s"] == 1 and x["src"] != "Client":
        print("   sub1 from server", x["line"], x["name"])
    if x["s"] == 2 and x["src"] != "Server":
        print("   sub2 from client", x["line"], x["name"])
tab = {}
fn = {}
for line in open(D + "research/03040008/ida-transfer/dumps/pc-ida.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r.get("kind") == "table":
        tab[(r["group"], r["id"], r["sub"])] = r["callback"]
    elif r.get("kind") == "function":
        fn[r["va"]] = r
print("pc table keys", len(tab), collections.Counter(k[2] for k in tab), "sub!=2,16", [k for k in tab if k[2] not in (2, 16)])
gid = {(x["g"], x["i"], x["s"]): x for x in ids if x["st"] == "Game"}
print("PC record, no server id", [k for k in tab if k not in gid])
print("PC record, server says Client source", [(k, gid[k]["name"]) for k in tab if k in gid and gid[k]["src"] != "Server"])
print("PC record, server name says C2S")
for k in tab:
    if k in gid and gid[k]["name"].startswith("C2S"):
        print("  ", k, gid[k]["name"], gid[k]["line"])
print("server source Server, no PC record")
for x in ids:
    if x["st"] == "Game" and x["src"] == "Server" and (x["g"], x["i"], x["s"]) not in tab:
        print("  ", x["line"], f"{x['g']}.{x['i']}.{x['s']}", x["name"])
res = []
for k, cb in tab.items():
    if k in gid and cb in fn:
        sv = None
        for s in fn[cb].get("strings") or []:
            m = re.search(r"OnPacket_(\w+)", s if isinstance(s, str) else json.dumps(s))
            if m:
                sv = m[1]
        res.append((k, gid[k], sv))
print("handlers with an OnPacket string", sum(1 for a in res if a[2]))


def norm(n):
    out = []
    for t in re.sub(r"^(S2C|C2S)_", "", n).split("_"):
        if not out or out[-1] != t:
            out.append(t)
    return "".join(out)


print("--- OnPacket string differs from server name (duplicate words folded)")
for k, x, sv in res:
    if sv and norm(x["name"]) != norm(sv):
        print("  ", "%d.%d.%d" % k, x["name"], sv, x["line"], "PLACEHOLDER" if re.search(r"_\d+_\d+_\d+_", x["name"]) else "")
print("--- docs/reference/packet-ids.md rows against the table")
rows = re.findall(r"^\| (\d+)\.(\d+)\.(\d+) \| `(\w+)`", open(D + "docs/reference/packet-ids.md", encoding="utf-8").read(), re.M)
print("rows", len(rows))
lid = {(x["g"], x["i"], x["s"]): x for x in ids if x["st"] == "Login"}
miss = 0
nm = []
for g, i, s, name in rows:
    k = (int(g), int(i), int(s))
    t = lid if name[:3] in ("C2L", "L2C") else gid
    if k not in t:
        print("   no server id", ".".join((g, i, s)), name)
        miss += 1
        continue
    x = t[k]
    if want.get(name[:3]) and want[name[:3]] != x["src"]:
        print("   source", ".".join((g, i, s)), name, "server:", x["name"], x["src"], x["line"])
    if norm(name) != norm(x["name"]):
        nm.append((".".join((g, i, s)), name, x["name"], x["line"]))
print("no server id", miss, "name differs", len(nm))
for a in nm:
    print("   name", *a)
doc = open(D + "docs/reference/packet-handler-tables.md", encoding="utf-8").read()
lrows = re.findall(r"\b(\d)\.(\d)\.(\d+) \| `0x88", doc)
print("--- login handlers in the doc", len(lrows), "absent from server table", [r for r in lrows if (int(r[0]), int(r[1]), int(r[2])) not in lid])
print("--- login ids: server S2C without a PC login handler", [(x["g"], x["i"], x["s"], x["name"], x["line"]) for x in ids if x["st"] == "Login" and x["src"] == "Server" and (str(x["g"]), str(x["i"]), str(x["s"])) not in lrows])

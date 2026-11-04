"""010 T001: server structure, serializer and handler cross-check, client 03040008.

Reads only C# text of the clean clone at e2411fe8f9 and prints findings to stdout.
Regex over C#: a miss is a coverage gap of this script, not a statement about the code.
Run: python -X utf8 -I dispatch_scan.py
"""
import collections
import glob
import os
import re

R = "D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean/"


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


tbl = rd(R + "Arrowgene.Ddon.Shared/Network/PacketId.cs")
pat = re.compile(
    r'public static readonly PacketId (\w+)\s*=\s*new PacketId\((\d+),\s*(\d+),\s*(\d+),\s*"([^"]*)",\s*ServerType\.(\w+),\s*PacketSource\.(\w+)'
)
ids = {m[1]: dict(g=int(m[2]), i=int(m[3]), s=int(m[4]), name=m[5], st=m[6], src=m[7]) for m in pat.finditer(tbl)}


def key(f):
    return "%d.%d.%d" % (ids[f]["g"], ids[f]["i"], ids[f]["s"])


S = {}
serial = rd(R + "Arrowgene.Ddon.Shared/Entity/EntitySerializer.cs")
reg = collections.Counter(re.findall(r"^\s*Create\(new ([\w\.]+)\.Serializer\(\)\)", serial, re.M))
print("registered", sum(reg.values()), "dup", [k for k, v in reg.items() if v > 1])
for p in glob.glob(R + "Arrowgene.Ddon.Shared/**/*.cs", recursive=True):
    t = rd(p)
    for m in re.finditer(r"public\s+(?:sealed\s+)?class\s+(\w+)\s*:\s*([\w\.<>, ]+)", t):
        c, b = m[1], m[2]
        if not re.search(r"ServerResponse|IPacketStructure", b):
            continue
        rest = t[m.end():]
        im = re.search(r"PacketId\s+Id\s*(?:=>|\{\s*get\s*=>|\{\s*get\s*\{\s*return)\s*PacketId\.(\w+)", rest)
        wr = re.search(r"void Write\(IBuffer buffer, %s \w+\)(.*?)(?=public override %s Read)" % (c, c), rest, re.S)
        rr = re.search(r"public override %s Read\(IBuffer buffer\)(.*)" % c, rest, re.S)
        S[c] = dict(
            base=b.strip(),
            id=im[1] if im else None,
            file=os.path.relpath(p, R).replace("\\", "/"),
            line=t[: m.start()].count("\n") + 1,
            w=wr[1] if wr else None,
            r=rr[1] if rr else None,
            serres="ServerResponse" in b,
        )
print("structs", len(S), "server responses", sum(1 for v in S.values() if v["serres"]))
print("no id", [c for c, v in S.items() if not v["id"]][:50])
print("id field not in table", [(c, v["id"]) for c, v in S.items() if v["id"] and v["id"] not in ids and v["id"] != "UNKNOWN"])
print("Id==UNKNOWN", [c for c, v in S.items() if v["id"] == "UNKNOWN"])

byid = collections.defaultdict(list)
for c, v in S.items():
    if v["id"]:
        byid[v["id"]].append(c)
print("--dup struct per id")
for k, v in byid.items():
    if len(v) > 1:
        print(" ", k, v)

print("--unregistered structs")
for c in S:
    if c not in reg and not any(r.endswith("." + c) for r in reg):
        print(" ", c, S[c]["file"], S[c]["line"], S[c]["id"])


def nz(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


print("--class/id naming mismatch")
for c, v in sorted(S.items()):
    if not v["id"] or v["id"] not in ids:
        continue
    a = nz(c)
    b = nz(v["id"])
    if a[:3] in ("c2s", "s2c", "c2l", "l2c") and a[:3] != b[:3]:
        print("  DIR", c, v["id"], key(v["id"]), v["file"], v["line"])
    if a[-3:] in ("req", "res", "ntc") and b[-3:] in ("req", "res", "ntc") and a[-3:] != b[-3:]:
        print("  SUF", c, v["id"], key(v["id"]), v["file"], v["line"])
    ta = {x.upper() for x in re.findall(r"[A-Z][a-z0-9]*", c)}
    tb = set(v["id"].split("_")) | {"C2", "S", "L", "L2", "S2"}
    miss = ta - tb
    if len(miss) >= max(2, len(ta) // 2):
        print("  TOK", c, v["id"], key(v["id"]), sorted(miss), v["file"], v["line"])

print("--RES checks")
for c, v in sorted(S.items()):
    if not v["id"] or v["id"] not in ids:
        continue
    i = ids[v["id"]]
    if v["serres"]:
        if v["w"] is not None and "WriteServerResponse" not in v["w"]:
            print("  noWSR", c, v["file"], v["line"])
        if v["r"] is not None and "ReadServerResponse" not in v["r"]:
            print("  noRSR", c, v["file"], v["line"])
        if i["s"] != 2:
            print("  ServerResponse but sub!=2", c, v["id"], key(v["id"]), v["file"], v["line"])
    elif i["s"] == 2:
        print("  sub2 not ServerResponse", c, v["id"], key(v["id"]), v["base"], v["file"], v["line"])
    if v["serres"] and v["w"] and "WriteServerResponse" in v["w"]:
        first = re.search(r"\b(Write\w+)\(", v["w"])
        if first and first[1] != "WriteServerResponse":
            print("  WSR not first", c, v["file"], v["line"], first[1])
    if v["serres"] and v["r"] and "ReadServerResponse" in v["r"]:
        first = re.search(r"\b(Read\w+)\(", v["r"])
        if first and first[1] != "ReadServerResponse":
            print("  RSR not first", c, v["file"], v["line"], first[1])

H = {}
hf = glob.glob(R + "Arrowgene.Ddon.GameServer/**/*.cs", recursive=True) + glob.glob(
    R + "Arrowgene.Ddon.LoginServer/**/*.cs", recursive=True
)
for p in hf:
    t = rd(p)
    for m in re.finditer(
        r"class\s+(\w+)(?:\([^)]*\))?\s*:\s*(\w*(?:RequestPacketHandler|RequestPacketQueueHandler|StructurePacketHandler|PacketHandler|PingRequestPacketHandler)\w*)(?:<([^>{]*)>)?",
        t,
    ):
        srv = "Login" if "LoginServer" in p else "Game"
        H[(srv, m[1])] = dict(
            base=m[2],
            args=[a.strip() for a in (m[3] or "").split(",") if a.strip() not in ("GameClient", "LoginClient", "TClient")],
            file=os.path.relpath(p, R).replace("\\", "/"),
            line=t[: m.start()].count("\n") + 1,
            text=t[m.end():],
        )
print("handlers", len(H), collections.Counter(v["base"] for v in H.values()).most_common(12))
reg_g = re.findall(r"^\s*AddHandler\(new (\w+)(?:<[^>]*>)?\(", rd(R + "Arrowgene.Ddon.GameServer/DdonGameServer.cs"), re.M)
reg_l = re.findall(r"^\s*AddHandler\(new (\w+)(?:<[^>]*>)?\(", rd(R + "Arrowgene.Ddon.LoginServer/DdonLoginServer.cs"), re.M)
print("reg", len(reg_g), len(reg_l), "dup", [k for k, v in collections.Counter(reg_g).items() if v > 1], [k for k, v in collections.Counter(reg_l).items() if v > 1])
print("reg without class", [x for x in reg_g if ("Game", x) not in H], [x for x in reg_l if ("Login", x) not in H])
print("class not registered")
for k, v in H.items():
    lst = reg_g if k[0] == "Game" else reg_l
    if k[1] not in lst:
        print(" ", k[0], k[1], v["base"], v["file"], v["line"])

hid = collections.defaultdict(list)
unp = []
print("--pairing")
for k, v in H.items():
    lst = reg_g if k[0] == "Game" else reg_l
    if k[1] not in lst:
        continue
    a = v["args"]
    req = a[0] if a and a[0] else None
    res = a[1] if len(a) > 1 else None
    if req and req in S:
        cid = S[req]["id"]
    elif req:
        print("  reqstruct unknown", k, req)
        cid = None
    else:
        m = re.search(r"Id\s*(?:=>|\{\s*get\s*=>)\s*PacketId\.(\w+)", v["text"])
        cid = m[1] if m else None
    v["cid"] = cid
    if cid:
        hid[(k[0], cid)].append(k[1])
    else:
        unp.append(k)
    if req and req in S and S[req]["id"] in ids:
        ri = ids[S[req]["id"]]
        if ri["src"] != "Client":
            print("  handler req id source!=Client", k[1], req, S[req]["id"], key(S[req]["id"]), v["file"])
        if ri["s"] == 2:
            print("  handler on RES", k, req)
        if req not in reg:
            print("  req not registered", k, req)
        if res:
            if res not in S:
                print("  res unknown", k, res, v["file"], v["line"])
                continue
            if res not in reg:
                print("  res not registered", k, res)
            sid = S[res]["id"]
            if sid in ids:
                si = ids[sid]
                if (si["g"], si["i"]) != (ri["g"], ri["i"]) or si["s"] != 2 or ri["s"] != 1:
                    print("  MISPAIR", k[1], req, key(S[req]["id"]), res, key(sid), v["file"], v["line"])
print("no id", unp)
print("--dup handlers per id")
for k, v in hid.items():
    if len(v) > 1:
        print(" ", k, v)
print("--REQ handled by a handler that is not a request handler")
for k, v in H.items():
    if "cid" in v and v["cid"] in ids and ids[v["cid"]]["s"] == 1 and "Request" not in v["base"]:
        sends = re.findall(r"new (S2C\w+|L2C\w+)", v["text"])
        print("  ", k[1], key(v["cid"]), v["base"], v["file"], v["line"], sorted(set(sends))[:6])
print("--NTC handler of a request handler base")
for k, v in H.items():
    if "cid" in v and v["cid"] in ids and ids[v["cid"]]["s"] == 16 and "Request" in v["base"]:
        print("  ", k[1], key(v["cid"]), v["base"], v["file"], v["line"])
game_client = [f for f, i in ids.items() if i["src"] == "Client" and i["st"] == "Game"]
print("game client ids", len(game_client), "handled", sum(1 for f in game_client if ("Game", f) in hid))
print("--Structures whose Read and Write op sequences differ, no control flow")
op = re.compile(
    r"\b(?:Write|Read)(MtStringList|MtString|EntityList|Entity|UInt64Array|UInt32Array|Int32Array|ByteArray|UInt64|UInt32|UInt16|Int64|Int32|Int16|Bool|Byte|Float|Double|ServerResponse|MtArray|T)\b"
)
for c, v in sorted(S.items()):
    if v["w"] and v["r"]:
        a = op.findall(v["w"])
        b = op.findall(v["r"])
        if a != b and not re.search(r"\b(if|for|foreach|while|switch)\b", v["w"] + v["r"]):
            print("  ASYM", c, v["id"], v["file"], v["line"], a[:14], b[:14])

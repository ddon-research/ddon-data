"""010 T001: which client-reachable readers trust a count or a length, client 03040008.

Closure from the C2S/C2L structures of registered handlers through their CData entities, over the
C# text of the clean clone at e2411fe8f9. Regex: a miss is a coverage gap, not a statement about the code.
Run: python -X utf8 -I robustness_scan.py
"""
import collections
import glob
import os
import re

R = "D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean/"


def rd(p):
    return open(p, encoding="utf-8-sig", errors="replace").read()


serial = rd(R + "Arrowgene.Ddon.Shared/Entity/EntitySerializer.cs")
reg = set(x.split(".")[-1] for x in re.findall(r"^\s*Create\(new ([\w\.]+)\.Serializer\(\)\)", serial, re.M))
readers = {}
writers = {}
where = {}
for p in glob.glob(R + "Arrowgene.Ddon.Shared/**/*.cs", recursive=True):
    t = rd(p)
    for m in re.finditer(r"public override ([\w\.]+) Read\(IBuffer buffer\)\s*\{", t):
        i = m.end()
        d = 1
        while d and i < len(t):
            d += {"{": 1, "}": -1}.get(t[i], 0)
            i += 1
        name = m[1].split(".")[-1]
        readers[name] = t[m.end(): i]
        where[name] = (os.path.relpath(p, R).replace("\\", "/"), t[: m.start()].count("\n") + 1)
    for m in re.finditer(r"public override void Write\(IBuffer buffer, ([\w\.]+) \w+\)\s*\{", t):
        i = m.end()
        d = 1
        while d and i < len(t):
            d += {"{": 1, "}": -1}.get(t[i], 0)
            i += 1
        writers[m[1].split(".")[-1]] = t[m.end(): i]
print("readers", len(readers), "registered", len(reg))

gen = re.compile(r"\b(?:Read|Write)Entity(?:List)?<\s*([\w\.]+)\s*>")
print("--entity type used by a serializer but not registered (Get<T> returns null: write skipped, read consumes nothing)")
used = collections.defaultdict(set)
for name, body in list(readers.items()) + [("W:" + k, v) for k, v in writers.items()]:
    for x in gen.findall(body):
        used[x.split(".")[-1]].add(name)
for x, u in sorted(used.items()):
    if x not in reg:
        print(" ", x, sorted(u)[:6])

print("--readers that consume nothing (a list of these loops on the client's count)")
empty = set()
for name, body in readers.items():
    if not re.search(r"\bRead\w*\s*[<(]|\.Read\w*\(|\bbuffer\b", body):
        empty.add(name)
print(" count", len(empty), sorted(empty)[:40])

# handler reachable set
H = []
for srv in ("GameServer", "LoginServer"):
    for p in glob.glob(R + "Arrowgene.Ddon.%s/**/*.cs" % srv, recursive=True):
        t = rd(p)
        for m in re.finditer(r"class\s+\w+(?:\([^)]*\))?\s*:\s*\w*(?:RequestPacketHandler|RequestPacketQueueHandler|StructurePacketHandler)\w*<([^>{]*)>", t):
            a = [x.strip() for x in m[1].split(",") if x.strip() not in ("GameClient", "LoginClient", "TClient")]
            if a:
                H.append(a[0])
print("handler request structs", len(set(H)))
closure = set()
parents = {}
stack = list(set(H))
while stack:
    c = stack.pop()
    if c in closure:
        continue
    closure.add(c)
    for x in gen.findall(readers.get(c, "")):
        x = x.split(".")[-1]
        parents.setdefault(x, c)
        stack.append(x)
print("reachable readers", len(closure))

print("--cycles")
g = {c: {x.split(".")[-1] for x in gen.findall(readers.get(c, ""))} for c in closure}
seen = {}


def dfs(u, path):
    seen[u] = 1
    for v in g.get(u, ()):
        if seen.get(v) == 1:
            print("  cycle", path + [u, v])
        elif v not in seen:
            dfs(v, path + [u])
    seen[u] = 2


for c in closure:
    if c not in seen:
        dfs(c, [])

print("--reachable readers: empty element in a list")
for c in sorted(closure):
    for x in re.findall(r"ReadEntityList<\s*([\w\.]+)\s*>", readers.get(c, "")):
        if x.split(".")[-1] in empty:
            print(" ", c, "->", x, where.get(c))

print("--reachable readers: dynamic length")
dyn = re.compile(r"(Read(?:ByteArray|UInt32Array|UInt64Array|Int32Array)\(buffer,\s*([^)]+)\)|buffer\.ReadBytes\(([^)]+)\)|new\s+\w+\[\s*([^\]]+)\s*\]|for\s*\(.*?;.*?<\s*([^;]+);)")
for c in sorted(closure):
    for m in dyn.finditer(readers.get(c, "")):
        arg = next(a for a in m.groups()[1:] if a)
        if re.fullmatch(r"\s*\d+\s*", arg):
            continue
        print(" ", c, where.get(c), "::", " ".join(m[1].split())[:110])

print("--reachable readers: counted list totals")
n = 0
for c in closure:
    n += len(re.findall(r"ReadEntityList<|ReadMtArray|ReadMtStringList|ReadUInt32Array|ReadInt32Array|ReadUInt64Array", readers.get(c, "")))
print(" counted reads", n)
print("--strings: reachable ReadMtString count", sum(readers.get(c, "").count("ReadMtString") for c in closure))

print("--constructor-less null on the error path: ServerResponse with a reference property the ctor does not set")
prop = re.compile(r"public\s+(string|byte\[\]|List<[^>]+>|CData\w+|\w+\[\])\??\s+(\w+)\s*\{\s*get;\s*set;\s*\}(\s*=)?")
hits = 0
for p in glob.glob(R + "Arrowgene.Ddon.Shared/Entity/PacketStructure/*.cs"):
    t = rd(p)
    m = re.search(r"class\s+(\w+)\s*:\s*ServerResponse", t)
    if not m:
        continue
    c = m[1]
    body = t[m.end():]
    cut = body.find("class Serializer")
    head = body[:cut] if cut > 0 else body
    wbody = writers.get(c, "")
    for pm in prop.finditer(head):
        if pm[3]:
            continue
        name = pm[2]
        if re.search(r"\b%s\s*=" % name, head):
            continue
        if re.search(r"obj\.%s\b" % name, wbody) and not re.search(r"obj\.%s\s*(\?|!=|==)" % name, wbody):
            hits += 1
            print(" ", c, pm[1], name, os.path.relpath(p, R).replace("\\", "/"))
print(" total", hits)

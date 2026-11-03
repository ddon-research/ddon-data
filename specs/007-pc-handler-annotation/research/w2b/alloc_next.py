"""007 W2 T013b: call sites of the element allocators (PC sub_8BC2E0, PS4 operator_new 0xd61f30, PS4
MtMemoryAllocator::getAllocator 0xd5c780) and the args of the next two calls. Run: python -X utf8 -I alloc_next.py"""
import collections
import json

D = "D:/ddon-data/research/03040008/ida-transfer/dumps/"
for side, tgt in (("pc", 0x8BC2E0), ("ps4", 0xD61F30), ("ps4", 0xD5C780)):
    n = 0
    ex = []
    nxt = collections.Counter()
    for line in open(D + f"{side}-ida.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "function":
            continue
        cs = r.get("calls", [])
        for i, c in enumerate(cs):
            if c["target"] == tgt:
                n += 1
                el = any(a["kind"] == "element" and a.get("site") == c["site"]
                         for d in cs[i + 1:] for a in d.get("args") or [])
                nxt["element-later" if el else "no-element"] += 1
                if len(ex) < 3:
                    ex.append((hex(r["va"]), hex(c["site"]),
                               [(hex(d["site"]), d["target"] if isinstance(d["target"], str) else hex(d["target"]),
                                 d.get("args")) for d in cs[i + 1:i + 3]]))
    print(side, hex(tgt), "sites", n, dict(nxt))
    for e in ex:
        print("   ", e)

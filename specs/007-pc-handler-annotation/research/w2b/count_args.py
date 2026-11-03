"""007 W2 T013b: offline counts of the v6 call-site `args` (PC 03040008 / PS4 02020005 dumps) and the
comparison with the T012 destination table. Run: python -X utf8 -I count_args.py"""
import collections
import csv
import json

D = "D:/ddon-data/research/03040008/ida-transfer/dumps/"
T012 = "D:/ddon-data/specs/007-pc-handler-annotation/research/W2-T012-codec-destinations.tsv"


def load(side):
    sites = {}
    funcs = 0
    for line in open(D + f"{side}-ida.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "function":
            continue
        funcs += 1
        for c in r.get("calls", []):
            sites[c["site"]] = (r["va"], c)
    return funcs, sites


SITES = {}
for side in ("pc", "ps4"):
    funcs, sites = load(side)
    SITES[side] = sites
    kinds = collections.Counter()
    slots = collections.Counter()
    sites_with = 0
    elem = collections.Counter()
    objdef = collections.Counter()
    for va, (owner, c) in sites.items():
        a = c.get("args") or []
        if a:
            sites_with += 1
        for x in a:
            kinds[x["kind"]] += 1
            slots[(x["kind"], str(x["slot"]))] += 1
            if x["kind"] == "element":
                elem[(x["from"], x.get("callee"), x.get("getter") and hex(x["getter"]))] += 1
            if x["kind"] == "obj":
                objdef["def-null" if x["def"] is None else "formed"] += 1
    print(side, "functions", funcs, "call-site records", len(sites), "with args", sites_with)
    print("  by kind", dict(kinds))
    print("  obj", dict(objdef))
    print("  element", {str(k): v for k, v in elem.items()})
    print("  top slots", sorted(slots.items(), key=lambda kv: -kv[1])[:14])

pc, ps4 = SITES["pc"], SITES["ps4"]
rows = list(csv.DictReader((l for l in open(T012, encoding="utf-8") if not l.startswith("#")), delimiter="\t"))
pcseen = {int(r["pc_site"], 16): r for r in rows if r["pc_dest"] == "lea"}
ps4seen = {int(r["ps4_site"], 16): r for r in rows if r["ps4_dest"] == "lea"}
print("T012 rows", len(rows), "distinct lea sites pc", len(pcseen), "ps4", len(ps4seen))


def args_of(sites, s):
    return {str(x["slot"]): x for x in (sites[s][1].get("args") or [])} if s in sites else None


def classify_pc(s, r):
    a = args_of(pc, s)
    if a is None:
        return "site-missing"
    x = a.get("1")
    if x is None:
        return "no-slot1"
    if x["kind"] != "obj":
        return "slot1-" + x["kind"]
    loc = f"{x['arg_loc']}:{x['arg']}"
    return (f"obj off={'eq' if x['disp'] == int(r['pc_off'], 16) else 'ne'} "
            f"def={'eq' if x['def'] == int(r['pc_lea_va'], 16) else 'ne'} obj={'eq' if loc == r['pc_obj'] else 'ne'}")


def classify_ps4(s, r):
    a = args_of(ps4, s)
    if a is None:
        return "site-missing"
    x = a.get("rsi")
    if x is None:
        return "no-rsi"
    if x["kind"] != "obj":
        return "rsi-" + x["kind"]
    loc = f"{x['arg_loc']}:{x['arg']}"
    return (f"obj off={'eq' if x['disp'] == int(r['ps4_off'], 16) else 'ne'} "
            f"obj={'eq' if loc == r['ps4_obj'] else 'ne(' + loc + ' vs ' + r['ps4_obj'] + ')'}")


for name, seen, fn, good in (("PC", pcseen, classify_pc, "obj off=eq def=eq obj=eq"),
                             ("PS4", ps4seen, classify_ps4, "obj off=eq obj=eq")):
    cnt = collections.Counter()
    ex = collections.defaultdict(list)
    for s, r in seen.items():
        k = fn(s, r)
        cnt[k] += 1
        ex[k].append(hex(s))
    print(name, "T012 lea sites", dict(cnt))
    for k, v in ex.items():
        if k != good:
            print("   ", k, v[:10])

pair = collections.Counter()
for r in rows:
    a = args_of(pc, int(r["pc_site"], 16)) or {}
    b = args_of(ps4, int(r["ps4_site"], 16)) or {}
    pair[(a["1"]["kind"] if "1" in a else "-", b["rsi"]["kind"] if "rsi" in b else "-")] += 1
print("975 pairs (PC slot 1 kind, PS4 rsi kind):", sorted(pair.items(), key=lambda kv: -kv[1]))
print("0x757df5 args", args_of(pc, 0x757DF5))

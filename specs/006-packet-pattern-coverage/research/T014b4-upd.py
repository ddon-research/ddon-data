"""T014b4 helper: update rows of T014b-consumer-property-names.tsv by (struct, field[, pattern]).

Usage: python -X utf8 -I T014b4-upd.py <updates.json>
updates.json: list of {struct, field, [pattern], proposed_name, mark, basis, vas, [verdict], [force]}.
Only rows whose mark starts with 'open' change, unless force is true. Plain tab split/join, LF.
"""
import json
import sys

TSV = "D:/ddon-data/specs/006-packet-pattern-coverage/research/T014b-consumer-property-names.tsv"
ups = json.load(open(sys.argv[1], encoding="utf-8"))
with open(TSV, encoding="utf-8", newline="") as f:
    lines = f.read().split("\n")
trail = lines[-1] == ""
if trail:
    lines = lines[:-1]
rows = [ln.split("\t") for ln in lines]
ix = {h: i for i, h in enumerate(rows[0])}
counts = {}
for u in ups:
    n = 0
    for r in rows[1:]:
        if r[ix["struct"]] != u["struct"] or r[ix["field"]] != u["field"]:
            continue
        if "pattern" in u and u["pattern"] not in r[0]:
            continue
        if not u.get("force") and not r[ix["mark"]].startswith("open"):
            continue
        for k in ("proposed_name", "mark", "basis", "vas"):
            r[ix[k]] = u[k].replace("\t", " ")
        if "verdict" in u:
            r[ix["t014a_candidate"]] = u["verdict"].replace("\t", " ")
        n += 1
    counts[u["struct"] + "." + u["field"]] = n
with open(TSV, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join("\t".join(r) for r in rows) + ("\n" if trail else ""))
print(json.dumps(counts))

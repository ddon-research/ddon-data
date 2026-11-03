"""008 T001 step 1: uncovered packet ids in packets/decrypted_raw (client 03040008).

Run from D:/ddon-data:  python -X utf8 -I specs/008-remaining-packets/research/t001/inventory.py OUT.json
Stdlib only (os.scandir, re, json). Reads packets/decrypted_raw/<stream>/<n>_<NAME>_<time>.<g>_<id>_<sub>
and the `// packet-id:` lines of research/03040008/packets/*-pattern.cpp. Writes OUT.json only.

Side: raw name prefix C2L/L2C = login server ("L"), else game server ("G") (006 T001 § Method 1);
patterns take the side from their file name prefix the same way.
Body bytes = file size - 9 (header u8 g, u16 id, u8 sub, u8 source, u32); includes cipher padding (<= 15).
"""
import json
import os
import re
import sys
from collections import defaultdict

RAW = os.path.join("packets", "decrypted_raw")
PAT = os.path.join("research", "03040008", "packets")
NAME = re.compile(r"^(\d+)_([A-Za-z0-9_]+?)_(\d{4}-\d\d-\d\dT[^.]*\.[^.]*)\.(\d+)_(\d+)_(\d+)$")
PID = re.compile(r"^//\s*packet-id:\s*(\d+)\.(\d+)\.(\d+)", re.M)


def side_of(name: str) -> str:
    return "L" if name.startswith(("C2L", "L2C")) else "G"


def main(out: str) -> None:
    covered = set()
    npat = 0
    for e in os.scandir(PAT):
        if not e.name.endswith("-pattern.cpp"):
            continue
        npat += 1
        with open(e.path, encoding="utf-8") as f:
            text = f.read()
        for m in PID.finditer(text):
            covered.add((side_of(e.name), f"{m.group(1)}.{m.group(2)}.{m.group(3)}"))
    ids = defaultdict(lambda: {"files": 0, "streams": defaultdict(int), "names": defaultdict(int),
                               "sizes": [], "source": defaultdict(int)})
    nfiles = nstreams = 0
    bad = []
    for d in os.scandir(RAW):
        if not d.is_dir():
            continue
        nstreams += 1
        for f in os.scandir(d.path):
            nfiles += 1
            m = NAME.match(f.name)
            if not m:
                bad.append(f.path)
                continue
            key = (side_of(m.group(2)), f"{m.group(4)}.{m.group(5)}.{m.group(6)}")
            r = ids[key]
            r["files"] += 1
            r["streams"][d.name] += 1
            r["names"][m.group(2)] += 1
            r["sizes"].append(f.stat().st_size - 9)
    rows = []
    for (side, pid), r in sorted(ids.items()):
        rows.append({"side": side, "id": pid, "covered": (side, pid) in covered, "files": r["files"],
                     "streams": dict(r["streams"]), "names": dict(r["names"]),
                     "body_min": min(r["sizes"]), "body_max": max(r["sizes"])})
    unc = [x for x in rows if not x["covered"]]
    summary = {"raw_files": nfiles, "raw_streams": nstreams, "unparsed": bad, "patterns": npat,
               "pattern_ids": len(covered), "distinct_ids": len(rows),
               "covered_ids_captured": len(rows) - len(unc), "uncovered_ids": len(unc),
               "uncovered_files": sum(x["files"] for x in unc),
               "pattern_ids_not_captured": sorted("%s:%s" % k for k in covered
                                                  if k not in {(x["side"], x["id"]) for x in rows})}
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "rows": rows}, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])

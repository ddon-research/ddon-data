"""008 T002: fit the IDA-read C2S writer layouts (PC 03040008) against every capture of the id.

usage (from D:/ddon-data): python -X utf8 -I specs/008-remaining-packets/research/t002/fit.py
Inputs: specs/008-remaining-packets/research/t001/inventory.json (stream dirs per id) and
packets/decrypted_raw/<stream>/*.<g>_<id>_<sub>. Rule (006/T001): body from offset 9, the decode
ends within the last 15 bytes, no overrun. Integers are big-endian (nPacket::Write_u32 byte-swaps).
Layout tokens: 1/4 = u8/u32, S = MtString and C = Write_cstr (both u16 BE length + bytes, no NUL),
("L", elem) = u32 count written before the elements.
"""
import json
import os
import re
import struct
import sys

SLACK = 15
RAW = os.path.join("packets", "decrypted_raw")
INV = os.path.join("specs", "008-remaining-packets", "research", "t001", "inventory.json")

LAYOUTS = {
    "70.0.1": [("L", ["1", "4"])],
    "62.24.1": ["4", ("L", ["S", "4"]), "4", "1", "4", "4"],
    "62.10.1": ["4", ("L", ["S", "4"]), "1"],
    "12.5.1": ["4", ("L", ["S", "4"]), "4", "C"],
    "62.34.1": ["4", "1", "4", "4", ("L", ["4", "4"])],
}


class Over(Exception):
    pass


def dec(b, p, lay, rec):
    for t in lay:
        if isinstance(t, tuple):
            if p + 4 > len(b):
                raise Over("count")
            n = struct.unpack(">I", b[p:p + 4])[0]
            p += 4
            rec.setdefault("counts", []).append(n)
            if n > 5000:
                raise Over("count %d" % n)
            for _ in range(n):
                p = dec(b, p, t[1], rec)
        elif t in "SC":
            if p + 2 > len(b):
                raise Over("len")
            n = struct.unpack(">H", b[p:p + 2])[0]
            s = b[p + 2:p + 2 + n]
            p += 2 + n
            rec.setdefault("str", []).append((t, n, b"\0" in s, s.decode("utf-8", "replace")))
        else:
            p += int(t)
        if p > len(b):
            raise Over("overrun")
    return p


def main():
    with open(INV, encoding="utf-8") as f:
        rows = {r["id"]: r for r in json.load(f)["rows"]}
    total = 0
    for pid, lay in LAYOUTS.items():
        g, i, s = pid.split(".")
        suf = re.compile(r"\.%s_%s_%s$" % (g, i, s))
        files = []
        for st in rows[pid]["streams"]:
            for e in os.scandir(os.path.join(RAW, st)):
                if suf.search(e.name) and e.name.split("_", 2)[1] not in ("C2L", "L2C"):
                    files.append(e.path)
        ok = bad = 0
        counts, slack, strs = {}, set(), []
        for path in sorted(files):
            with open(path, "rb") as f:
                b = f.read()
            rec = {}
            try:
                p = dec(b, 9, lay, rec)
                good = len(b) - p <= SLACK
            except Over:
                good = False
            if good:
                ok += 1
                slack.add(len(b) - p)
                for n in rec.get("counts", []):
                    counts[n] = counts.get(n, 0) + 1
                strs.extend(rec.get("str", []))
            else:
                bad += 1
                print("  misfit", path)
        total += len(files)
        print("%s files %d (inventory %d) fit %d/%d counts %s tail %s" % (
            pid, len(files), rows[pid]["files"], ok, len(files), dict(sorted(counts.items())), sorted(slack)))
        seen = sorted({(t, n, z) for t, n, z, _ in strs})
        if seen:
            print("  strings (kind, len, has_nul):", seen)
            for t, n, z, v in sorted(set(strs))[:3]:
                if t == "C":
                    print("  cstr sample len %d: %r" % (n, v))
    print("total files", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())

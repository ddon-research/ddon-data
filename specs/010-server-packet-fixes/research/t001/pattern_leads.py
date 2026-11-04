"""010 T001: comments in the packet patterns of client 03040008 that name a server (Arrowgene) layout.

Reads packets/patterns/03040008/ only; prints matched comment lines, joined with their continuation lines.
Run: python -X utf8 -I pattern_leads.py [broad]
"""
import glob
import os
import re
import sys

root = "D:/ddon-data/packets/patterns/03040008"
files = sorted(glob.glob(root + "/*.cpp") + glob.glob(root + "/include/*.hexpat"))
word = re.compile(r"\b(server|arrowgene|ag|emulator|c#)\b|\.cs\b|\bCData\w+\.cs", re.I)
strong = re.compile(
    r"contradict|misplac|swap|wrong|reversed|\bdiffers?\b|\bdisagree|opposite|mismatch|shifted|too (short|long)|"
    r"not read|never read|no field|omits?|missing|absent|extra|instead|but the (code|client|pc)|while (the )?(pc|client|code)|"
    r"reads? .*\b(before|after)\b|\border\b|(u8|u16|u32|u64|s32|byte|width).*(server|arrowgene)|(server|arrowgene).*(u8|u16|u32|u64|s32|byte|width)",
    re.I,
)
broad = len(sys.argv) > 1
n = 0
for f in files:
    lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
    head = next((m for l in lines[:6] for m in [re.search(r"//\s*(\d+\.\d+\.\d+)", l)] if m), None)
    pid = head[1] if head else "include"
    for i, l in enumerate(lines):
        c = l.find("//")
        if c < 0:
            continue
        text = l[c + 2:].strip()
        if not word.search(text):
            continue
        j = i + 1
        joined = text
        while j < len(lines) and lines[j].lstrip().startswith("//") and j - i < 3:
            joined += " " + lines[j].lstrip()[2:].strip()
            j += 1
        if broad or strong.search(joined):
            n += 1
            print("%s\t%s:%d\t%s" % (pid, os.path.relpath(f, root).replace("\\", "/"), i + 1, joined[:420]))
print("TOTAL", n, "files", len(files))

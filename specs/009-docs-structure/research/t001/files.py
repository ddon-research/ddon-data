"""009 T001: write T001-files.tsv: every loose file or small directory with its readers, git status and proposed home.

Readers are searched by token in this repository's live files (not specs/, client/, packets data, knowledge-graph,
flags generated reports) and in the tracked files of the sibling repositories (not their specs/, client/, packets/,
recompilation/). Hand-read readers are added in EXTRA. The search prints nothing to the repository but the TSV.

usage (from D:/ddon-data): python -X utf8 -I specs/009-docs-structure/research/t001/files.py
"""
import collections
import pathlib
import re
import subprocess

TAB, NL = "\t", "\n"
SIB = {
    "ddon-explorer-server": "D:/ddon-explorer-server",
    "DDON-translation": "D:/DDON-translation",
    "ddon-hook": "C:/Users/morph/CLionProjects/ddon-hook",
    "reconstructor": "C:/ddon-dwarf-reconstructor-rust",
    "ddon-extractor": "D:/ddon-extractor",
    "ddon-ghidra-scripts": "D:/ddon-ghidra-scripts",
    "ddon-data-s1": "D:/ddon-data-s1",
    "ddon-data-s2": "D:/ddon-data-s2",
}
LIVE = ["AGENTS.md", "CLAUDE.md", "readme.adoc", ".claude", "tools", "research", "patches/README.md", ".specify/memory", ".github",
        ".gitignore", "binaries/PS4_02020005/elf-dumps/README.adoc", "binaries/PS4_02020005/elf-dumps/generate-elf-dumps.sh",
        "packets/README-decrypt-annotate-streams.adoc", "packets/decrypt-annotate-streams.sh", "packets/decrypt-export-streams.sh",
        "packets/imhex-export.sh", "packets/split-annotated.sh", "packets/statistics-commands.sh", "packets/keys/decrypt-pcapng-streams-all-in-one.sh",
        "packets/keys/dump-and-decrypt-packet-headers-manual-process.sh"]
GLOBS = ["!research/knowledge-graph/**", "!research/03040008/flags/generated/**", "!research/external/**", "!research/imhex/plbatch/build/**",
         "!research/03040008/ida-transfer/dumps/**", "!research/03040008/ida-transfer/manifest/**", "!research/03040008/packets/*-pattern.cpp",
         "!research/03040008/xfs/**", "!research/rng-race/scratch-*/**", "!research/rng-race/*.csv", "!research/rng-race/*.tsv", "!**/__pycache__/**"]

pats = sorted(p.name for p in pathlib.Path("research/03040008").glob("r*-pattern.cpp"))
s2names = {p.name for p in pathlib.Path("research/02030004").glob("*.cpp")}

# path, what, token, proposed, reason, extra readers
R = []


def add(path, what, token, prop, why, extra=""):
    R.append((path, what, token, prop, why, extra))


NOTES3 = "research/03040008/notes/"
SCR = "research/scripts/"
for n in pats:
    cls = n.split("-")[0]
    wip = "; WIP" if "WIP" in n else ""
    dup = " Same file name in research/02030004." if n in s2names else ""
    add("research/03040008/" + n, f"ImHex pattern for {cls}, client 03040008{wip}", n[:-4], "stay",
        "per-build convention research/<build>/r<Type>-pattern.cpp; no relative include; moving only the notes clears the directory." + dup)

add("research/03040008/q00030260_Hopes_Bitter_End_info_dump.txt", "quest notes with annotated packet excerpts (03040008)", "q00030260_Hopes", NOTES3 + "q00030260_Hopes_Bitter_End_info_dump.txt", "note among patterns")
add("research/03040008/q50204000-black-sword-investigation.txt", "quest investigation notes (03040008): links and findings", "q50204000-black-sword", NOTES3 + "q50204000-black-sword-investigation.txt", "note among patterns")
add("research/03040008/release-contents-research.txt", "cEndContentsManager and quest unlock notes (03040008)", "release-contents", NOTES3 + "release-contents-research.txt", "note among patterns")
add("research/03040008/release-elements.txt", "RELEASE_CONTENT_* key and message JSON excerpt (03040008)", "release-elements", NOTES3 + "release-elements.txt", "note among patterns")
add("research/03040008/quest-flag-data-source-mapping.adoc", "rough map from flag command to client file (03040008)", "quest-flag-data-source", NOTES3 + "quest-flag-data-source-mapping.adoc", "content copied to docs/reference/quest-flag-sources.md; the note may then go; flags project does not read it")
add("research/03040008/dumps/", "DTI dumps dti.csv, dti-class-name.txt (03040008)", "dti-class-name", "stay", "data directory; needs a short README; readme.adoc names DTI dumps", "knowledge-graph test test_resource_observations.py matched a wider regex, file not read (scope); ddon-hook tests/test_resource_inventory.py:203 builds its own dti.csv fixture, not a reader")
add("research/03040008/xfs/", "37 XFS txt/xml samples (03040008)", "research/03040008/xfs", "stay", "data directory; needs a short README")
add("research/03040008/packets/include/", "36 .hexpat includes", "packets/include", "stay", "packets/imhex-export.sh PATTERN_DIR/include; plbatch -I")
add("research/03040008/packets/tools/", "unk_correlate.py and its test: value correlation over JSON", "unk_correlate", "stay", "no page names it: gap, name-an-unknown-field")
add("research/03040008/packets/tests/imhex-export-select.sh", "export selection test", "imhex-export-select", "stay", "tools/check.sh:152 EXPORT_TEST")
add("research/03040008/ida-transfer/", "ddon-ida-transfer uv project, manifest, tests", "research/03040008/ida-transfer", "stay", "tools/check.sh:182 XFER_DIR; .gitignore:71-72; CLAUDE.md:52")
add("research/03040008/protections/", "README and R1-R3 reports", "research/03040008/protections", "stay", "outside reader", "ddon-hook AGENTS.md:57, docs/development/08:70, 09:206, 14:12, 15:142")
add("research/03040008/flags/", "ddon-flags, other work, dirty", "research/03040008/flags", "stay", "brief: no move; src/ddon_flags/_paths.py derives the repo root by depth (parents[2])")

add("research/01020003/", "9 ImHex patterns, build 01020003", "research/01020003", "stay", "per-build convention")
add("research/02030004/", "50 ImHex patterns plus 2 C++ traces, build 02030004", "research/02030004", "stay", "spec rule and constitution line 47; DDOn-Tools only credits it by URL", "DDOn-Tools utils/stageextractor/rstagecustom*-season2-pattern.hexpat:3 (URL comments to names that no longer exist in research/02030004); Arrowgene docs/quests/generic_quest_state_machine.md:77 links the repo root only")
add("research/PS4/ddo-launcher-important-methods.txt", "IDA pseudocode of the PS4 launcher, build not stated", "ddo-launcher-important", "research/PS4_02020005/ddo-launcher-important-methods.txt only if the build is checked; else stay", "build must be named; lone folder. Build not verified here")
add("research/bbm/BlackBitterMaze_rev2.png", "Bitterblack Maze map image", "BlackBitterMaze", "stay", "low benefit; no reader")
add("research/bbm/bbm-connected-stages.txt", "Bitterblack Maze stage links, v3.2 notes", "bbm-connected", "stay", "low benefit; no reader")
add("research/claude-vision/", "count_image_tokens.py", "count_image_tokens", "stay", "named as the script of the report by research/external-references.md:22")
add("research/claude-vision-tokens.md", "survey report for ddon-hook", "claude-vision-tokens", "stay", "outside reader", "ddon-hook docs/development/11:113, 13:91; external-references.jsonl 10 rows")
for n in (1, 2, 3):
    add(f"research/dump-season{n}-headers.sh", f"prints the first 4 bytes per extension for season {n} via absolute /d/DDON_* paths; writes season{n}headers.csv in cwd", f"dump-season{n}", SCR + f"dump-season{n}-headers.sh", "survey scripts together; absolute input paths; output in cwd")
add("research/external/", "community spreadsheets, lists and tools; MyTool.py and QuestTool.py untracked", "research/external/", "stay", "dirty other work per spec", "tools/hooks/test_guard_bash.py:187 uses research/external/flag-smasher.csx as a test string")
add("research/external-references.jsonl", "manifest of clones and documents", "external-references.jsonl", "stay", "outside reader; dirty", "ddon-hook AGENTS.md:84")
add("research/external-references.md", "format and report index", "external-references.md", "stay", "outside reader", "ddon-hook AGENTS.md:85")
add("research/find-unsupported-extensions.sh", "extension coverage against ddon-extractor; /d absolute paths", "find-unsupported", SCR + "find-unsupported-extensions.sh", "update AGENTS.md:121, readme.adoc:141, research/readme.adoc:221,260,263,302 in the same package; no relative path")
for n, w in (("gpt-java-class-prompt.txt", "Java class"), ("gpt-java-record-prompt.txt", "Java record"), ("gpt-map-deserializer-methods.txt", "deserializer")):
    add("research/" + n, f"LLM prompt: C++ to {w} for ddon-extractor (2024)", n, "research/prompts/" + n, "three loose prompts; no reader")
add("research/ida/", "decompile_func.py, private-copy.sh and its test", "research/ida/private-copy", "stay", "tools/check.sh:166, tools/hooks/guard_ida.py, CLAUDE.md:26, .claude/agents/evidence-researcher-ida.md:33; refuses paths by name")
add("research/imhex/", "plbatch project", "research/imhex/plbatch", "stay", "packets/imhex-export.sh:126-127 default PLBATCH by relative path; .gitignore:68")
add("research/jq-npc-shops.sh", "jq one-liners over client JSON; paths relative to the repo root", "jq-npc-shops", SCR + "jq-npc-shops.sh", "cwd-relative paths: run from the root, unaffected by the move")
add("research/jq-setinfo.sh", "jq and find one-liners over client JSON; paths relative to the repo root", "jq-setinfo", SCR + "jq-setinfo.sh", "as above")
add("research/knowledge-graph/", "other work, own Spec Kit project, named only", "research/knowledge-graph", "stay", "brief scope; tools/check.sh:22, guard_paths.py:31-34")
add("research/pharos/", "OOAnalyzer Docker setup", "research/pharos", "stay", "own directory; run.sh and compose relative: not checked beyond the README")
add("research/rLandInfo-example.adoc", "worked resource decoding example, 02030004 to 03040008", "rLandInfo-example", "docs/how-to/decode-a-resource-format.md (content)", "moves to a page; delete after, git history keeps it; update research/readme.adoc:193,218 (itself replaced)")
add("research/readme.adoc", "LLM-assisted resource decoding workflow", "research/README.adoc", "research/README.md (short), content to docs/how-to", "case trap: index readme.adoc, disk README.adoc, core.ignorecase true: rename in two git mv steps; AGENTS.md:126, readme.adoc:147 name README.adoc")
add("research/rng-race/", "RNG race models, scanners, lab notes (build 03040008)", "research/rng-race", "stay", "outside reader by default path", "ddon-hook tools/rng/timeline.py:48 DEFAULT_MODEL_DIR, corpus.py:50 cbcdec.exe (ignored, local), test_*.py skip without it")
add("research/textures/", "DDS pattern, two convert scripts, how-to and scratch note", "research/textures", "stay; the how-to moves to docs/how-to/convert-textures.md", "scripts use only their arguments")
add("research/validate_pattern.sh", "validates a pattern over files through imhex on PATH", "validate_pattern", SCR + "validate_pattern.sh", "update AGENTS.md:125, tools/check.sh:215 in the same package; no relative path")
add("research/wikis-and-resources.adoc", "community links", "wikis-and-resources", "docs/reference/community-resources.md (content)", "pure reference; git mv then convert")
add("research/wireshark/wireshark-ddon-tcp-postdissector.lua", "Lua postdissector draft", "postdissector", "stay", "named by readme.adoc:91 as a directory; no script reads it")
add("research/wireshark/wireshark-filters.txt", "display filters", "wireshark-filters", "stay", "as above")

add("packets/README-decrypt-annotate-streams.adoc", "patches, split, export and statistics manual", "README-decrypt-annotate", "packets/README.md (short), content to docs/", "update AGENTS.md:131, readme.adoc:167, packets/decrypt-export-streams.sh:15, statistics-commands.sh:14, research/03040008/packets/README.md:168 and any pattern README mention")
add("packets/all_packets_v03040008.txt", "279 KB packet list, 2024-05", "all_packets_v03040008", "packets/statistics/all_packets_v03040008.txt", "statistics output; no reader")
add("packets/decrypt-annotate-streams.sh", "parallel annotated dump over streams", "decrypt-annotate-streams", "stay", "dirty other work per spec; relative keys/, encrypted_streams; AGENTS.md:130")
add("packets/decrypt-export-streams.sh", "raw export over streams; cd to its dir", "decrypt-export-streams", "stay", "cd $(dirname BASH_SOURCE); relative keys/, decrypted_raw; packet-tree scripts belong at the tree top")
for k in ("c2l", "c2s", "l2c", "s2c"):
    add(f"packets/decrypted-tcp-streams-unique-{k}-packets-count.txt", f"unique {k} packet counts, output of statistics-commands.sh", f"unique-{k}-packets-count", f"packets/statistics/decrypted-tcp-streams-unique-{k}-packets-count.txt", "statistics output: update the script's outdir default (read, not changed here) and adoc:322")
add("packets/imhex-export.sh", "pattern export driver", "imhex-export.sh", "stay", "tools/check.sh:155; relative ../research/03040008/packets and ../research/imhex/plbatch; test imhex-export-select.sh")
add("packets/keys/", "decrypt-pcapng-streams-all-in-one.sh, manual header script, keys-all-in-one.csv", "keys-all-in-one", "stay", "outside reader", "ddon-hook tools/rng/corpus.py:48 DEFAULT_CSV, tear_search.py:819, test_mt_random.cpp:23; packets/decrypt-*.sh KEYS_FILE default")
add("packets/packets-missing-structure-dumps.txt", "packet types without a C# structure, statistics output", "packets-missing-structure", "packets/statistics/packets-missing-structure-dumps.txt", "statistics output")
add("packets/packets-structure-parse-failures.txt", "empty file, statistics output", "packets-structure-parse", "packets/statistics/packets-structure-parse-failures.txt", "statistics output; empty means no failure")
add("packets/split-annotated.sh", "splits dumps over 50 MiB", "split-annotated", "stay", "AGENTS.md:133; works on arguments")
add("packets/statistics-commands.sh", "writes the statistics files", "statistics-commands", "stay", "cd to its dir; outdir awk variable; AGENTS names the tree")

add("tools/check.sh", "the local gate", "tools/check.sh", "stay", "AGENTS.md; add a docs section; SMALL_TREES at line 23 lists absent plan and lacks docs")
add("tools/hooks/", "Claude Code guards and tests", "tools/hooks", "stay", ".claude/settings.json; ddon-hook ports them")
add("tools/orchestration/", "progress.py, retro.py, section.py", "tools/orchestration", "stay", "tools/check.sh:85; specs/orchestration.md")

toks = sorted({r[2] for r in R})
args = ["rg", "-F", "--no-heading", "--no-messages", "-n", "--max-columns", "400"]
for g in GLOBS:
    args += ["-g", g]
for t in toks:
    args += ["-e", t]
args += LIVE
p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
live = collections.defaultdict(set)
for line in p.stdout.split(NL):
    m = re.match(r"^(.+?):(\d+):(.*)$", line)
    if not m:
        continue
    f = m.group(1).replace("\\", "/")
    for t in toks:
        if t in m.group(3):
            live[t].add(f"{f}:{m.group(2)}")
sib = collections.defaultdict(set)
for name, repo in SIB.items():
    a = ["git", "-C", repo, "grep", "-I", "-n", "-F", "--max-depth=-1"]
    for t in toks:
        a += ["-e", t]
    a += ["--", ":!specs", ":!client", ":!packets", ":!recompilation", ":!**/testdata/**", ":!**/fixtures/**"]
    p = subprocess.run(a, capture_output=True, text=True, encoding="utf-8", errors="replace")
    for line in p.stdout.split(NL):
        m = re.match(r"^(.+?):(\d+):(.*)$", line)
        if not m:
            continue
        for t in toks:
            if t in m.group(3):
                sib[t].add(f"{name}:{m.group(1)}:{m.group(2)}")

tracked = set(subprocess.run(["git", "ls-files", "--", "research", "tools"], capture_output=True, text=True, encoding="utf-8").stdout.split(NL))
for q in ["README-decrypt-annotate-streams.adoc", "all_packets_v03040008.txt", "decrypt-annotate-streams.sh", "decrypt-export-streams.sh", "imhex-export.sh",
          "packets-missing-structure-dumps.txt", "packets-structure-parse-failures.txt", "split-annotated.sh", "statistics-commands.sh",
          "decrypted-tcp-streams-unique-c2l-packets-count.txt", "decrypted-tcp-streams-unique-c2s-packets-count.txt", "decrypted-tcp-streams-unique-l2c-packets-count.txt",
          "decrypted-tcp-streams-unique-s2c-packets-count.txt", "keys/keys-all-in-one.csv", "keys/decrypt-pcapng-streams-all-in-one.sh"]:
    tracked |= set(subprocess.run(["git", "ls-files", "--", "packets/" + q], capture_output=True, text=True, encoding="utf-8").stdout.split(NL))
st = subprocess.run(["git", "status", "--porcelain=v1", "--", "research", "tools", "packets/decrypt-annotate-streams.sh", "packets/keys"], capture_output=True, text=True, encoding="utf-8").stdout.split(NL)
dirty = [(x[:2], x[3:].strip('"')) for x in st if x]


def status(path):
    if path.endswith("/"):
        d = [s for s, q in dirty if q.startswith(path)]
        n = sum(1 for t in tracked if t.startswith(path))
        if path == "packets/keys/":
            n = 3
        if not d:
            return f"tracked ({n} files)"
        u = sum(1 for s in d if s == "??")
        return f"tracked ({n} files); dirty: {len(d) - u} modified, {u} untracked"
    for s, q in dirty:
        if q == path:
            return "untracked" if s == "??" else "dirty"
    return "tracked" if path in tracked else "not tracked"


GENERIC_SELF = re.compile(r"^(research/knowledge-graph|tools/hooks/test_|tools/hooks/.*test)")
out = pathlib.Path("specs/009-docs-structure/research/T001-files.tsv")
nread = 0
with out.open("w", encoding="utf-8", newline=NL) as o:
    o.write(TAB.join(["path", "what", "readers", "git_status", "proposed", "reason"]) + NL)
    for path, what, tok, prop, why, extra in R:
        base = path.rstrip("/")
        hits = sorted(x for x in live.get(tok, ()) if not x.startswith(base + ":") and not x.startswith(base + "/"))
        shits = [] if tok.startswith("tools/") else sorted(sib.get(tok, ()))
        parts = []
        if hits:
            parts.append(f"{len(hits)} live: " + ", ".join(hits[:8]) + (" ..." if len(hits) > 8 else ""))
        if shits:
            parts.append(f"{len(shits)} sibling: " + ", ".join(shits[:6]) + (" ..." if len(shits) > 6 else ""))
        if extra:
            parts.append(extra)
        readers = "; ".join(parts) if parts else "none found"
        nread += readers != "none found"
        o.write(TAB.join([path, what, readers, status(path), prop, why]) + NL)
print("rows", len(R), "with readers", nread)
print(collections.Counter("stay" if r[3].startswith("stay") else "move" for r in R))
print("tracked sample", len(tracked), "dirty", len(dirty), dirty[:6])

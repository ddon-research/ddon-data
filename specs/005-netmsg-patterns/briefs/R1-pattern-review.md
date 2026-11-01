005 R1 (T007): review the spec's ImHex patterns, export script and plbatch

Objective (build 03040008): an independent review of everything spec 005 built, before docs and
closing. Commits (git receipt; you cannot run git): 2a9f798b05 (nNetMsg include + 4 patterns),
2dbc15e036 + a390e0d6fb (plbatch, export script), 04418e2c4b (P5 include changes), 6d151374a5
(6.24/6.26), 2aa7c3dc46 (character/bad-status notices), fbab54ad9d (group 35 context), 3af13f7366
(selection by declared id), b9c1cd5f90 (binary save).

Review against the evidence, not against the server: `specs/005-netmsg-patterns/research/`
P1, P2, P4 (read its coordinator correction first), P5, P7. Files:
`research/03040008/packets/include/{nNetMsg,Packet,Context}.hexpat`, the packet patterns those
commits added or changed in `research/03040008/packets/`, `packets/imhex-export.sh`,
`research/imhex/plbatch/{plbatch.cpp,CMakeLists.txt,build.sh,README.md}`.

Look for, in this order:
1. A pattern field that disagrees with the report it cites (width, order, signedness, count, clamp,
   condition), or a report item marked V that no pattern implements.
2. Fit flags that can pass on a wrong layout (non-nNetMsg packets "fit" when they end within the
   last 15 bytes: where could a missing or extra field still end there?).
3. Names: a pattern or comment that names a PC packet from a PS4 number (forbidden), or that takes a
   server C# layout as evidence (forbidden; community leads only).
4. Export script and plbatch: selection by id vs name, shard handling, failure counting, temp-file
   rename, paths over 260 characters, the NaN-as-`-nan` JSON output (invalid JSON; 35.9.16).
5. AGENTS.md conventions (pattern naming, enums from debug symbols, `#pragma pattern_limit`,
   script header `set -o errexit -o nounset -o pipefail`, `command -v` checks).

Owns: nothing (read-only). Never touch any file.
Done: findings ranked by severity, each with file:line, the report line it contradicts (or the
rule), a concrete failure case, and a suggested fix; a short list of what you checked and found
correct; what you could not check. Final message: at most 80 lines.
Stop: budget 45 min of work time.
Base: ad90eda290.

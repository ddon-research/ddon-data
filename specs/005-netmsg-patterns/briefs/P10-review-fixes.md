005 P10: fix the R1 review findings

Objective (build 03040008): apply `research/R1-pattern-review.md` findings 1-10 (read it first; it
cites file:line for each). No layout in it disagrees with the reports; the fixes are evidence
hygiene, tooling and comments.

Do (commit per group):
1. Tooling (F1, F2, F9): on a failed packet in `--force` runs, remove the stale `<rel>.json` (plbatch
   and the ImHex fallback) so counts never mix runs; make invalid JSON visible: plbatch validates its
   output (the nlohmann json it already builds with) and reports `ok-nan`/`badjson` separately, or
   writes NaN/Inf as `null` behind an option (`--json-nonfinite=null`), default unchanged so output
   stays byte-identical to ImHex; the script counts them; `require` covers every external command
   (no `sed`: use bash or `sd`); `usage()` prints the env overrides; the name filter matches files only.
2. Names and evidence (F4, F5): drop the PS4 `Send_` citations in the group-2 patterns that came from
   P4's withdrawn numbering or from server names (or replace them only with a PC caller-code match
   you can cite from P5); `ONLINE_STATUS` from PS4 DWARF `nCharacter::E_ONLINE_STATUS`
   (`binaries/PS4_02020005/DDOORBIS.elf.h:97775-97788`), with 0xD marked "Season 3?, server lead".
3. Patterns (F8, F10): guard negative `len`; fix the "LOBBY_DUMMY" copy-paste comments; add the
   padding check after `len`/`OnlineStatus` to 3.3, 3.4, 6.23, 6.25 as 6.24/6.26 have it; export the
   header `source` byte check (0x00 client, 0x34 server) where the pattern knows its direction.
4. Fit-flag honesty (F3): in each non-nNetMsg pattern header and in the README, state that a fit
   within the 15-byte padding does not prove widths when the slack exceeds a field; export the
   slack (`padding` bytes) so counts can show it. Do not claim more than the reports do.
5. Records (F6, F7): bin-save comments say the bit-level walk was "not run" (or cite file, SHA-256,
   offsets if you run one); correct P4 § 2.2's SetAdditional size line (567 fixed + 2 x (4+2n);
   add a dated "corrected by P10 from R1 F7" note, do not rewrite other lines).
6. Re-export every pattern type with plbatch; counts per type (exported, failed, fit, nonfinite);
   the nNetMsg JSON must stay byte-identical unless a fix changes its output (say which).

Owns: `research/03040008/packets/**`, `packets/imhex-export.sh`, its README section,
`research/imhex/plbatch/**`, `packets/decrypted_json/**` for re-exported types, the one P4 line
(F7). Never touch: `packets/decrypted_raw/`, client/, other research; the three files staged by
other work (commit only with `-- <paths>`; large path lists via `git update-index --stdin`).
Libraries: PatternLanguage's bundled nlohmann json for validation; no new dependencies.
Done: signed commits; plbatch rebuilt and its byte-identity re-checked on the P8 samples (default
options); counts; `bash tools/check.sh --since <base>`; receipt (from git if `receipt.py` fails).
Stop: budget 90 min of work time.
Base: 7c485e935c.

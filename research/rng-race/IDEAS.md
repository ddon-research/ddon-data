# Idea ledger: decrypting captures from long-running clients

One row per idea. Status: **done** (tried, outcome recorded), **abandoned** (decided not to
pursue, with the reason), **open** (not tried yet), **blocked** (waiting on something named).
Evidence points at files in this folder unless stated. Newest decisions at the bottom of each
section; never delete a row, mark it superseded instead.

## Hypotheses about the cause

| # | Hypothesis | Status | Outcome and evidence |
| --- | --- | --- | --- |
| H1 | Later logins fail only because they sit deeper than the old tool searched (depth 15,000, seeds up to 40 s) | done: rejected | stream1 session-2 login, seed 2344, clean depth 0..1e10: no hit (`deepscan.exe`, 75 s). NOTES.md test 1. |
| H2 | The client reseeds the RNG (e.g. on returning to title) | done: rejected | Seeds 0..1,000,000 ms × depth 0..5000: no hit (`seedscan.exe`). Static: the global is seeded once (4357 static init, then the timer); no code reseeds it from its own output. NOTES.md test 2 and Reading. |
| H3 | Our xorshift model is wrong (bit width, sign, init) | done: rejected | Matches all 125 recovered keys and the 10-value seeded hook log; PS4 DWARF `MtRandom` is 4 × u32, no hidden fields. `ddon-hook` test `test_mt_random.cpp`. |
| H4 | Unlocked concurrent `nrand` calls tear the state (thread race) | done: supported | The 2022 log values 9E0D6628, 9964B803, DBB8B273 are reproduced exactly by two overlapping calls with the disassembled memory-op order (`race_model.py`, `patterns.py`). |
| H5 | Only the first login of a fresh client process decrypts | done: confirmed | keys-all-in-one.csv: in every capture only the first login (and its game-select and game keys from the same sequence) has a key; captures starting at t < 5 s were already mid-process. |
| H6 | The race happens when the login and world connections overlap (Discord, 2022) | open | Needs the live monitor: where do divergences fall relative to the key bursts? |

## Search strategies

| # | Idea | Status | Outcome and evidence |
| --- | --- | --- | --- |
| S1 | Faster clean scan (one rolling key window per seed instead of regenerating) | done | ~185 M keys/s on 32 threads with the NTT Camellia (`deepscan.c`, `seedscan.c`), versus minutes per seed range with the old tool. |
| S2 | Full 16-byte crib instead of 5 bytes | done | The first plaintext block is fully known (`01|2C 00 00 02 34` + zeros) and the second is constant. The old 5-byte check produced a false key for stream55 at 5.6e10 candidates. `crib.h`. |
| S3 | Single-race search: one torn state (14 patterns from two overlapping calls) within 20,000 calls of session 1's game key, then up to 200,000 clean calls | done: no hit | 6 captures × 5.6e10 candidates (`racescan.exe`, `single_race.log`). Either more than one race, or races outside that window. |
| S4 | Race search widened (larger windows, depth 1e8+, more patterns incl. inlined copies) | blocked | Cost grows multiplicatively; needs measured race positions and rates from the monitor (M1) to bound it. |
| S5 | Recover the post-race state from observed RNG outputs in decrypted traffic (GF(2) linear algebra, as in xorshift/V8 Math.random state recovery) | abandoned for now | No RNG outputs from the right time window are visible: the session-2 stream is what we cannot decrypt, and session-1 gameplay values are separated from the login by further races. Revisit if the monitor shows a race-free window that contains observable outputs. |
| S6 | Statistical bias in the torn states | done: reframed | Camellia ciphertext carries no information about the key, so there is no bias to read from packets. The measured race distribution can rank the search (a prior), which is part of M1. |
| S7 | Guess the key outright | abandoned | At most 2^128 reachable keys (xorshift state), ~6e22 years at 185 M/s. |
| S8 | Multi-key Camellia key schedule on AVX-512 (Zen 5) | open | The existing SIMD fork (`E:\Projects\ClionProjects`) speeds up 16 blocks under one key, which does not help; a bitsliced multi-key schedule would. Worth it once S4 has a bounded space. |
| S9 | Port the brute forcer to Rust | open | Sam's idea; same gains as S8, decide together with S8. |

## The RSA side

| # | Idea | Status | Outcome and evidence |
| --- | --- | --- | --- |
| R1 | The corrupted key reaches the server RSA-wrapped (nothilvien): break the server key | done: closed | 278 cert notices, 39 distinct 2048-bit moduli, e = 17: no small, shared (batch GCD), Fermat or Pollard p-1 factors (`collect_moduli.sh`, `rsa_checks.py`). The private keys died with the official server. |
| R2 | Håstad broadcast with e = 17 | abandoned | PKCS#1 v1.5 random padding makes each encryption of the key different. |

## Measuring the race (ddon-hook)

| # | Idea | Status | Outcome and evidence |
| --- | --- | --- | --- |
| M1 | Hook `MtRandom::nrand` without a lock, replay against a shadow generator, record races, key bursts and summaries; run the client for hours to days | blocked on a live run | Implemented and tested on the host in ddon-hook branch `rng-monitor` (feature 009, `docs/reverse-engineering/17-rng-monitor.md`). Needs Sam to deploy the DLL and run the client. |
| M2 | Disable every unrelated hook during the measurement | done | `config/rng-monitor.env` → `ddon_hook.env` enables only `mtrandom.nrand`. |
| M3 | Use the Arrowgene bot to script logins | abandoned | PR #982's bot is a headless protocol client; it never runs DDO.exe's RNG. |
| M4 | `haunt` (nothilvien's injectable tracing DLL) instead of ddon-hook | open | ddon-hook already hooks the client; haunt could help with ad hoc breakpoints if the monitor raises questions. |
| M5 | Re-run the 2022 experiment (stop server, client returns to title, log in again) against a local server with the monitor | open | Gives a known-key session-2 login to validate any search before using it on captures. |

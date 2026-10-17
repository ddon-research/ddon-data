# Camellia keys from long-running clients (RNG race)

Why captures from clients that stayed open for a long time do not decrypt, what has been tried
and what is next. Client build **03040008** (PC) unless stated.

- [IDEAS.md](IDEAS.md): every idea with its status (done, abandoned, open, blocked) and outcome.
- [NOTES.md](NOTES.md): dated lab notes with commands, inputs and counts.

## Current understanding (2026-10-17)

1. Each connection's Camellia common key is 48 calls of `alphabet[nrand() & 63]` on the global
   `MtRandom::instance` (key generators `sub_88ADD0` and `sub_849C00`); Camellia uses the first
   32 characters. The generator is xorshift128 seeded once from the millisecond timer.
2. The same unlocked generator serves about 420 gameplay call sites on several threads. Two
   overlapping calls can tear its state (the 2022 hook log is reproduced exactly by that model).
   After a tear the sequence continues from a state that no seed produces.
3. In all 822 recorded challenge packets, only the first login of a fresh client process (with
   its game-select and game keys) decrypts. Later logins fail; depth and reseeding are ruled out.
4. A bounded search over one tear near the session-1 game key found nothing in six captures, so
   either several tears happen or they happen elsewhere. Multi-day clients have an unknown seed,
   billions of calls and many tears: out of reach unless measurement shows otherwise.
5. Next step: measure the races in a live client with the ddon-hook monitor (branch
   `rng-monitor`, `docs/reverse-engineering/17-rng-monitor.md`) and size a search from the data.

## Resume here (2026-10-17 15:35)

- ddon-hook `C:\Users\morph\CLionProjects\ddon-hook`, branch `rng-monitor`: monitor implemented
  and committed (feature 009). A worker was adopting the reconstructor's practices there
  (feature 010: hooks, roles, coordination protocol, Diátaxis index, `tools/check.sh`); check
  `git log` and `specs/010-agentic-practices/tasks.md` for what landed.
- Deployed 2026-10-17: `D:\DDON_03040008\dinput8.dll` is the Zen 5 release build
  (SHA-256 `e71c454c…ead89`); the previous DLL is `dinput8.dll.bak-2026-10-17-752695bd`.
  `ddon_hook.env` is **not** placed yet, so the monitor is off and all other hooks run as before.
- Next: Sam starts a monitor run (copy `config/rng-monitor.env` to
  `D:\DDON_03040008\ddon_hook.env`), then analyse `ddon_hook_artifacts/evidence/rng_monitor.jsonl`
  here and size the search (IDEAS S4, M1, M5).
- Nothing is pushed: ddon-hook `rng-monitor` and ddon-data `claude/project-thread-7tqspy` are
  local branches. Build logs from the session are in the ignored `scratch-2026-10-17/`.

## Video of the captured sessions

`D:\ddon-longplay\ddon longplay\` holds about 88 screen recordings that match the pcaps
(`NNN - Dragon's Dogma Online N [id].mkv` plus `.info.json`; 182 GiB, up to 15 GiB and 3.5 h per
file). Use them to see what happened in game around a capture time, such as a login or a key
burst. The only clock is the Windows 7 taskbar clock, accurate to the minute. Never copy or decode a
whole file: read `.info.json` with `jq`, and take single frames with
`ffmpeg -ss <t> -i <mkv> -frames:v 1 <png>`.

## Files

| File | What it is |
| --- | --- |
| `ddonrng.py` | Python model of the generator (init, next, backwards stepping) |
| `race_model.py`, `patterns.py`, `pat2.json`, `pat2.h` | Memory-op level model of overlapping `nrand` calls; the 16 end states of two overlapping calls |
| `deepscan.c` | Clean-sequence scan from a seed or explicit state to a large depth |
| `seedscan.c` | Seed range × depth scan (the old tool's job, faster) |
| `racescan.c`, `run_single_race.sh`, `single_race.log` | Single-tear search and its run on six captures |
| `mkcase.c` | Builds a synthetic single-tear case to self-test `racescan` |
| `cbcdec.c` | Camellia-256-CBC decryption with the DDON IV, for checking hits |
| `crib.h` | The 16-byte known plaintext check shared by the scanners |
| `collect_moduli.sh`, `moduli.csv`, `rsa_checks.py` | Server RSA public keys from the captures and the weakness checks |
| `failed_with_seed.tsv` | Failed challenge packets from captures whose seed is known |

Build the scanners with MinGW and OpenMP, using the NTT Camellia from
`D:\research\ddon_common_key_bruteforce\src`:

```bash
gcc -O3 -march=native -fopenmp -I/d/research/ddon_common_key_bruteforce/src deepscan.c /d/research/ddon_common_key_bruteforce/src/camellia.c -o deepscan.exe
```

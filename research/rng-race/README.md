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

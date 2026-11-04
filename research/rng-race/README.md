# Camellia keys from long-running clients (RNG race)

Lab tools and notes on why captures from long-running clients do not decrypt, client build 03040008 (PC) unless stated. The account of what is known and what is open is [RNG race](../../docs/explanation/rng-race.md). ddon-hook carried the work on and closed it with a negative result on 2026-10-19, and reads files here by path, so they stay.

- [IDEAS.md](IDEAS.md): every idea with its status and outcome at 2026-10-17. ddon-hook's `hypotheses.md` continues it.
- [NOTES.md](NOTES.md): dated lab notes with commands, inputs and counts.

## Files

| File | What it is |
| --- | --- |
| `ddonrng.py` | Python model of the generator (init, next, backwards stepping) |
| `race_model.py`, `patterns.py`, `pat2.json`, `pat2.h` | Memory-op level model of overlapping `nrand` calls; the 16 end states of two overlapping calls |
| `deepscan.c` | Clean-sequence scan from a seed or explicit state to a large depth |
| `seedscan.c` | Seed range × depth scan (the job of `ddon_common_key_bruteforce`, faster) |
| `racescan.c`, `run_single_race.sh`, `single_race.log` | Single-tear search and its run on six captures |
| `mkcase.c` | Builds a synthetic single-tear case to self-test `racescan` |
| `cbcdec.c` | Camellia-256-CBC decryption with the DDON IV, for checking hits |
| `crib.h` | The 16-byte known plaintext check shared by the scanners |
| `collect_moduli.sh`, `moduli.csv`, `rsa_checks.py` | Server RSA public keys from the captures and the weakness checks |
| `failed_with_seed.tsv` | Failed challenge packets from captures whose seed is known |

`single_race.log` and the `*.exe` builds are local (gitignored). Build a scanner with MinGW and OpenMP, using the NTT Camellia from `D:\research\ddon_common_key_bruteforce\src`:

```bash
gcc -O3 -march=native -fopenmp -I/d/research/ddon_common_key_bruteforce/src deepscan.c /d/research/ddon_common_key_bruteforce/src/camellia.c -o deepscan.exe
```

## Video of the captured sessions

`D:\ddon-longplay\ddon longplay\` holds about 88 screen recordings that match the pcaps (`NNN - Dragon's Dogma Online N [id].mkv` plus `.info.json`; 182 GiB, up to 15 GiB and 3.5 h per file). They show what happened in game around a capture time, such as a login or a key burst. The only clock is the Windows 7 taskbar clock, accurate to the minute. Never copy or decode a whole file: read `.info.json` with `jq`, and take single frames with `ffmpeg -ss <t> -i <mkv> -frames:v 1 <png>`.

# Long-session stream decryption: RNG race investigation (2026-10-16)

Scratch folder. Inputs read only: `packets/keys/keys-all-in-one.csv`,
`D:\research\ddon_common_key_bruteforce`, IDA 9.3 export
`D:\research\DDON-binaries\IDA9.3\PC_DDON_03040008\2022_01_29_DDO_DUMP_FIX.exe.c`,
radare2 disassembly of `D:\research\DDON-binaries\PC\2022_01_29_DDO_DUMP_FIX.exe` (PC 03040008).

## Facts (PC 03040008)

- Global RNG `dword_21E720C` (x,y,z,w + 1 dword). `rng_next` = `sub_13B5E10`; `sub_5A07D0` is a
  second accessor on the same object. ~420 references to the global in the decompiler export:
  gameplay code (`% 100`, `& 1`, `% 0x2710`, ...) shares it with the key generator.
- Key generator `sub_88ADD0` (`cNetLoginServer::clientChallenge` per Discord) draws **48** chars
  `alphabet[rng_next(&global) & 0x3F]`; Camellia uses the first 32.
- Default seed 4357 (0x1105) via `sub_4C8FE0`; seeding = `sub_4C9000`.
- `sub_13B5E10` memory-op order (disassembly 0x13B5E10..0x13B5E3D), no lock:
  `R x; R y; R w; R x (again); W x<-y; R z; W y<-z; W z<-w; W w<-result`.

## Captures (keys-all-in-one.csv, 822 rows, 125 keys)

- In every capture only the **first login of the client process** decrypts, together with its
  game-select and game keys (same seed, depths ~250 / ~1500-1700 / ~1850-2100). Every later login
  in the same process fails. Captures whose first login is at t<5 s were started mid-process and
  have no key at all.
- stream82 shows two logins + game-select in one title phase, all on the clean sequence: the title
  phase is race-free in the data.

## Tests

1. Clean deep scan, stream1 session-2 login, seed 2344, depth 0..1e10: no hit (`deepscan.exe`,
   75 s). Not a depth problem.
2. Reseed hypothesis: seeds 0..1,000,000 ms x depth 0..5000: no hit (`seedscan.exe`, 31 s).
3. Race model check against the 2022 Discord hook log (c:1229 DCD16E4E, reference sequence
   DCD16E4E 0BCF94BF 4E7A444A C300DFC9): game outputs 9E0D6628 = g(s-3, s-1),
   9964B803 = g(s-2, s0), DBB8B273 = g(s-2, 9E0D6628). All three are explained by two overlapping
   `sub_13B5E10` calls with the op order above (`race_model.py`, `patterns.py`): a torn read gives
   [s-3, s-2, s-1, s-1] and the final state is a mix like [s-2, s-1, s-1, s0].
   Two overlapping calls produce 16 end states, 2 of them clean (incl. lost update = duplicate).
4. Single-race search (`racescan.exe`, `run_single_race.sh`, log `single_race.log`): six session-2
   logins (stream1, 4, 5, 7, 55, 61), race position p = session-1 game key depth + 48 .. +20,000,
   14 torn patterns, then 0..200,000 clean calls: 5.6e10 candidates each, ~5 min each at
   ~185 M keys/s (32 threads, NTT Camellia). No genuine hit. stream55 gave one hit
   (p=15327 pattern 11 depth 65183) that matched the old 5-byte crib only; decrypting the packet
   showed garbage after byte 5, a false positive.
5. Crib: the first plaintext block of the challenge response is fully known
   (`01|2C 00 00 02 34` + 11 zero bytes) and the second block is constant across captures
   (`0010108979eed698ad50785502ccb988`). `ddon_common_key_bruteforce` checks only 5 (login 9)
   bytes, which produces false positives once searches reach ~1e10 candidates. All tools here now
   compare the whole 16-byte block (`crib.h`).

## Reading (PS4 02020005 DWARF/export, reconstructor output)

- `struct MtRandom { u32 mRandomX, mRandomY, mRandomZ, mRandomW; }`, global
  `MtRandom::instance` (0x25FE770, size 0x10): no lock member. PC `dword_21E720C` is the same object.
- `MtRandom::nrand` = Marsaglia xorshift128 with shift triple (15, 4, 21); `MtRandom::init` is
  Capcom's 100-round seed mixer (default seed 4357; seeded once from the main timer). Our
  implementation matches all 125 known keys and the 10-value seeded hook log.
- No code re-seeds the global from its own output: PC references to the global are `rng_next`
  (`sub_13B5E10`), the float wrapper `sub_5A07D0`, and the static init with 4357.
- `ddon-dwarf-reconstructor-rust` output lists 93 inlined copies of `MtRandom::nrand` on PS4.
  Inlined copies on PC can have their own memory-op order, so the other racing thread may tear the
  state in patterns not covered by `pat2.h` (which models two `sub_13B5E10` calls).

## Cost model

candidates = (race positions) x (patterns ~14 per race) x (clean depth), multiplied per extra race.
At ~185 M/s: 1e11 ~ 9 min, 1e13 ~ 15 h. A multi-day client has seen ~1e9+ gameplay calls from
~420 call sites before its first captured login, and its seed is unknown: even with zero races
that is 6e4 seeds x 1e9+ depths, and every race multiplies the space.

## Next steps (need Sam)

- Measure, don't guess: hook `sub_13B5E10` in ddon-hook (thread id, return address, state
  before/after; flag when the state before differs from the last state after) through
  login -> game -> logout -> login against a local server. That gives calls/second in game, which
  threads call it, and how often and where races happen, which decides if a bounded search can work.
- If races cluster (e.g. around connection setup), aim racescan at those windows with larger depth
  and a SIMD Camellia; otherwise the long-session captures are not recoverable from the RNG side.

## 2026-10-17: RSA side and monitoring plan

- RSA (nothilvien's point: the corrupted CommonKey reaches the server RSA-wrapped). The
  L2C_LOGIN_SERVER_CERT_NOTICE uses the fixed default Camellia key, so every server public key is
  readable (`collect_moduli.sh` -> `moduli.csv`): 278 notices, 39 distinct 2048-bit moduli,
  e = 17. No small factors (< 2e5), no shared factors between any pair (batch GCD), no Fermat hit
  (|p - q| small), no Pollard p-1 hit (B = 1e5) (`rsa_checks.py`, 63 s). Only the dead official
  server holds the private keys, so that side is closed; PKCS#1 v1.5 random padding also rules
  out Hastad broadcast with e = 17.
- Guessing: the key is 32 chars of 6 bits drawn from xorshift128, so at most 2^128 keys are
  reachable (not 63^32 or 64^32). 2^128 at 185 M/s is ~5.8e22 years: only structure (few races,
  known positions) makes a search feasible.
- The Arrowgene bot from PR #982 is a headless protocol client (removed before the merge), so it
  cannot exercise the real client's RNG; it could only script the server side.
- `E:\Projects\ClionProjects\ddon_common_key_bruteforce` (SIMD fork): camellia-simd-aesni speeds up
  16 blocks under **one** key; our search needs one key schedule per candidate, so a
  multi-key (AVX-512/GFNI, Zen 5) key schedule is what would help.
- Monitor design (not built, needs Sam): hook `sub_13B5E10` without a lock and keep a shadow
  xorshift. On entry: state == shadow -> clean; state == shadow advanced k steps -> k calls from
  inlined copies; anything else -> corruption event (log thread, return address, old shadow, new
  state, time; classify against `pat2.h`), then resync. Count calls per thread and caller per minute.
  Run idle and active in game for hours, plus logout/login cycles like the captures.

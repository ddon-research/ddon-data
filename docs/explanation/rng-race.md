# RNG race

Why captures from long-running PC 03040008 clients do not decrypt, and why they stayed undecrypted after a dedicated attempt. It is for a reader who wants to decrypt captured sessions, or who meets a stream with no key. You need the [wire protocol](wire-protocol.md) first, for what a session key is. This page states the understanding as of 2026-11-04. Its source is ddon-hook's closed investigation of 2026-10-19 (`ddon-hook/specs/013-prng-state-recovery/whitepaper.md`, with `hypotheses.md` beside it, at commit `36a61a6`), and the first steps in `research/rng-race/NOTES.md` and `IDEAS.md`. Those two stop at 2026-10-17; where they differ, this page follows the later source. Its labels are the whitepaper's: verified, inferred, open.

## The short answer

Each connection's key comes from a generator that gameplay threads share without a lock. The first login of a client process sits a few hundred draws after a known kind of seed, so a search finds its key. After that, the generator's state breaks away by itself, permanently, onto a sequence no seed produces. Each break multiplies the search, and a gap of minutes holds more breaks than any search can pay for. No capture was recovered. The investigation closed with a negative result on 2026-10-19, with the questions below still open.

## How a key is drawn (verified)

The common key is 48 calls of `alphabet[nrand() & 63]` on the global `MtRandom::instance` (`0x21E720C`, in key generators `sub_88ADD0` and `sub_849C00`), and Camellia-256 uses the first 32 characters. What the last 16 feed is open, probably nothing. `MtRandom` is four 32-bit words with no lock member (PS4_02020005 DWARF); `nrand` (`sub_13B5E10`) is Marsaglia xorshift128 with shifts (15, 4, 21). The model reproduces all 125 recovered keys of the 822 challenge packets in `packets/keys/keys-all-in-one.csv`.

Seeding is `init(seed)`, 100 mixing rounds. The static initializer uses 4357; 10 to 14 s after process start the game calls `init(0)` and then `init(seed)` twice, with `seed` the milliseconds since about process start. No later `init` appears in any lab run.

The first login's key sits at a depth of about 250 after that seed, the game-select key at about 1,500 to 1,700 and the game key at 1,850 to 2,100. That is why only those three decrypt in every capture, and why a capture started mid-process has no key at all: 449 of the 697 targets have no known key earlier in their process, so nothing to start from.

## Why later logins fail

A peer's first guesses were tested and fail:

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| Later logins are only deeper | rejected | clean depth to 1e10 finds nothing |
| The client reseeds | rejected within the searched depths | all 2^32 seeds at every burst depth to 12,000 (login) and 8,000 (game-select, game), against all 697 targets, with 125 known keys and 3 planted keys found as controls |
| The model is wrong | rejected | 125 keys, and the exact end states of the breaks |
| The monitor causes the breaks | rejected for the bulk | 43 breaks in 800.9 s with a read-only sampler that suspends nothing |
| Breaks are long clean walks | rejected | none joins within 2^40 steps |
| One call seen half way | rejected | no break is a one-call intermediate, and none returns |

What happens instead is a **tear** (verified as a fit, its mechanism inferred). One `nrand` is nine memory operations with no lock, `R x, R y, R w, R x, W x, R z, W y, W z, W w`, so another thread's call can run between any two. Of 43 breaks in the one run with a full timeline, 38 are exactly the end state of one **slow call**, whose first load of `x` is one or two draws older than its other loads. The state it writes lies on another orbit of the generator, so the break is permanent. This refines the notes' first model of two overlapping calls, which reproduced the 2022 hook log: of the same 43, 12 are two-call end states and 26 three-call ones.

Lab rates are 0.008 to 0.067 tears per second, in bursts. In a run of 800 s, 22 breaks lay between the first game key and the second login key, and none between a login key and its game key or inside a key burst. So a later login sits behind many tears, while a login's game-select and game keys do not.

The generator has no other writer that the database shows: all 345 references to `0x21E720C` in the `f1c9` database are `mov ecx, offset` before a call, 299 to `nrand`, 35 to the float accessor, 1 to `init`, 10 not followed. The start-up `init` calls themselves are invisible to cross references. A count over a decompiler export, such as the "about 420 call sites" in `research/rng-race/NOTES.md`, is not tied to the database.

## Why a search cannot pay for it

A key search must guess each tear's position and spread and the burst's start. For N clean steps and k tears with spreads {1, 2}:

```text
candidates(N, k) ≈ N^(k+1) · 2^k / (k+1)!
```

A candidate costs one Camellia-256 key schedule and one block, and neighbouring keys share nothing. The cipher offers no shortcut, since a known plaintext gives only a yes or no per candidate. Measured on a Ryzen 9 9950X3D: 208 M candidates/s with the reference code at 32 threads, 12.5 G/s with the GPU and AVX-512 engines together.

At 12.5 G/s, k = 2 takes minutes for a gap of 40 s and 20 minutes for 80 s; k = 3 takes 24 days for 40 s and about a year for 80 s, and more for the wider tear families. Only a second login within about a minute of a known key can hold few enough tears, and 12 login targets of the 697 are that close. The searches that ran on real captures found no key:

| Search | Targets | Candidates | Key found |
| --- | --- | --- | --- |
| k ≤ 1, spreads {1, 2} | 37 logins, 40.6 to 277.5 s after a known key | 3.1e11 | none |
| k = 2, spreads {1, 2} | 3 of the shortest gaps | 4.8e12 to 1.7e13 each | none |
| k = 1, wide spreads (to 5,000) and split reads | the same 3 | 6e11 to 2e12 each | none |
| k = 2, 14 narrow forms | `stream49@10588` | 1.53e14 | none |

These are real negatives only because every run also found keys it had to find: known and planted keys in the same run. A hit counts only when the following packets decrypt, since a 5-byte crib gave a false key for stream55 at 5.6e10 candidates; the tools compare a whole 16-byte block (`research/rng-race/crib.h`).

The server's RSA side is closed too: 39 distinct 2048-bit moduli with e = 17 show no small, shared, Fermat or Pollard p-1 factor, the padding rules out Håstad's broadcast attack, and the private keys ended with the official server. The monitor could not hook `nrand` either, since a code patch [crashes the client](client-lineage-and-protections.md#why-a-code-patch-crashes-the-client); it reads the state from outside.

## What is open

These are the questions at the close of the investigation, 2026-10-19; nothing has run on them since that date.

- **Why the real captures fail at k ≤ 2.** Three explanations remain: more than two tears in the real gaps, a tear family the real machines produced and the lab does not, or a start state other than the clean one after the last known key. A lab replay of one real gap measured 0.45 tears per gap, with no spread above 2, but it under-sampled the in-world phase: its second key is the game-select key, while the real client has the world at its game key. A corrected pass was planned and not run.
- **The cause of the rate.** It is about a thousand times what chance overlap of two 20 ns calls gives, and the thread that writes a tear is unknown.
- **Five of the 43 breaks** fit no form, among them the two start-up reseeds.
- **PC inlined copies of `nrand`.** PS4_02020005 has 93. Their count and memory-op orders on PC were not established.
- **Whether the real clients' rate equals the lab's.** It is inferred near 0.05 per second, from twelve real re-logins that all failed the clean search.

More machine time on the same model is not expected to help. What would reopen it is evidence of another kind: the capture machines' thread behaviour, a pair of captures with a known first login and a second login within about 20 s, or a client-side writer of the generator.

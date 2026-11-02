# 006 T002c: why the 1.0.1 C2L_CLIENT_CHALLENGE_REQ raws are still ciphertext

Brief: `specs/006-packet-pattern-coverage/briefs/T002c-challenge-decrypt.md`. Observed at ddon-data
HEAD `707ef3594c0` (brief base `5421fdf867`; no `packets/` change between them). Captures:
2019 PC client traffic in `packets/encrypted_streams/` that this feature reads as build **03040008**.
Static code: Arrowgene Upstream clone
`C:/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream` at `e2411fe8`
(the build that `packets/decrypt-export-streams.sh:32` runs; its `PacketFactory.cs` and `Packet.cs`
are byte-identical to the fork `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline` `88d82caf`, and its
`PacketCommand.cs` differs only by the debug log at lines 143-146). PS4 **02020005**:
`binaries/PS4_02020005/DDOORBIS_2.elf.c`, `DDOORBIS.elf.h` (working-tree copy; the `.h` is dirty).
V = verified here, I = inferred.

## Answer in brief

- The first packet in each direction of every login (and game) connection is Camellia-256-CBC
  encrypted with a **fixed key compiled into the client**, `f23e98HafJdSoaj80QBjhh23oajgklSa`, and
  IV `$cbM6WP)aX=%J^zA`. The session key in `keys/keys-all-in-one.csv` applies only from the
  second packet on. (V: PS4 code, Arrowgene code, and a trial decrypt of all 84 files.)
- The CLI keyed both of its decoders with the session key before the first packet, so it decrypted
  these two packets with the wrong key. It then named both of them `C2L_CLIENT_CHALLENGE_REQ` 1.0.1,
  because its decoder calls the first packet in either direction that, and it writes them without
  a header. (V: code and a byte-exact rerun of all 84.)
- The 304-byte file is **not** a C2L packet. It is the server's first packet, its RSA public key:
  modulus[256], exponent padded to 16, SHA-1[20], 12 unknown bytes. The 336-byte file is the real
  C2L_CLIENT_CHALLENGE_REQ: the 324-byte body with **no 9-byte header**, padded to 336. (V, 42/42 each.)
- The plaintext can be recovered completely from the captures. The fix is a small patch to the
  CLI's `PacketCommand.cs` (first packet per direction on the static key, then the session key),
  then a re-export of the affected files. The same defect affects 166 `C2S_CERT_CLIENT_CHALLENGE_REQ`
  44.0.1 raws in the 83 game and game-select streams (V).

## 1. How the packet is encrypted on the wire

Wire framing (V, Arrowgene `PacketFactory.cs:207-223`, `:321-345`; `Camellia.cs:68-110`): a u16
big-endian length, then a Camellia ciphertext of that length. The mode is CBC with a **fresh copy of
the fixed IV for every packet** (`Util.Copy(CamelliaIv)` at `PacketFactory.cs:328,341`). The key is
256 bits (`CamelliaKeyLength = 32*8`, `:32`).

Key per packet:

| Packet | Key | Evidence |
| --- | --- | --- |
| Server's first packet (public key, 304 B) | static `f23e98HafJdSoaj80QBjhh23oajgklSa` | Arrowgene: `PacketFactory` ctor keys the static key (`PacketFactory.cs:18-22,53`); `Client.InitializeChallenge` sends `CreateClientCertChallenge()` through `WriteDataWithLengthPrefix`, a raw body with no header (`Client.cs:180-195`, `Challenge.cs:44-56`), on connect (`DdonLoginServer.cs:58-61`). V by trial (SHA-1 check, § 4). |
| Client's first packet (C2L_CLIENT_CHALLENGE_REQ, 336 B) | same static key | PS4 02020005 `cSeedServerConnection::Send` (`0x55BB80`, `DDOORBIS_2.elf.c:948919`) and `::analyzePacket` (`0x55AEE0`, `:948386`): if `mGuardData.mCommonKey[0] == 0`, `cCamellia::setKeyBytes(.., "f23e98HafJdSoaj80QBjhh23oajgklSadrhogh2IJnwJEF58", 256)` (`:948488,948988`), so only the first 32 characters are used, with IV `"$cbM6WP)aX=%J^zA"` (`:948475,948494,948991`). Otherwise the key is `mCommonKey` (first 32 bytes, `:948462-948473`). `cGuardData { char mCommonKey[49]; bool mIsEnableCipher; }` (`DDOORBIS.elf.h:73207-73211`). The same key string is in `elf-dumps/strings/strings-rodata.rebased.tsv:26465` at `0x1f20ef2`. V by trial. |
| Every later packet (from 1.0.2 RES on) | session common key (32 ASCII characters, the CSV `decryption_key`) | Arrowgene: the server decrypts the RSA blob and calls `SetCamelliaKey` (`Client.cs:212-222`, `Challenge.cs:80-100`). The key search finds this key from the first 96-byte RES (`decrypt-pcapng-streams-all-in-one.sh:46`: `data.len eq 98 && data contains 00:60`; expected plaintext `0100000234000000` = header 1.0.2, `:81`). V: the RES raws decode (T002 § 4, 42/42). |

Inside the client challenge (V, layout; I, semantics): `CommonKeyEnc` is the session key
RSA-PKCS#1-encrypted with the server's public key from the 304-byte packet (Arrowgene
`Challenge.cs:69,91`). The server's private key is not in the captures, so the RSA blob itself
cannot be decrypted, and it does not need to be: the session key is already in the CSV. Observed
`CommonKeySrcSize` = **48** in 42/42 login and 83/83 game captures, while Arrowgene's own client
sends 32 (`Challenge.cs:142`). Together with `mCommonKey[49]` (PS4), this suggests the client
generates a 48-character key and Camellia uses its first 32 (I). `PasswordEnc` is the fixed
password `0123456789abcdef` (Arrowgene `Challenge.cs:14`), Blowfish-ECB with key
`mofumofu capcom(^-^)` in little-endian word order (`BlowFish.cs:508-511`, compat mode,
`Challenge.cs:23`). V: decrypts to exactly that string in 42/42 login captures.

Arrowgene is code-confirmed here only where PS4 code or the wire trial agrees: the static key/IV, the
headerless first packet, the 1+256+3+1+1+62 body (`C2LClientChallengeReq.cs` Read/Write) and the
public-key packet layout. Its `PacketSource.Client` label for the server's first packet
(`PacketFactory.cs:251`) is wrong for capture replay; see § 2.

## 2. How the pipeline produced these raws and their names

1. `packets/keys/decrypt-pcapng-streams-all-in-one.sh` finds the session key per TCP stream from
   the first 98-byte server segment, which is the 1.0.2 RES (`:13-24,46,81`), and dumps the stream
   with `tshark -z follow,tcp,yaml` (`:33`) into `encrypted_streams/<capture>_tcp-stream-N.yaml`.
2. `packets/decrypt-export-streams.sh:65-82` looks up the key and runs
   `Arrowgene.Ddon.Cli packet <yaml> --key=<key> --export-decrypted-packets` (Upstream build).
   The bruteforce and split binaries in `D:/research/DDON-pcaps` (`ddon_common_key_bruteforce.exe`,
   `ddon_pcap_split.exe`) ship without source, so steps 1-2 are traced from the scripts only.
3. `PacketCommand.DecryptPackets` (`PacketCommand.cs:69-72`) creates one `PacketFactory` per
   direction, then **immediately** calls `SetCamelliaKey(sessionKey)` on both. This overwrites the
   static key the constructor set (`PacketFactory.cs:53`). **This is the bug** (V).
4. In each factory, `_firstPacket` starts as true (`PacketFactory.cs:54`). Its first packet is taken
   without header parsing and named by server type alone: `C2L_CLIENT_CHALLENGE_REQ` for login,
   `C2S_CERT_CLIENT_CHALLENGE_REQ` for game, `PacketSource.Client`, count 0
   (`PacketFactory.cs:229-254`). The factory does not know its direction, so the **server's**
   first packet gets the same name and source.
5. The file name `<pcap>_<Id.Name>_<ts>.<group>_<id>_<sub>` (`PacketCommand.cs:92-94`) gives
   `.1_0_1`. The content `GetHeaderBytes() + Data`: `GetHeaderBytes()` returns an empty array for
   exactly these two ids (`Packet.cs:29-35`), so the files hold only the body. They are
   ciphertext decrypted with the wrong key, with no header.

V by rerun: for all 84 files, Camellia-CBC decrypting the wire body (YAML) with the CSV session key
reproduces the raw byte for byte (84/84; game: 166/166).

The header check in T002 § 3 (`01 0000 01 00`) cannot pass even after the fix, because the first
packet carries no header (§ 4).

## 3. The 304 / 336 split

| Size | Count | Direction (YAML peer) | What it is |
| --- | --- | --- | --- |
| 304 | 42 | server → client (port 52100 side), the first packet of the stream in 42/42 | Server public key: `modulus[256]`, `exponent[16]` (= `0x11`, big-endian, left-padded with zeros in 42/42), `SHA1(modulus‖exponent)[20]` (matches in 42/42), `unknown[12]` (differs in every capture, sometimes plain-looking data, so probably uninitialised memory; I). 304 = 19×16, so no padding. Not a C2L packet; Arrowgene has no `PacketId` for it. |
| 336 | 42 | client → server, after the 304 in 42/42 | C2L_CLIENT_CHALLENGE_REQ body (324 B) plus 12 bytes of CBC block padding. The padding is not zeroed: 13 distinct tails, e.g. `0000004c006f006700690074` ("Logit" in UTF-16). |

So 336 = 324 + 12, not 9 + 324 + 3 (the T002 § 3 guess). The 304-byte file is a different packet in
the other direction, not a retry. All 125×2 first packets arrive in their own TCP segments
(wire length = length field + 2 in 250/250), so no later packet shares a segment with them.

Contradiction for T002 § 3 (open, I): the PC writer `0x88a900` calls `WritePacket(p, 1, 0, 1, -1)`
as if it had a header, but the wire body starts at `CommonKeySrcSize` (byte 0 = `0x30`) in 42/42.
The header is evidently not sent for this packet. The mechanism (the first-packet path of
`Send`/`analyzePacket`) was not traced, PC or PS4.

## 4. Trial on two files (scratchpad only)

Script `C:/Users/morph/AppData/Local/Temp/claude/D--ddon-data/584d9d84-927d-466f-adf6-d1c15549c007/scratchpad/t002c/trial.py`
(sha256 `70517659f18d8d0f…`), run with
`research/knowledge-graph/.venv/Scripts/python.exe -B -X utf8 -I trial.py D:/ddon-data/packets <scratch>/out`.
It uses the `cryptography` package already installed in that environment (Camellia-CBC, Blowfish).
The password and RES-echo check is `check2.py` (`ebdd01898f0dbcbb…`); the game variant is
`trial_game.py` (`57f5f386fd942580…`). The script reads `packets/` only and wrote nothing there.
Input: `encrypted_streams/stream1-marked.pcapng_tcp-stream-33.yaml` (sha256 `d457b64499600534…`).

| File (stream1 tcp-stream-33) | Current raw | Static-key plaintext, first 16 bytes | Result |
| --- | --- | --- | --- |
| `11756_…1_0_1`, 304 B | `b3f2 d2bb 7f82 af19 6c78 4b7f c18d 1419` (`9eeb40a9d8fd5adf…`) | `c5df 75a5 eba5 b226 6347 f402 3e03 8b19` (output sha256 `87cdeb1b54743716…`) | Not `01 0000 01 00` and not meant to be: it is a modulus. Exponent `…0011` at 0x100; SHA-1 at 0x110 matches the modulus and exponent. The public-key layout fits exactly. |
| `11758_…1_0_1`, 336 B | `135b 767f f6e0 19de 00a4 5525 9d4a 5bd5` (`c489c6ce2add5064…`) | `3007 6301 8b82 38c9 979f 4e6d 3c9e facd` (output sha256 `7cc99c2cd0588a1f…`) | No header (`01 0000 01 00` absent, by design). The body fits the 324-byte layout: `CommonKeySrcSize=0x30`, `CommonKeyEnc[259]` = 256 RSA bytes + `000000`, `PasswordSrcSize=0x10`, `PasswordEncSize=0x10`, `PasswordEnc` = `8979eed698ad50785502ccb988aec988` + 46 zero bytes, then 12 padding bytes. |

Across all captures (same run):

- Login: 42/42 server SHA-1 OK; 42/42 client `0x30 / 000000 / 0x10 / 0x10`; 42/42 passwords decrypt
  to `0123456789abcdef`.
- 42/42 `L2C_CLIENT_CHALLENGE_RES` raws repeat the client's `PasswordSrcSize, PasswordEncSize,
  PasswordEnc[16]` at offset 17. This independently confirms the body offsets, and it agrees with
  T002 § 4 (`u8, u8, u8[62]`).
- Game and game-select (`*.44_0_1`): 83/83 SHA-1 OK, 83/83 client `CommonKeySrcSize` 48, 166/166
  current raws equal the session-key decrypt.

## 5. The fix

Not applied: `packets/` and the Arrowgene clones are outside this package.

1. **CLI patch** in the Upstream clone, as one more uncommitted patch next to those listed in
   `README-decrypt-annotate-streams.adoc` § arrowgene-patches. In `PacketCommand.DecryptPackets`,
   stop keying the factories up front (delete `:71-72`). After each factory's first decoded packet,
   switch it to the session key:

   ```csharp
   bool serverKeyed = false, clientKeyed = false;   // factories start on the static key (PacketFactory ctor)
   ...
   pcapPacket.ResolvedPackets = clientFactory.Read(pcapPacket.Data);
   if (!clientKeyed && pcapPacket.ResolvedPackets.Count > 0) { clientFactory.SetCamelliaKey(camelliaKeyBytes); clientKeyed = true; }
   // same for serverFactory / serverKeyed
   ```

   This is safe for these captures because every first packet sits alone in its segment
   (250/250, § 3). A sturdier variant would switch the key inside `PacketFactory.Read` right after
   `_firstPacket = false` (`:253`), through a pending-key setter.

   Optional naming patch: for `Source == Server`, re-label the first packet, e.g.
   `L2C_CLIENT_CHALLENGE_KEY` / `S2C_CERT_CLIENT_CHALLENGE_KEY`. That name is invented: neither PC
   nor PS4 names this packet in the evidence read here. `GetHeaderBytes()` must still return empty
   for it (`Packet.cs:31-35` compares ids). Without this patch the file names stay as they are, and
   only the bytes change.
2. **Rebuild** (`dotnet build Arrowgene.Ddon.Cli/Arrowgene.Ddon.Cli.csproj -c Debug`, as in the
   README), then export to a scratch folder, because the script refuses existing stream folders
   (`decrypt-export-streams.sh:73-77`):
   `OUT_DIR=<scratch>/raw ./decrypt-export-streams.sh encrypted_streams/*.yaml` (or only the 42
   login YAMLs).
3. **Verify, then replace only the changed files.** Expect every other file under `<scratch>/raw`
   to be byte-identical to `decrypted_raw/`. Expect exactly the 84 `*.1_0_1` (and 166 `*.44_0_1`)
   files to differ, with unchanged names and sizes (304/336), the first 16 bytes as in § 4, and the
   SHA-1 / password / RES-echo checks passing. Then copy those files into `decrypted_raw/<stream>/`.
   Scope: 84 login files (+166 game files if included); nothing else in `decrypted_raw/` changes.
   `decrypted_annotated/` (125 files mention these packets, e.g. `stream1-…-33`, lines 1 and 26,
   both labelled `Client`) also shows the wrong-key hex. They would change on a re-annotation with
   `decrypt-annotate-streams.sh` and the patched CLI. `decrypted_json/` is unaffected unless a
   pattern is exported for 1.0.1.
4. **Pattern consequence for T002/T003:** a 1.0.1 pattern must read the body from offset 0 with no
   header (`u8; u8[259]; u8; u8; u8[62];` then padding). The 304-byte server packet needs its own
   pattern or none.

Alternative without a CLI rebuild: a stdlib/`cryptography` script equivalent to `trial.py` could
write the 250 files directly from the YAMLs. It reproduces the CLI's other 146,641 outputs nowhere
and adds a second producer for `decrypted_raw/`, so the CLI patch is the recommended path (I).

## Checks not run

- No CLI rebuild or export run (outside the brief); the CLI was not executed.
- RSA blob not decrypted (the server's private key is not in the captures). The 48-versus-32 key
  length is inferred.
- PC 03040008 static-key location not checked in IDA. The PC-side claim rests on the PC captures
  decrypting with it (V for the wire) and on PS4 02020005 code.
- The first-packet header skip in the PC writer `0x88a900` path was not traced (§ 3 contradiction).
- ImHex not run (not on `PATH`).

## Errata (R1, 2026-11-02)

Appended after the R1 review of T002-T004; the sections above stay as written.

- **§ 3, the 304-byte packet.** "`unknown[12]` (… probably uninitialised memory; I)" and "304 =
  19×16, so no padding" are wrong: the body is 292 bytes (`u8 OpenModulo[256]; u8 OpenExpo[16];
  u32 OpenHash[5]`), and its last 12 bytes are cipher block padding (292 + 12 = 304). Source: T003
  § 1 (b) and § 15 (PC reader `0x801a80` reads 0x100 + 0x10 + 5×4 bytes, V). The packet is the
  server's certificate notice, filed since T002e as 1.1.16 L2C_LOGIN_SERVER_CERT_NTC (login) and
  44.1.16 S2C_CERT_GAME_SERVER_CERT_NTC (game).

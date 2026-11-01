006 T002c: why the 1.0.1 C2L_CLIENT_CHALLENGE_REQ raws are still ciphertext (research)

Objective (build 03040008): all 84 raws named `*_C2L_CLIENT_CHALLENGE_REQ_*.1_0_1` under
`packets/decrypted_raw/` (two per login stream, 42 x 304 B and 42 x 336 B) fail the header check:
e.g. `…/11758_C2L_CLIENT_CHALLENGE_REQ_…1_0_1` (336 B) starts `135b 767f f6e0 …` instead of
`01 0000 01 00`. The PC writer (`specs/006-packet-pattern-coverage/research/T002-login.md` § 3)
writes a 324-byte body (u8, u8[259] RSA-encrypted common key, u8, u8, u8[62]). Find out:

1. How this packet is encrypted on the wire and with what key (the login key search in
   `packets/keys/` uses expected plaintext `0100000234000000`, i.e. the 1.0.2 RES, and is bounded),
   from the toolchain sources and Arrowgene's login server (`D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline`:
   `Arrowgene.Ddon.LoginServer`, `Arrowgene.Ddon.Server/Network` packet factory / Camellia setup,
   `Arrowgene.Ddon.Cli` decrypt command). Arrowgene is a lead; say what is code-confirmed.
2. How the pipeline produced these raw files and their names (it named them 1.0.1 although the bytes
   do not decode): `packets/keys/decrypt-pcapng-streams-all-in-one.sh`,
   `packets/decrypt-export-streams.sh`, `packets/decrypt-annotate-streams.sh` and their README
   (`packets/README-decrypt-annotate-streams.adoc`); the toolchain under `D:/research/DDON-pcaps`
   (`ddon_pcap_split`, `ddon_common_key_bruteforce`). Why two sizes (304 vs 336 = 9 + 324 + 3)?
   Are the 304-byte ones a different packet or a different state (e.g. a retry)?
3. Whether the plaintext is recoverable from what the captures hold (keys in `packets/keys/`,
   the 1.0.2 key, the stream's first bytes), and the exact fix: which script or CLI step, the
   command, and what it would rewrite. Try it on 2 streams in the scratchpad only (never in
   `packets/`): decrypt one 336-byte and one 304-byte file and show the first 16 bytes and whether
   the header reads `01 0000 01 00` and the body fits the 324-byte layout.

Owns: only `specs/006-packet-pattern-coverage/research/T002c-challenge-decrypt.md`. Never write to
`packets/`, client/, patterns. Read-only on the sibling repos and `D:/research/DDON-pcaps`
(clones are reference: never build them; running the existing CLI binaries on scratch copies is fine).
Libraries: the existing CLI and scripts; stdlib Python (e.g. `cryptography` only if a project env
already has it) for the scratch trial.
Done: § how it is encrypted (citations), § how the files were made, § the 304/336 split, § trial
result on 2 files, § the fix (command, scope: 84 files, what changes). Final message: report path +
at most 15 lines. Stop: budget 60 min of work time; finish the scope.
Base: 5421fdf867.

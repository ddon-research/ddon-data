# 010 T006: what the branch itself says, before a push

Server clone `fix/packet-handling` at `b8be1e19`, read only here. The body of `pr-body.md` keeps to what the server does. A push also publishes the commit messages and the code comments, and those do not. Nothing was changed in the clone: a rewrite is the coordinator's or Sam's decision (it changes hashes, as the fixture rewrite did).

This file names no value and no reproduction, since it may become public with this repository.

## Commit messages that say more than the pull request body

| Commit | Subject | What goes |
| --- | --- | --- |
| `ef78efed` | Register the serializers for CDataOcdImmuneLv and CDataSwitchStorage. | The sentences on the count, the memory measurement and login. **The worst of the set**: it is a whole recipe in three lines |
| `1808826b` | Close a connection whose stream can not be followed, and keep split frames. | The paragraph on what a bad length did to the buffer and the kick path |
| `e90e78a6` | Bound the lengths a client supplies and the frames a server sends. | The values and what each did, in the first paragraph; the sentence on the size in the second |
| `f8683307` | Close the session after a failed challenge. | The sentences on what a session could reach after a failure. The sentence on a key "that is not 32 bytes" is also **wrong at the head**: the check is under 32, since the client encrypts 48 |
| `da7322d6` | Cap an MtString at what the client can read, and write null as empty. | The sentence on which text is relayed and who a player could disconnect |

18 lines of the 29 messages also carry this spec's task ids and row labels, which mean nothing to a reader of that repository.

## Proposed bodies

Each keeps the client evidence and says what the server does.

`ef78efed`:

```text
Neither had a Create line, and WriteEntity and ReadEntity returned silently with no serializer, so a list
wrote its count and no elements. Both are registered, and an entity with no serializer now throws.

A new test decodes the IL of every registered serializer and fails if an entity one of them looks up has no
serializer. It is green, so no live path relies on the silence. Serializers nothing registers are not walked:
they cannot run from a packet. The element layout {u8, u8} agrees with PC 03040008 0x76fc20; CDataSwitchStorage
is checked against capture 10.13.16.
```

`1808826b`:

```text
A TCP split inside a length prefix, or right after the prefix of a 16-byte frame, lost the place in the stream
and desynchronised the session. The state already holds the place, so the rewind goes and the Reset waits for a
whole frame.

A frame length under 16 or not a multiple of 16, a bad source byte, or anything else thrown out of Read now closes
the connection. Read reports these through ReadFailed, with the packets decoded before them, and Client drops
what follows. Sources 0 and 0x34 are both still accepted on either direction, as 63.11.16 needs. The CLI ignores
ReadFailed: it keeps reading as it does today, and a length that is not a multiple of 16 no longer ends its run.
```

`e90e78a6`:

```text
The s32 lengths in 3.3.16, 6.23.16 and 6.25.16 are checked against the bytes left, and a bad one reads as a short
packet does everywhere else. A real length is unaffected: the padding stays in the buffer, so it always fits.

The padding of 1.0.2 and 44.0.2 can not go negative. Logging a malformed packet with LogIncomingPacketStructure on
is caught per packet, and the handler then answers as it would with the setting off.

The frame size check counts the padded frame, so a body near the limit is refused before it uses a counter, and
null never reaches SendRaw. PC 03040008 has no frame limit below the u16 (0x9d6d69).
```

`f8683307`:

```text
The key is now set only on success, and a failed challenge throws a critical error, so one RES goes out under the
fixed key and the connection closes. A session key under 32 bytes counts as a failure: Camellia's schedule takes 256
bits, and the client encrypts 48 and ciphers with the first 32 (PC 03040008 0x88aecd, 0x88afbb; 48 on 125 of 125
first frames). The game handler marks the challenge complete after the check; its RES is allowed either way, so
the bytes do not change.

The good path is pinned by a test that walks it: the 304-byte certificate with a correct hash, the headerless
request, the 96-byte response, then a normal packet under the new key. That test also passes on develop.
```

`da7322d6`:

```text
PC 0x8bc5b0 takes a length up to 0x800 and otherwise fails the read, so the cap stays one below that, at 0x7FF.
Truncation stops on a UTF-8 boundary. The writer in EntitySerializer now calls the extension, so the rule sits in
one place. Null writes length 0, as the client's writer does.
```

## Code and tests on the branch

| File | What | Proposal |
| --- | --- | --- |
| `Arrowgene.Ddon.Test/Shared/Entity/SerializerRegistrationTest.cs` | The comment above `A_huge_list_count_ends_at_the_end_of_the_data` measures the fault and names a task id. The test body sets the bytes | Drop the comment's second half. The body shows the shape to anyone who reads the diff, as does the fix; whether that test stays public is Sam's call |
| `Arrowgene.Ddon.GameServer/Handler/ClientChallengeHandler.cs`, `Arrowgene.Ddon.LoginServer/Handler/ClientChallengeHandler.cs` | The comment "the session would otherwise go on under the fixed key" | Say what it does: `// Critical: a failed challenge closes the connection.` |
| `Arrowgene.Ddon.Test/Server/Network/ClientSuppliedLengthTest.cs` | Test names and cases name the hostile lengths | Leave, or decide with the test above |

# Write a packet pattern

This page is for anyone taking a packet id of client 03040008 to a pattern, its marks, a re-export and a fit count. You need [plbatch built](build-plbatch.md), a read-only way into the PC database ([which one](../reference/packet-handler-tables.md#which-database-to-read-them-in)) and the [marks](../reference/packet-marks.md). [Read one packet by hand](../tutorials/read-one-packet.md) shows the result on a small packet, and [Packet decoding method](../explanation/packet-decoding-method.md) says why the steps run in this order. The example throughout is 14.3.2.

## 1. Check the id

1. Look for the id in [Packet ids](../reference/packet-ids.md). If it has a row, change that pattern rather than adding one.
2. List its raw files:

   ```sh
   fd -d 2 -t f -g '*.14_3_2' packets/decrypted_raw | wc -l
   ```

   No file means no capture can test the pattern: state that in its row as `no capture`. If the name prefixes differ (`C2L_`/`C2S_`), two servers share the id, and each gets its own pattern with `// packet-select:` ([Header comment](../reference/packet-pattern-format.md#header-comment)).

## 2. Find the PC code

| Direction | Where | Example |
| --- | --- | --- |
| S2C on the game server | a record of the [directory](../reference/packet-handler-tables.md#game-server-the-directory), and its handler | the row below |
| L2C on the login server | a [login list](../reference/packet-handler-tables.md#login-server-the-lists) | 1.1.16 is handler `0x886b00`, which IDA shows as `dd` data until you disassemble it ([which handlers](../reference/packet-handler-tables.md#login-server-the-lists)) |
| C2S or C2L | the [`WritePacket` site](../reference/packet-handler-tables.md#senders) with this key | 14.11.16 is writer `0x840080` |

With the local dump, the handler of an S2C packet is one line of `jq` (decimal VAs):

```sh
jq -c 'select(.kind=="table" and .group==14 and .id==3 and .sub==2)|{record_va,callback,proved}' research/03040008/ida-transfer/dumps/pc-ida.jsonl
```

```text
{"record_va":34799256,"callback":8385920,"proved":true}
```

8385920 is `0x7ff580`. Open it in the database, and follow it to the function that calls the `nPacket::Read_*` codecs: here reader `0x81dc00`.

## 3. Decide what the layout rests on

| The code shows | Then | Mark of the layout |
| --- | --- | --- |
| a reader or writer | walk it in call order and note each codec's width; read the pushes in disassembly, not the pseudocode | `V` |
| a handler that reads nothing, as 29.23.16 | the captures alone give the shape, and every field stays a guess | `G` |
| no code found | stop and record it in [Packet open questions](../reference/packet-open-questions.md) | none |

For a RES, the reader's first calls are the [RES header](../reference/packet-wire-format.md#res-header), written as the guard. Then look for what else can check the walk:

- **PS4 02020005:** match by code (callers, strings, data read), never by packet number. A match gives DWARF member names and, where the recompilation has a `ReadPacket` or `WritePacket` body, the argument order. A disagreement goes back to the PC code.
- **Server C#:** `Arrowgene.Ddon.Shared/Entity/PacketStructure/` gives a name to test, never a width. The [marks page](../reference/packet-marks.md#the-marks) says how a server name may be used.

## 4. Decide where the structure goes

| Case | Place |
| --- | --- |
| A body of plain fields | in the pattern |
| An element or structure with its own PC reader that another packet also calls | in the include for that group, listed in [Packet pattern includes](../reference/packet-includes.md) |
| The reader is already in an include | look it up by VA, and use that structure: `rg -n '0x76f820' packets/patterns/03040008/include` |
| A structure only this packet needs, whose name an include also uses | rename it: a pattern's local type must not share a name with a type of its includes |

## 5. Write the file

Create `packets/patterns/03040008/<packet name>-pattern.cpp`, named after the name the raw files carry. The whole of `packets/patterns/03040008/S2C_WARP_WARP_RES-pattern.cpp`, with the standard fit comment shortened:

```cpp
// 14.3.2 S2C_WARP_WARP_RES (client 03040008).
// Evidence: specs/006-packet-pattern-coverage/research/T008-warp-item.md
// section 2.3.
// PC handler 0x7ff580, reader 0x81dc00: RES header, u32, u32 (V). PS4 OnPacket_S2C_WARP_RES
// 0x2f7190: u32 m_unWarpPointID, u32 m_unrim (V). Walk: 44/44 fit, slack 7.
// Body: s32 Error [, s32 Result, u32 WarpPointID, u32 Rim] (16 bytes).
// packet-id: 14.3.2
// Fit flag `fits`: ...
#pragma endian big

import std.mem;

#include "Packet.hexpat"

struct S2C_WARP_WARP_RES : CPacket {
    bool sourceOk = source == 0x34 [[export]];  // header source byte: 0x34 server (Packet.hexpat)
    s32 Error;
    if (Error == 0) {
        s32 Result;
        u32 WarpPointID;
        u32 Rim;
    }
    // Fit: the decode ends within the last 15 bytes (cipher block padding; Packet.hexpat).
    u128 paddingSize = std::mem::size() - $ [[export]];
    bool fits = paddingSize <= 15 [[export]];
    if (paddingSize > 0) padding[paddingSize];
};

S2C_WARP_WARP_RES packet @ 0x00;
```

- The lines the format requires are in [Packet pattern format](../reference/packet-pattern-format.md). Copy the fit comment and the last four lines of the struct from a neighbouring pattern.
- A first packet of a direction has no header: it does not use `CPacket` or `sourceOk`, as `packets/patterns/03040008/C2L_CLIENT_CHALLENGE_REQ-pattern.cpp` shows.
- Carrier packets use `NetMsg<len>` and also export `msgFits`, as `packets/patterns/03040008/S2C_PARTY_RECV_BINARY_MSG_NTC-pattern.cpp` shows.

Give every field a mark, in a [form the marks page lists](../reference/packet-marks.md#comment-forms), and keep `unk_*` where no basis holds. To earn a name later, see [Name an unknown field](name-an-unknown-field.md).

## 6. Export and count

1. Export by the pattern's own id line:

   ```sh
   packets/imhex-export.sh --force @ S2C_WARP_WARP_RES
   ```

   Success is `0 failed` and `0 badjson` on the last line. For the failures, see [When a packet fails](export-packets-to-json.md#when-a-packet-fails).

2. Count the fit:

   ```sh
   fd -d 2 -t f S2C_WARP_WARP_RES packets/decrypted_json -x jq -r .packet.fits | sort | uniq -c
   ```

   ```text
        44 true
   ```

   Any `false` means the layout is wrong or a variant is missing. A row of only `true` does not prove the widths ([what a fit proves](../explanation/packet-decoding-method.md#what-a-fit-proves)), so also look at the `paddingSize` values and at a few decoded values against what they should be.

3. Add the row to [Packet ids](../reference/packet-ids.md) with its report label and any marks, by a script or a one-line edit, then correct the counts and run the check:

   ```sh
   python -X utf8 tools/docs_check.py --packet-counts --write
   uv run --offline --no-project --with markdown-it-py==4.2.0 python -X utf8 tools/docs_check.py
   ```

## 7. After an include changes

Re-export every pattern that includes it, directly or through another include, and make sure each one still compiles. A clash between an include's type and a pattern's local type breaks that pattern without any file of that pattern changing, so a test of the pattern you worked on does not see it.

1. List the includers. Save this as a script outside the repository and run it from the repository root with the include's name:

   ```python
   import re, sys
   from pathlib import Path

   root = Path("packets/patterns/03040008")
   users = {}
   for p in [*root.glob("*-pattern.cpp"), *root.glob("include/*.hexpat")]:
       for inc in re.findall(r'^#include "(.+?)"', p.read_text(encoding="utf-8"), re.M):
           users.setdefault(inc, []).append(p)
   todo, seen = [sys.argv[1]], set()
   while todo:
       for p in users.get(todo.pop(), []):
           if p not in seen:
               seen.add(p)
               if p.suffix == ".hexpat":
                   todo.append(p.name)
   print("\n".join(sorted(p.name[:-len("-pattern.cpp")] for p in seen if p.suffix == ".cpp")))
   ```

   For `EntryBoard.hexpat` it prints the 5 patterns of 34.1.1, 34.1.2, 34.2.1, 34.2.2 and 34.14.16.

2. Export each name as in step 6. A compile error fails every file of that pattern. A clash reads `Compilation failed` and `error: Type with name 'CDataCommonU32' has already been declared.` in the `.err`; rename the local type.

3. **A pattern with no capture is not compiled by an export**, since no file selects it. Compile those through plbatch on a stand-in file of 16 zero bytes. The stand-in is no valid packet, so exit status 1 is normal: read the `.err` beside the output. `Array size cannot be negative`, which this example gives, comes from evaluation, so the pattern compiled.

   ```sh
   t=$(mktemp -d); mkdir "$t/in"; head -c 16 /dev/zero > "$t/in/x"
   echo x | packets/plbatch/build/bin/plbatch.exe --pattern packets/patterns/03040008/S2C_PARTY_RECV_BINARY_MSG_NTC-pattern.cpp \
     -I "$IMHEX_INCLUDES" -I packets/patterns/03040008/include --in-root "$t/in" --out-root "$t/out"
   sed -n 1p "$t/out/x.json.err"
   ```

   `IMHEX_INCLUDES` is the std library folder of the [imhex-export CLI](../reference/imhex-export-cli.md#environment).

4. Check the result by prediction: [Verify a regeneration](verify-a-regeneration.md).

## What done looks like

- The pattern has its header comment and a mark on every field.
- Its JSON exists, with `0 failed`, and every file's `fits` is true.
- Its row is in [Packet ids](../reference/packet-ids.md), and `tools/docs_check.py` reports `0 findings`.
- Where the annotated dump disagrees, the PC code decided it, and the server's version stands in a comment: see [Two packet decodings](../explanation/two-packet-decodings.md).

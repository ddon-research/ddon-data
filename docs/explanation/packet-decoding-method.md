# Packet decoding method

This page is for anyone reading a [pattern](../reference/glossary.md#packets)'s [marks](../reference/glossary.md#evidence-marks) or writing one: why the packet patterns of client 03040008 are built from the client's readers and only tested on captures, what the [fit](../reference/glossary.md#packets) check can and cannot say, and how a value in a capture may support a name. Read [Evidence model](evidence-model.md) first for the wider reasoning. The steps are in [Write a packet pattern](../how-to/write-a-packet-pattern.md) and the rules in [Packet evidence marks](../reference/packet-marks.md).

## Reader first

The client's reader of a packet is the format. It consumes bytes in a fixed order, with fixed widths, and the code states both. Starting there means a pattern can be written before any capture is looked at, and the captures become a test of it.

A peer would start from the bytes: decrypted traffic is plentiful, and a structure can often be read off it. That is how a guess is formed where no reader exists, and the marks say so. As a method for layouts it fails on what captures cannot show. A list that is always empty in the captures has no visible element. A u16 and two u8s look the same. A field that is always 0 can be any width the neighbouring fields allow.

The client sometimes reads nothing at all: a handler can return without touching the body. Then the capture shape is the only source, and every field stays at `G`. That is a statement about the evidence, not a failure of the method.

## What a fit proves

A decode fits when it ends within the last 15 bytes of the file, without running past the end. The check is this loose because of the wire: the plaintext has no length, and padding runs up to 15 bytes ([why](wire-protocol.md#why-the-plaintext-has-no-length)).

So a fit shows that a layout is not too long and not more than a block too short, and nothing else.

- It cannot see a width error smaller than the padding. A field dropped from the end still fits if the slack had room.
- It cannot see order at all. Two same-width fields fit identically in either order.
- It says little on short packets, where a single 16-byte file admits many bodies.
- Agreement over many captures adds less than it seems to, because the captures of one packet tend to share a size.

A failed fit is strong: some layout claim is false for that capture. That asymmetry decides how the check is used. It is a filter that catches errors, run on every export, and it never raises a mark. A full tree with every packet fitting says that no decode overran its file and no more.

The nNetMsg patterns can do better, because their `len` states the end exactly. There a wrong width usually breaks the walk, so the width changes between PS4 02020005 and PC show clearly in that layer.

## Value bases

When code gives a width but no meaning, values can suggest one: this field holds what looks like item ids. Such arguments deceive easily, in two ways that the rules guard against.

**Repetition is not evidence.** A headline like "every capture matches" may be one list sent again and again. So a value basis counts distinct values, since repeated captures of one value are one observation.

**Dense tables match anything.** Most integers in the observed range are valid item ids, since the item table is nearly full, so a field of arbitrary small numbers "matches" it with high probability. The chance rule therefore computes what luck would give: the table's density over the observed range, to the power of the distinct count. A high chance, or very few distinct values, means the value shows nothing, and the mark stays at `G`. The thresholds are on [the marks page](../reference/packet-marks.md#value-bases).

An independent structural basis, such as the same reader as a known structure, comes first and survives without this arithmetic.

## Why PS4 numbers never name PC packets

PS4 02020005 numbers packets as a flat u16 in its send functions, and PC 03040008 uses `group.id.sub`. The temptation is an offset table: anchor a few known pairs and interpolate within a group. It looks right often enough to be believed, and it is unsound, because the two schemes were never the same and Season 3 inserted packets. A name reached that way is a name for some other packet.

So a pairing goes through code: the PC's own diagnostic string in the handler, or a PC caller matched to a PS4 symbol by callers, strings and data read. [Packet handler tables](../reference/packet-handler-tables.md#names) gives the PC sources. Wire layouts read from PC code are not affected, since they never needed the number.

## Why IDA can misorder stack arguments

On 32-bit x86 the writers take many values through the stack, and a decompiler rebuilds those arguments by tracking the stack pointer. That reconstruction can attribute or order them wrongly, and the pseudocode then reads with full confidence. For a packet writer, the order of arguments is the order of fields, so the error lands directly in a layout.

Two things check it. The disassembly's pushes are the program, so widths and order are read there and not from the pseudocode. The [recompilation](../reference/glossary.md#builds-and-clients) states `ReadPacket` and `WritePacket` bodies with the right order where it has them. It has gaps, and it is PS4, so Season 3 changes still come from the PC reader. When it and IDA disagree the question goes back to the code, never to a guess.

## Why every includer is re-exported

Patterns share structures through includes, and each pattern compiles alone. A structure added to an include can therefore clash with a local structure of the same name in a pattern that nobody touched. No file of that pattern changed, its last JSON still looks fine, and a test of the pattern being worked on says nothing about it. Only compiling every includer shows the clash, so the rule is that an include change is checked over all its includers and not over the pattern that prompted it.

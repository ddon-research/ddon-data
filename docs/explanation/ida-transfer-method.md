# IDA transfer method

This page is for a reverse engineer who wants to trust, extend or challenge the annotations of the PC 03040008 database: why they were carried over from PS4 02020005 the way they were, why function [pairs](../reference/glossary.md#disassembly-and-transfer) are proved by code shape, what each gate prevents, what the controls show and what the method leaves out. Read the [evidence model](evidence-model.md) first. The commands are in [Transfer annotations from PS4 to PC](../how-to/transfer-annotations-ps4-to-pc.md), the rule lists in [IDA transfer tools](../reference/ida-transfer-tools.md) and the counts in [Status](../reference/status.md#annotated-database-pc-03040008).

## The problem

PS4 02020005 has symbols and DWARF for the whole game. PC 03040008 is a later season, built by another compiler for another word size, with no symbols and no RTTI. A name or a type on PC is worth having only if it is right: a reader of the database takes it as a fact, and a wrong type makes the decompiler lie about every function that touches it. So the method writes only what it can prove holds on PC, leaves the rest as it is, and lists what it left with the reason.

The goal is precision, and coverage is what remains. Every design choice below trades reach for fewer false positives.

## Why not names

A peer would first propose matching by name: PC strings against PS4 symbols, or server emulator names against both. It looks cheap and it is what the earlier annotations of this database did, with links marked inferred. It fails for three reasons.

- **The two sides spell handlers differently and the sets differ.** A diagnostic string `cSeedGameSvConnection::OnPacket_<GROUP>_<NAME>` must lose an unknown number of group tokens before it resembles PS4's `OnPacket_S2C_<NAME>`. Many strings have several candidates or none, since Season 3 added handlers.
- **Equal names can be different functions.** A game handler and a login handler can share a `<NAME>`. A name match pairs them; the class in the string and a shape check do not.
- **Names travel without evidence.** A server name is a [lead](../reference/glossary.md#evidence-marks), and PS4 packet numbers are another scheme altogether. A pairing built on them inherits their errors, invisibly.

The PC's own strings are still used for what they prove: a [tier 0](../reference/glossary.md#disassembly-and-transfer) handler takes the string it alone references, because that is the PC's own name for itself. A string names a handler; it does not by itself prove the PS4 partner. The seed must also pass the shape gate, in its own class, unclaimed by any other string.

## Why code shape

What survives a compiler change is the program's structure: a handler calls one packet reader, a reader calls its codecs in wire order with the same widths, a function takes the same arguments. Call sequences cannot be aligned by position, because the compilers inline differently. They can be aligned on calls already paired, so a gap between two paired calls proposes the unpaired calls inside it, and only when exactly one candidate per side leaves no choice.

The extractor therefore dumps facts, not guesses: ordered call sites, what is provably each call's argument, memory accesses whose base provably holds an argument. Each fact comes from decoded operands and a must-analysis over the flow chart, so a register keeps a value only when every predecessor agrees. A value it cannot prove is absent. Matching is then offline Python over those dumps with tests, bound by hash to the databases they came from, and deterministic. A rule change costs seconds and leaves the database alone.

A single witness can be a coincidence, so pairs pass gates, and they pass all of them.

## The gates and the failure each prevents

| Check | It prevents |
| --- | --- |
| Witnesses: two independent parents, or one plus equal strings or constants | a pair resting on one alignment that happened to fit |
| Uniqueness: a function proposed with two partners rejects every pair involved, and a restart re-evaluates | keeping whichever of two contradictory pairs came first |
| Shape: PC `this` use and stack bytes equal the DWARF parameters | a pair whose arguments cannot be the same; a function no caller loads `ecx` for takes no object, since MSVC's `push ecx` stack reservation looks like a read of it |
| The seed's class: the partner must be of the string's own class | a game handler paired with the login handler of the same name |
| Not trivial: short, widely shared or code-identical functions are not named | one PC address standing for many PS4 functions. MSVC folds identical functions, so such a PC function has no one PS4 name. The fold check counts the immediates each call passes, because hundreds of senders differ only in their `WritePacket` key and are not folded |
| Identified by widths: an element reader needs one occurrence no other packet reader could fit | short equal bodies pairing wrong element readers; the shuffled control accepts such pairs without this gate |
| Same pair at every occurrence | an element reader that pairs one way here and another way there, or has no partner at some occurrence |
| Slot order against every handler pair | a deranged listener pair passing because only the candidates were compared with one another |
| The handler string names the packet class | a member link taken from a shuffled reader: single-member types look plausible, and only the witness removes them |

The first three were designed in. The others exist because a control or a review caught exactly that failure.

## Roles widen the reach

Pure propagation from handler seeds reaches little: its gates need witnesses that the code rarely offers. So the matcher uses roles: positions in the code that mean the same thing on both sides. A handler's unique reader callee is the partner of the `CPacket_<NAME>::ReadPacket` its PS4 partner calls. A bracket of codecs covering the same positions is an element reader. The listener slot a handler passes ties it to a requester, and a requester to its sender.

Roles are not a loosening. Each role names its witnesses and the seeds it rests on, passes the shape and triviality gates, and joins the same controls.

## The two controls

A gate set can be measured only against pairs known to be wrong. Two controls supply that.

**The holdout** withholds a fifth of the seeds under fixed RNG seeds and reruns the pipeline. A role pair that depended on a withheld seed must vanish or return with the same partner. A different partner is a wrong pair, and `match.py` exits with an error. It tests whether the rules give the same answer from less evidence. Its limit: withheld seeds do not return by propagation, so it says nothing about seed correctness itself.

**The shuffled-partner control** deranges the PS4 side of the seeds, so every handler has a wrong partner, and reruns the role rules. Nothing may be accepted, and one acceptance fails the run. This measures the false-positive rate directly, and it is the check that exposed two of the gates above. Reader pairs get the same treatment for member links.

Both are in the run and in its exit status, not in a report: a rule change that breaks one fails at once. They bound the rule's behaviour on these inputs. Independent review still re-derives a sample from the disassembly, which is how the pointer-depth defects and the undersized types were found.

## Why a `lea` never accepts a type

A type is accepted when every access of the paired PC functions lands on a member of the computed layout. The hard case is the `lea`, which has no width: it takes the address of a sub-object, the `this` or out-argument of an inner reader, so nothing checks its size. Inner member starts are dense, so a `lea` at some offset nearly always falls on one by chance.

`nUserSession::CPacket_S2C_CHANGE_JOB_RES` shows it. Its PC reader's `lea`s of sub-objects land on inner leaves of the PS4 layout, so the type looks proved. The PC class's real sub-objects sit at other offsets, since Season 3 removed fields.

So there are two rules. A `lea` may land only on the object's start, one of its own members or an array element start; a `lea` inside an embedded struct contradicts. And a `lea` may contradict a type but never accepts one: a type with no checked load or store stays a forward declaration. A peer might call that too strict, since a reader's `lea`s are real evidence of *some* sub-object. They are evidence of an offset, not of a type. A `lea` passed to a paired callee whose parameter type is that member's type would tie the type as well. **Status:** planned.

## Why partial types, and why their members come from links

Season 3 changed the packet classes, so a whole PS4 layout, even recomputed for 32 bits, fails on them. A peer might try a per-class offset shift: often the shift is constant. But some classes change mid-way, with a list off the shift by an unrelated amount, so a shift rule is wrong exactly where a reader would rely on it.

A partial type therefore holds only members tied by an operation: a codec call whose destination is `obj+X` on PC and `obj+Y` on PS4, at aligned positions in paired readers. Everything else is an explicit gap. Accesses overlapping a linked member must fit it; accesses in a gap are allowed, since a gap claims nothing.

Sizes need their own rule. A lower bound from the last member is too small when a reader writes further, such as the trailing read-ok byte. Hex-Rays then splits the stack object and the local reads wrong. So any access through the object extends a lower-bound size, and any access past a proved size refuses the class. An access check that only tests members misses this, so "inside the object" is its own test.

A local is named only by an operation, such as the stack object passed to a paired reader, never by declaration order, since the compilers lay frames out differently. A rule that named locals by position or relaxed the size gates would label split packet pieces `packet`.

## Why writes go in batches

The transfer is several thousand writes, each with a before-state. It runs headless with a fail-closed precheck, and it compares against the row's recorded current value, so a database that moved since the manifest refuses rather than overwrites. [Write to an IDA database](../how-to/write-to-an-ida-database.md) says why a worker cannot do this. Conflicts with earlier annotations are never overwritten silently: each is settled in a decisions file with evidence, and the row's `current` guards it.

## What the method leaves out

Each of these needs another kind of evidence, not a relaxed gate:

- **Array-element member links.** The element pointer reaches the codec call only through MSVC's null-check join block.
- **Locals at codec sites.** PC call sites without argument sizes carry no stack argument values.
- **Context getters** such as `sContextManager::getContextMyPlayer`. No anchor reaches them, so most locals defined by their results stay unnamed.
- **Typed `lea` types and packet object vtables.** Both are planned rules.
- **The [login handler lists](../reference/packet-handler-tables.md#login-server-the-lists),** which the handler table walk does not reach: it reads the game server's directory only. Login handlers of PC 03040008 have no diagnostic strings to seed from.
- **Register-argument prototypes.** IDA's `__usercall` conventions are not provable from the dump.
- **Everything outside the packet subsystem**, except where it is a helper of it.

## What the results mean for a reader

In the annotated database of PC 03040008:

- A **name** on a paired function means the code shape and gates hold; it does not mean the bodies are identical. Season 3 may have extended a function, which `flags` in `pairs.tsv` and `Season 3:` in the comment state. The function comment holds the PS4 symbol and the rule.
- A **handler name** from a PC string is the PC's own; a handler with one and no `PS4 02020005:` line has no proven partner.
- A **whole type** has every access of its paired functions fitting and at least one checked load or store. `coverage` in `types.tsv` says how much it checked, and it is often partial: a member nothing accessed is unchecked.
- A **partial type** claims only its named members. Its gaps are unknown, not padding, and a size without proof is a lower bound extended by accesses.
- A **forward declaration** claims nothing about layout.
- A **`packet` local** is the handler's object passed to its reader.
- **No annotation proves absence.** A default name means not proved, and `skipped.tsv` and `rejected.tsv` hold the reason where a candidate existed.
- These are inferences of the form the [evidence model](evidence-model.md) describes: the code on PC decides. A wire layout is decided by reading the PC reader, whatever the type here says; types are a reading aid, and the `V` mark of a pattern still needs the code read.

A row not in the database was not disproved, and a row in it could still be wrong: the controls bound the rate on the rules they exercise, and review sampled the rest.

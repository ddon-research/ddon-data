# Documentation writing contract

The rules every page under `docs/` and every short directory README follows, for anyone who writes or reviews documentation in this repository. You need nothing first; [Write documentation](../how-to/write-documentation.md) gives the commands step by step.

This repository is versioned evidence: client dumps, disassembler exports, decrypted traffic, patches and research notes on Dragon's Dogma Online. Its pages describe that evidence and the methods behind it as they stand at the commit a page is written on, and say plainly where they stop.

## The reader

The pages are written for peers: reverse engineers who know x86, ELF and DWARF, and programmers who know Python. They do not know this project's specs or its history. Every page lets them act or understand without reading a spec. A term a page needs is defined once in the [glossary](glossary.md) and linked on first use.

## Level of detail

A page is written at one of two altitudes, by its type.

| Page | May name | Leaves out | Where the left-out fact lives |
| --- | --- | --- | --- |
| Explanation | the directories and tools that are layers of a method (`packets/`, `research/ida/private-copy.sh`, plbatch); the packet, class and resource names an argument rests on; the rules, with the check that enforces them | line numbers; counts of a run; current lists; task, package and wave ids; incidents told as stories | reference pages for names and lists; [Status](status.md) for counts; specs and Git for history |
| Reference, how-to, tutorial | every flag, field, path, command, address, hash and exact name the reader acts on, each checked in the source; counts only in an example that names the date of its run | argument and history | explanation pages |

- **The stability test.** A sentence on an explanation page stays true after the next change that touches no method. If a re-export could change it, it is a count: give its order of magnitude and link to Status.
- **Nothing is lost by moving it.** A fact cut from a page lands on the page this table names, or stays in the spec it came from when it is history. When it has no home, the change that cuts it adds one or reports it.

## One purpose per page (Diátaxis)

| Type | The reader wants | Home | Contains | Never contains |
| --- | --- | --- | --- | --- |
| Tutorial | to learn by doing one thing that is guaranteed to work | `tutorials/` | numbered steps on a fixed input, what to look at, what was learned | options, alternatives, arguments for a design |
| How-to | to reach one goal, already knowing the basics | `how-to/` | the steps, the decisions on the way, how to tell success from failure | background a step does not need |
| Reference | to look up a fact | `reference/` | tables of paths, fields, marks, ids, hashes, flags | argument, history, step lists |
| Explanation | to understand why | `explanation/` | the reasons, the trade-offs, the alternative a peer would propose and why it was not taken, the limits, diagrams | step lists, exhaustive tables |

- Each page opens with one paragraph right after its title: who it is for, what they get and what they need first (by link). The gate checks that the paragraph is there; the reviewer checks what it says.
- A page that starts to serve two purposes is split, and the halves link to each other.
- `docs/index.md` lists every page once, by type, and only pages that exist. An empty type has no folder and no placeholder.

## Directory READMEs

A directory that holds data or code keeps a short `README`: what the directory holds, who produces it, and links to the pages. It holds no method and no history. A README that outside repositories cite by section keeps those sections in place.

`research/03040008/flags/` and `research/knowledge-graph/` are other work with their own documents: pages link to them and never restate them. A tree of other work that is not committed is named in a code span, since a link to it would 404 on GitHub.

## Facts come from the source

- Every path, flag, field, address, default and message is checked in the source at the commit the page is written on. Name the file in a code span when a reader may want to check it.
- Specs (`specs/<NNN>-*/`) give intent and history. When a spec and the code disagree, the page follows the code and the disagreement is reported.
- **Every client fact names its build** (`03040008`, `02030004`, `PS4_02020005`). A layout from one build is no fact about another until it is checked there.
- **Evidence marks keep their meaning on pages:** `V`, `I` and `G`, as the [glossary](glossary.md#evidence-marks) defines them. A page that states a decoded fact keeps the mark its source gives, and never upgrades one. A check that did not run is "not run", never "passed".
- **Counts live in [Status](status.md) and in dated reference examples only.** A number names the date of the run it was measured on. Other pages give orders of magnitude or link to Status, so a re-export changes one page.
- Facts about fixed inputs (a client file, the ELF, a capture's hash) are not counts of a run: they may stand on the subject page with their source.
- Never invent an example value. Show output copied from a real file or run.

## Status words

Use them where the distinction changes a reader's decision, never on every paragraph. Write them inline: `**Status:** planned (no script for it).`

| Word | Meaning |
| --- | --- |
| implemented | in the repository and exercised by a run the page or Status names |
| approximate | implemented, but its output is marked approximate or its check is a sample |
| planned | decided, not in the repository |
| blocked | waiting on a named wall or decision |
| out of scope | listed as such by the page that says why |
| open | not resolved; what would resolve it is named |
| not run | the check exists and did not run here |

Status carries a dated blockquote as its second paragraph, with the date of the run its counts come from. An explanation page needs none: if it seems to, its moving content belongs in Status.

## Terms

- Process vocabulary (coordinator, wave, package, receipt, brief) belongs to the development setup. A page names a script that serves it by what the script does.
- The [glossary](glossary.md) defines the rest. Add a term there before using it on two pages.
- No task ids, package labels or wave names in prose (`T002`, `TC1`, `R2`, `P11`, `wave 2`, `batch B5`). An evidence report that readers need is cited by its path in a code span. x86 registers go in code spans too: `R8` is otherwise read as a label.
- No word that dates a page without a date. The gate refuses these in prose: `currently`, `now`, `nowadays`, `today`, `recently`, `new`, `newly`, `old`, `existing`, `yet`, `no longer`, `so far`, `at present`. A time that matters gets its date; quoted text goes in a code span.
- Spelling is British with -ize (behaviour, summarize); no serial comma; dates as ISO 8601.

## Links and paths

- Pages have no site build, and GitHub renders them. A Markdown link may point at any repository file; the gate checks it against the git index, with its exact case, so it does not 404 on GitHub. A link names a file: to send a reader to a directory, link its README.
- An anchor names a heading of the target, spelled as GitHub spells it.
- A repository path in a code span that starts with `client/`, `packets/`, `research/`, `binaries/`, `patches/`, `tools/`, `specs/` or `docs/` exists in the index, or is a gitignored local path or a tree of uncommitted other work on disk. Globs and `<placeholders>` are not checked.
- Closed specs are records: a page may cite one, and a spec's own paths are never corrected after a move.
- External sites are absolute URLs. Local machine paths appear only where `AGENTS.md` states them (the inputs, the databases, the sibling repositories).

## Diagrams

- Native Mermaid in a `mermaid` fence, next to the prose that explains it. The sentence before the diagram states the one question it answers and what an arrow means. When a second line style or colour carries a meaning, the same sentence says which; colour is never the only carrier.
- Flowchart, sequence diagram or state diagram only. At most about twelve nodes, readable at normal width.
- Node labels read as the prose names things.

## What the documentation does not do

- **It keeps the lesson and drops the story.** When an incident is why a rule exists, the page states the failure the rule prevents, in the present tense, without the task or package that met it. How a number moved and which spec changed what live in the specs and Git.
- A reference to a removed flag, file or page is deleted, not marked. There are no compatibility redirects.
- A page carries no status text that changes none of the reader's decisions.
- **It does not repeat the agents' rules.** `AGENTS.md` is canonical for agents (shell rules, commit rules, role rules). The pages summarize what a human needs and point there.

## Validation

`tools/docs_check.py` runs in the `docs` section of `tools/check.sh`: [Run the gate](../how-to/run-the-gate.md) reads its line, and [Write documentation](../how-to/write-documentation.md) lists its findings. The checks it makes are links and their case, anchors, the index, code-span paths, the mechanical wording rules above, the opening paragraph, the tutorial's pinned inputs and the rows of [Packet ids](packet-ids.md) against the patterns. The wording rules skip those rows: they are data that moved intact, and their report labels resolve through the key above them.

The tutorial's inputs and expected output are machine-checked: changing `docs/tutorials/read-one-packet.md` or its inputs means changing the `TUTORIAL` constant in `tools/docs_check.py` with it.

The external foundation is [Diátaxis](https://diataxis.fr/start-here/).

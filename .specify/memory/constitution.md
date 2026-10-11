# DDON Data Constitution

Operational facts, paths, and commands live in `AGENTS.md`, which is canonical. This document holds
the principles that every root-level feature in `specs/` must satisfy. The knowledge-graph
subproject has its own constitution in `research/knowledge-graph/.specify/memory/constitution.md`.

## Core Principles

### I. Source-Derived Facts Are Immutable

Addresses, layouts, field orders, enum values, packet bytes, and extracted resource content are
versioned observations bound to a client build and a producer. A feature never overwrites one with
an inference. Corrections replace an artifact with a newer observation from a named producer and
revision; they never patch values by hand.

### II. Evidence Authority Follows the Fact Type

DWARF/ELF symbols decide declared class structure; pinned disassembly decides instruction
coverage; decrypted traffic decides wire bytes; ddon-extractor JSON corroborates layouts. IDA,
Ghidra, and reconstructor observations remain distinct and are cross-validated, never silently
merged. Missing decompiler or extractor output is a coverage gap, not negative evidence.
Semantic conclusions cite their evidence and are marked inferred until proven.

### III. Builds and Producers Are Explicit

Every artifact names its client build (`03040008`, `PS4_02020005`, ...), its producer and producer
version, and the input it came from. Carrying a layout across seasons or platforms requires
verification for that format. Ingestion boundaries record source revisions and SHA-256 hashes.

### IV. Reproducible, Streaming, Preserving

Transforms are deterministic and streaming for large artifact sets, publish atomically, and record
the exact command used. Durable derived artifacts are bound to source content, producer/schema
version, and output-affecting configuration, and validated before reuse. Routine cleanup preserves
them; only the affected artifact is purged or rebuilt, explicitly. Game assets, disassembler
databases, credentials, and runtime caches are never committed.

### V. Honest Verification

A check that did not run is reported as not run, never as passed. Results state the command, the
input and output identity, and counts. Measure before optimizing; optimize measured hot paths first.

## Repository Constraints

- The repository aggregates output from external tools (see `AGENTS.md`); features that change a
  producer belong in that producer's repository, with only the refreshed output landing here.
- Paths read by downstream consumers (`client/03040008/`, `research/02030004/`) stay stable; a
  feature that moves them documents the migration.
- Automation is POSIX shell or a `uv`-managed Python project on CPython 3.14.

## Development Workflow

- Features live in `specs/NNN-slug/` and follow the Spec Kit loop described in `AGENTS.md`;
  use the steps that add value and skip the rest.
- `tasks.md` carries task state and blockers, updated in the same session as the work.
- Large data refreshes are reviewed by `git diff --stat` per resource type before commit.

## Governance

This constitution governs root-level features. Amendments are made through `/speckit-constitution`,
bump the version (MAJOR for removed or redefined principles, MINOR for additions, PATCH for
wording), and record the date. `AGENTS.md` must stay consistent with it.

**Version**: 1.0.0 | **Ratified**: 2026-10-11 | **Last Amended**: 2026-10-11

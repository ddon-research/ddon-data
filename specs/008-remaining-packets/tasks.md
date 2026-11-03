# 008 tasks

Coordinator: main session. One subagent at a time. Method, sources and marks: `spec.md`.

- [x] T001 Triage (`research/T001-triage.md`, `T001-triage.tsv`): 115 ids (70 S2C, 45 C2S), 4,887 files; every id has a
  PC handler or sender; PC layouts fit 4,885/4,887 (29.23.16's handler ignores its body); 5 writer loops inferred;
  Arrowgene names all 115, structures 87 (81 equal to the PC layout); 7 batches. Plan: T002 writer loops (IDA),
  T003 B5+B2, T004 B1+B4, T005 B3+B7+B6 (patterns, JSON, names), then review.
- [ ] T002.. Batches: evidence where the dump lacks a reader (`evidence-researcher-ida`), patterns + JSON
  (`implementer`), naming by code / data / extractor / leads; each with its fit counts and JSON changes.
- [ ] Review (adversarial: a sample of V/I/G marks and fits), close, merge and push.

## Running

- T002 (evidence-researcher-ida, brief `briefs/T002-writer-loops.md`), started 2026-11-03.

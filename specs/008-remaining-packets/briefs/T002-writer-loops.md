008 T002: read the five inferred writer loops and the cstr wire form (evidence, short)

Question (PC 03040008): T001 (`research/T001-triage.md` § 3-5) inferred counted lists in the C2S writers of 70.0.1
(`0x77D1E0`), 62.24.1 and 62.10.1 / 12.5.1 (`0x77FD30`), 62.34.1 (`0x77F9D0`), 12.5.1's `Write_cstr` wire form
(`0x8BCA30`), and 62.24.1 / 62.34.1 in B1. Read each writer: the loop, its count write (width, before or after
the elements), each element's codec widths, and `Write_cstr`'s form (length prefix width or terminator). Mark each
V or say what stays inferred. Confirm or correct the TSV rows' `width_seq`/`lists` for these ids and check the
corrected layout against every capture of the id (fit n/m).

IDA: headless batch (read-only, `DBFL_KILL` + `qexit`) on a `cp` of the wave-2 database in
`PC_DDON_03040008/ddon-data-t002w/` (deleted after), or a private copy of the accepted database; never ida-mcp on
`ddon-data-007work`. Output: `specs/008-remaining-packets/research/T002-writer-loops.md` (owns only it and its
`t002/` scripts). Done: final message with the path and at most 10 lines. Stop: budget 45 min of work time.
Base: the head when you start.

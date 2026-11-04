# 010 tasks

Coordinator: main session. One subagent at a time. Goal, error classes, method and PR rules: `spec.md`.

- [x] T000 Clean clone: `D:/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Clean`, `develop` at `e2411fe8f9`, equal to upstream.
- [ ] T001 Baseline and inventory: `dotnet build` and `dotnet test` on unpatched `develop`; framework, packet table, dispatch and robustness
  candidates from reading the server code against `docs/reference/` (`repository-researcher`).
- [ ] T002 Differential harness: server serializers over the captures, read and re-encode, fields against the JSON; per-id table of divergences
  (`implementer`, in the clean clone, on a scratch branch that is not part of the PR).
- [ ] T003 Evidence: PC 03040008 reader or writer per candidate, verdict `V` / `I` / not an error (`evidence-researcher-ida`).
- [ ] T004 Patch: branch `fix/packet-handling`, a test per fix (`implementer`).
- [ ] T005 Adversarial review: which fix would break a working client? (`adversarial-reviewer`), then fixes.
- [ ] T006 Impact outline and PR body (`research/impact.md`); push the branch, open the draft PR on the fork.
- [ ] T007 Close; ask Sam about upstream.

## Running

- (none). Starts when spec 009 closes. Next: brief T001.

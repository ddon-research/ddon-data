# Quickstart: validate the PS4 02020005 ELF dump set

Run from Git Bash in `D:/ddon-data`. Set `D=binaries/PS4_02020005/elf-dumps` and point `SCRATCH` at a
temporary directory outside the repository, such as the session scratchpad. Each step names the
success criterion it checks. Every check prints nothing, or an explicit `FAIL ...`, when it passes.

## 1. Prerequisites

```bash
ls "/d/SCE/ORBIS SDKs/12.000/host_tools/bin/orbis-bin.exe" /c/msys64/ucrt64/bin/llvm-dwarfdump.exe
command -v jq zstd sha256sum sed rg xxd uv timeout
$D/generate-elf-dumps.sh --dry-run        # checks tools and the input hash; writes nothing
```

## 2. Generate (FR-005)

```bash
$D/generate-elf-dumps.sh --compare-sdks; echo "exit=$?"     # 0, or 2 with failures listed in the manifest
# nothing under local/ or .staging/ may be visible to git
git status --porcelain -uall -- $D | rg '/(local|\.staging)/' && echo "FAIL leak"
# no published path may exceed 259 characters (edge case: MAX_PATH)
fd -H -I . "$(cygpath -m "$PWD")/$D" | awk 'length > 259 {print "FAIL long path: " $0}'
```

## 3. Manifest and coverage (SC-001, SC-002)

```bash
# schema: one instance file per manifest line
rm -rf "$SCRATCH/m"; mkdir -p "$SCRATCH/m"; i=0
while IFS= read -r l; do i=$((i+1)); printf '%s\n' "$l" > "$SCRATCH/m/$i.json"; done < $D/manifest.jsonl
uvx check-jsonschema --schemafile specs/001-ps4-static-dumps/contracts/manifest.schema.json "$SCRATCH"/m/*.json || echo "FAIL schema"
# every failed or timed-out dump is named in LOSSES.adoc
jq -r 'select(.status=="failed" or .status=="timeout") | .id' $D/manifest.jsonl |
  while read -r id; do rg -qF "$id" $D/LOSSES.adoc || echo "FAIL failure not in LOSSES: $id"; done
# every category has an ok primary entry or a not-produced entry
comm -23 <(tail -n +2 $D/categories.tsv | cut -f1 | sort -u) \
         <(jq -rs 'map(select((.role=="primary" and .status=="ok") or .kind=="not-produced")) | map(.categories[]) | unique | .[]' $D/manifest.jsonl | sort -u) \
  | sed 's/^/FAIL uncovered: /'
$D/generate-elf-dumps.sh --verify     # re-hash every published file (txt, zst, local) against the manifest
```

## 4. Reproducibility (SC-002)

Run this once before the dumps are committed. It compares hashes of the files on disk, so it does
not depend on git.

```bash
(cd $D && fd -t f -E local -E .staging -E manifest.jsonl . | sort | xargs sha256sum) > "$SCRATCH/files.before"
jq -c 'del(.generated,.seconds,.stderr.first)' $D/manifest.jsonl | sort > "$SCRATCH/manifest.before"
$D/generate-elf-dumps.sh --skip-local
(cd $D && fd -t f -E local -E .staging -E manifest.jsonl . | sort | xargs sha256sum) > "$SCRATCH/files.after"
jq -c 'del(.generated,.seconds,.stderr.first)' $D/manifest.jsonl | sort > "$SCRATCH/manifest.after"
diff "$SCRATCH/files.before" "$SCRATCH/files.after" && diff "$SCRATCH/manifest.before" "$SCRATCH/manifest.after" || echo "FAIL not reproducible"
```

## 5. Expected counts (SC-003)

File paths come from the manifest, because the storage class is decided at run time.

```bash
f() { jq -r --arg id "$1" 'select(.id==$id) | .file' $D/manifest.jsonl; }
cat_() { case "$1" in *.zst) zstd -dcqq "$D/$1";; *) cat "$D/$1";; esac; }
[ "$(tail -n +2 $D/oracles/dynamic.tsv | wc -l)" -eq 234 ] || echo "FAIL dynamic != 234"
[ "$(tail -n +2 $D/oracles/phdrs.tsv | wc -l)" -eq 11 ]    || echo "FAIL phdrs != 11"
[ "$(tail -n +2 $D/oracles/phdrs.tsv | rg -c 'SCE')" -eq 5 ] || echo "FAIL SCE phdrs != 5"
[ "$(cat_ "$(f relocations.orbis-bin)" | rg -c 'R_X86_64_JUMP_SLOT')" -eq 539 ] || echo "FAIL jump slots != 539"
```

Implementation fixes the oracle columns and these patterns, and records them in the README.

## 6. Fact check (SC-004)

`facts.tsv` is registered before the check runs. For each row:
1. Read the answer from `dump_id`.
2. Get the independent value: `xxd -s <off> -l <len>` on `$D/.staging/input/DDOORBIS.elf`, or
   `$D/generate-elf-dumps.sh --exec <tool> <args>` for a second tool.
3. Fill in `result` and `checked`.

```bash
awk -F'\t' '/^F[0-9]/ && $7 !~ /^agree/ {print "FAIL fact " $1 ": " $7}' $D/facts.tsv
```

## 7. Input untouched (SC-006)

```bash
diff $D/.staging/last/input-snapshot.before.tsv $D/.staging/last/input-snapshot.after.tsv || echo "FAIL input changed"
jq -rs '.[] | select(.cwd? and (.cwd | test("IDA9\\.3"))) | "FAIL cwd " + .id' $D/manifest.jsonl
```

## 8. Handover (SC-005)

```bash
rg -oN '^=== (L-[0-9]+)' -r '$1' $D/LOSSES.adoc | sort -u > "$SCRATCH/losses"
rg -oN 'L-[0-9]+' $D/handover/spec.md | sort -u > "$SCRATCH/mapped"
awk '/^=== L-/{id=$2} /Out of scope/{print id}' $D/LOSSES.adoc | sort -u > "$SCRATCH/oos"
comm -23 "$SCRATCH/losses" <(sort -u "$SCRATCH/mapped" "$SCRATCH/oos") | sed 's/^/FAIL unmapped: /'
rg -oN 'oracles/[A-Za-z0-9._-]+' $D/handover/spec.md | sort -u | while read -r o; do [ -f "$D/$o" ] || echo "FAIL missing $o"; done
fd -t f -S +5m . $D/oracles | sed 's/^/FAIL oracle too big: /'
```

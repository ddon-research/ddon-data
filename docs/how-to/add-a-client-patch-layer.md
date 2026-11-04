# Add a client patch layer

This page is for anyone who changed bytes of a PC 03040008 executable and must record the change so that others can replay it. You produce a `.r2` script and a `.json` beside it, replay the script on a clean parent, and add a row to the hash chain. You need `radare2`, `radiff2` and `rahash2` on `PATH`, and the parent and modified executables; how to replay is in [Apply a client patch](apply-a-client-patch.md). Never overwrite an earlier layer or the originals.

## Steps

1. Choose the parent. For a layer meant for hooked runs it is `f1c9`, never `f2a8` ([why](triage-a-client-crash.md#when-a-hook-writes-text)).

2. Generate the two files from the pair of executables, named `<date>_<name>`, as `2022_01_03_ddo_dump_fix_3`:

   ```bash
   radiff2 -r parent.exe modified.exe > patches/<date>_<name>.r2
   radiff2 -j parent.exe modified.exe > patches/<date>_<name>.json
   ```

   Or write the `.r2` by hand as `wx <hex> @ <file offset>` lines, with a `#` comment per site. A virtual address converts to a file offset through [the section table](../reference/client-patches.md#file-offsets-of-the-dumps); for `.text#2`, `0x24CD5DE` is file offset `0x20397DE`.

   Write these in Git Bash, whose `>` gives UTF-8. A PowerShell redirect writes UTF-16, which radare2 cannot run. [The fields of both files](../reference/client-patches.md#the-r2-and-json-files) are in the reference.

3. Replay the `.r2` on a fresh copy of the parent, and hash both executables:

   ```bash
   cp -p parent.exe replay.exe
   radare2 -qnw -i patches/<date>_<name>.r2 replay.exe
   rahash2 -a sha256 parent.exe modified.exe replay.exe
   ```

   Success: `replay.exe` and `modified.exe` have one hash. A difference means the script does not carry the whole change: fix it and repeat.

4. Add a row to [the tables of Client patches](../reference/client-patches.md#patched-executables): name, date, publisher, the parent's hash as Starting Hash, the `.r2` path, the replayed hash as Target Hash, and a note of what the layer changes. If it adds a branch, add it to the lineage too.

5. If the layer answers a mechanism of the [protection inventory](../reference/protection-inventory.md), correct that row.

6. Commit the `.r2`, the `.json` and the page. An executable is a game asset: it is never committed.

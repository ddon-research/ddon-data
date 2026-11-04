# Build plbatch

This page is for anyone who needs the batch engine behind [Export packets to JSON](export-packets-to-json.md). You build `packets/plbatch/build/bin/plbatch.exe` from its pinned PatternLanguage source. You need MSYS2 mingw64 and network access for the first fetch. Why it exists and why this pin: [plbatch design](../explanation/plbatch-design.md).

## Build it

1. Install the tools if they are missing:

   ```sh
   pacman -S mingw-w64-x86_64-{gcc,cmake,ninja,lld}
   ```

   The script compiles with mingw64 by full path, `/c/msys64/mingw64/bin` (measured with gcc 16.2.0, cmake 4.4.4, ninja 1.13.2, lld), never the Strawberry `g++` or `cmake` on `PATH`. `MINGW_BIN` overrides the folder.

2. Run it:

   ```sh
   bash packets/plbatch/build.sh
   ```

   It fetches PatternLanguage at `300d7388475dd7ffd04239dfc889b72fe08bae18` (master, 2026-09-13) with its submodules into `packets/plbatch/build/pl-src`, which is gitignored. `PL_URL` overrides the remote. Never build in the reference clone `D:/GitHub/WerWolv/PatternLanguage`.

3. Success ends with `built <path>/bin/plbatch.exe`. The output is statically linked, importing only `KERNEL32.dll` and `msvcrt.dll`, so it runs from any shell without DLLs beside it.

4. Run its tests, on synthetic inputs (ok, ok-nan, ok-null, stale JSON removed on failure, skip, a UTF-8 string with a quote and an invalid byte):

   ```sh
   bash packets/plbatch/test.sh
   ```

## After moving the folder

`build/obj` records the absolute path of this folder in `CMakeCache.txt`. After moving the folder, delete `build/obj` before running `build.sh`; `build/bin/plbatch.exe` keeps working without it.

**Status:** not run for this page: the build and its tests were not run; the commands are checked against `packets/plbatch/build.sh` and `packets/plbatch/test.sh`.

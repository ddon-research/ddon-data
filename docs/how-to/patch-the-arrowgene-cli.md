# Patch the Arrowgene CLI

This page is for anyone who needs `Arrowgene.Ddon.Cli` to reproduce the annotated dumps and raw packets of client 03040008, or who hit a packet that does not parse. You build the patched CLI and check its hashes. You need the .NET 10 SDK. What each patch changes is in [Arrowgene CLI patches](../reference/arrowgene-cli-patches.md).

An unpatched build skips the affected packets with `Unable to parse structure for resolved packet ... Skipping.` and writes `StructDump:` without a structure.

## Find the clone

The patches exist only as uncommitted changes in one clone, on branch `develop` at base `e2411fe8`:

```text
C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream
```

The clone `D:\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream` sits at the same base without the patches or a build, so do not build there. To see the patches:

```sh
git -C /c/Users/morph/Documents/GitHub/Sehkah/Arrowgene.DragonsDogmaOnline.Upstream diff -- Arrowgene.Ddon.Cli Arrowgene.Ddon.Shared
```

## Build it

1. From the clone's root:

   ```sh
   dotnet build Arrowgene.Ddon.Cli/Arrowgene.Ddon.Cli.csproj -c Debug
   ```

2. Compare the output in `Arrowgene.Ddon.Cli/bin/Debug/net10.0/` with the [recorded hashes](../reference/arrowgene-cli-patches.md#build-identity), using `sha256sum`. A different hash is a different build: a re-export with it needs a comparison against the committed raw files.

3. The scripts `packets/decrypt-annotate-streams.sh` and `packets/decrypt-export-streams.sh` take that path by default. Set `CLI_PATH` for another build.

**Status:** not run: the build command was not run for this page. The hashes of the build on disk were checked on 2026-11-04 and match.

## When a packet fails to parse

A packet that fails to parse is a structure bug, not a capture problem.

1. Write an ImHex pattern in `packets/patterns/03040008/` ([format](../reference/packet-pattern-format.md)).
2. Check it against the client's `nPacket::Read_*` routine.
3. Fix the C# structure.

To list what the C# side lacks, see [Refresh packet statistics](refresh-packet-statistics.md); the CLI also logs `No structure for packet: <name> <id>` at debug level.

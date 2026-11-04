# Patch the Arrowgene CLI

This page is for anyone who needs `Arrowgene.Ddon.Cli` to reproduce the annotated dumps and raw packets of client 03040008, or who hit a packet that does not parse. You build the patched CLI and check its hashes. You need the .NET 10 SDK. What each patch changes is in [Arrowgene CLI patches](../reference/arrowgene-cli-patches.md).

An unpatched build skips the affected packets with `Unable to parse structure for resolved packet ... Skipping.` and writes `StructDump:` without a structure.

## Get the patched source

The patches are committed here as `packets/tools/arrowgene-cli.patch`, against base `e2411fe8` of the server repository. In a clean clone at that commit, with `<repo>` this repository:

```sh
git checkout e2411fe8
git apply --check <repo>/packets/tools/arrowgene-cli.patch
git apply <repo>/packets/tools/arrowgene-cli.patch
```

The `--check` line prints nothing on success. A failure means the clone is not clean or not at that commit.

On this machine the patched tree and its build also sit in `C:\Users\morph\Documents\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream`, as uncommitted changes. The clone `D:\GitHub\Sehkah\Arrowgene.DragonsDogmaOnline.Upstream` is at the same base without them, so do not build there unpatched.

## Build it

1. From the patched clone's root:

   ```sh
   dotnet build Arrowgene.Ddon.Cli/Arrowgene.Ddon.Cli.csproj -c Debug
   ```

2. Compare the output in `Arrowgene.Ddon.Cli/bin/Debug/net10.0/` with the [recorded hashes](../reference/arrowgene-cli-patches.md#build-identity), using `sha256sum`. A different hash is a different build, which a build from another path may well give: a re-export with it needs a comparison against the committed raw files ([Verify a regeneration](verify-a-regeneration.md)).

3. The scripts `packets/decrypt-annotate-streams.sh` and `packets/decrypt-export-streams.sh` take that path by default. Set `CLI_PATH` for another build.

**Status:** `git apply --check` passed on 2026-11-04 on a clean checkout of `e2411fe8`. Not run: the apply itself and the build command. The hashes of the build on disk were checked on 2026-11-04 and match.

## When a packet fails to parse

A packet that fails to parse is a structure bug, not a capture problem.

1. Write an ImHex pattern in `packets/patterns/03040008/` ([format](../reference/packet-pattern-format.md)).
2. Check it against the client's `nPacket::Read_*` routine.
3. Fix the C# structure.

To list what the C# side lacks, see [Refresh packet statistics](refresh-packet-statistics.md); the CLI also logs `No structure for packet: <name> <id>` at debug level.

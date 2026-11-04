# Extract client resources

This page is for anyone who must re-extract a client's resources after a change to ddon-extractor or `gmd.csv`: you run the extractor, replace `client/<build>/` and review the change. You need ddon-extractor (`D:\ddon-extractor`, built with `./gradlew build` or `./gradlew jpackage`, JDK 25), the client (`D:\DDON_03040008`) and `D:\DDON-translation\gmd.csv`. The tree is large: the [repository layout](../reference/repository-layout.md#client) says what it holds and who reads it.

**Status:** not run. No re-extraction was made for this page: its commands are read against `D:\ddon-extractor\README.adoc` and `ExtractResourceCommand.java` at ddon-extractor `e6c358ea`.

## 1. Unpack the archives

```powershell
./ddon-extractor resource -p true -o -m -f json -u -x D:\DDON_03040008 D:\DDON-translation\gmd.csv .
```

| Argument | Meaning |
| --- | --- |
| `-p true` | run in parallel, the default; turn it off to debug |
| `-o` | write files, not console output |
| `-m` | add resolved names and translations from `gmd.csv` |
| `-f json` | JSON, the default; `yaml` is the other format |
| `-u` | unpack `.arc` archives |
| `-x` | process `.arc` files only; it needs `-u` |
| `D:\DDON_03040008` | the client root; `nativePC\rom` is appended to it |
| `D:\DDON-translation\gmd.csv` | the JP and EN message file |
| `.` | what to process, relative to `rom`: `.` is all of it, `game_common\param` one folder, `game_common\param\enemy_group.emg` one file |

The third argument is the input, not an output folder. Output always goes to `output/` under the working directory, followed by the client's path: `output\DDON_03040008\nativePC\rom\...`.

## 2. Extract the resource files

The second run walks the client root, so the unpacked files must be under it. The tree at `D:\DDON_03040008\nativePC\rom` holds them: `base\scr\land_list.lai` is one, with the archive's name as its folder. How they got there from `output\` is not in the extractor's documentation (**I**, inferred from `ExtractResourceCommand.java`: the unpacker writes under `output\`, and the walk reads the client root).

```powershell
./ddon-extractor resource -p true -o -m -f json D:\DDON_03040008 D:\DDON-translation\gmd.csv .
```

Add `-t` to export `.tex` files as DDS, as [Convert textures](convert-textures.md) does, and `-i .dds,.tex` to skip extensions. A log line `Failed to resource one or more resource files.` and a non-zero exit status mean at least one file failed; the lines above it name them. The last line on success is `Extracted all resource files.`

## 3. Replace the tree

Replace `client/03040008/` with `output\DDON_03040008\nativePC\rom\`, so that `client/03040008/base/scr/land_list.lai.json` comes from `output\DDON_03040008\nativePC\rom\base\scr\land_list.lai.json`. Keep the tree's path: outside tools read it, as the [repository layout](../reference/repository-layout.md#what-outside-tools-read) says.

The summaries beside it (`client/03040008.csv`, `client/03040008-resources.csv`, `client/03040008-resources-exclusive.csv`, `client/03040008-extensions.txt`, `client/03040008-headers.csv`) are regenerated separately. `research/scripts/dump-season3-headers.sh` writes `season3headers.csv`, the raw form of the headers file.

**Status:** open. Neither this repository nor ddon-extractor holds a script that writes the other summaries.

## 4. Review the change

The tree holds on the order of 170,000 files ([count](../reference/status.md#client-resources)), so never list or diff it unbounded. Review it per resource type:

```bash
git diff --stat -- client/03040008/quest
```

Then verify by prediction and sample, as in [Verify a regeneration](verify-a-regeneration.md). Commit only after that.

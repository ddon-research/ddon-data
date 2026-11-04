# Choose a resource target

This page is for anyone who wants to decode a client resource format and needs to pick one: you list the extensions ddon-extractor does not support for a build, then choose by value and evidence. You need Git Bash, a checkout at `D:\ddon-data` and ddon-extractor at `D:\ddon-extractor`, because the script has `/d` paths built in. For 02030004 it also reads `D:\ddon-data-s2`. Next comes [Decode a resource format](decode-a-resource-format.md).

## 1. List the unsupported extensions

From the repository root:

```bash
research/scripts/find-unsupported-extensions.sh 03040008
```

The default build is `02030004`. The script compares `ddon-extractor/docs/deserialization/supported-file-extensions.csv` with `client/<build>-resources.csv`, takes one example path per extension from `client/<build>.csv`, writes only to a temporary folder it removes on exit, and prints this (run of 2026-11-04, cut to its start; the totals of each build are on [Status](../reference/status.md#resource-extensions)):

```text
=== Unsupported Extensions ===
Extensions found in 03040008 resources: 331
  - Supported by ddon-extractor: 186
  - Not supported by ddon-extractor: 145
  - Coverage: 56%

Unsupported extensions (each appears in exactly 1 resource file):
  - .acp (e.g., obj\em\emActionParam\em_normal.acp)
```

The script prints the words `each appears in exactly 1 resource file` as a fixed text: it measures nothing. The closing line `Generated temporary files in:` names a folder that is gone by then.

Exit status 1 and a line starting `ERROR:` mean an input file is missing. A `WARNING` about the file paths CSV means the list comes without examples.

## 2. Check one extension by hand

```bash
rg -n '^\.lai,' /d/ddon-extractor/docs/deserialization/supported-file-extensions.csv
rg -n '^\.lai,' client/03040008-resources.csv
rg -c ',gui,' client/03040008.csv
```

The first two print the class of a supported extension: `.lai,rLandInfo`. The class name of an unsupported one is in `client/03040008-resources.csv`, or try the usual `r<Name>` and `r<Name>Info` forms. The third counts the files of an extension in the client. `client/03040008.csv` has the columns `Path,ArcPath,Ext,JamCrcStr,Class,JamCrc,Size,SizeCompress,Offset`, so its `Class` column names the class too.

## 3. Choose

| Ask | How to tell |
| --- | --- |
| Does the format matter to what you are researching? | the example path says what it is for; examples from client 03040008, by family, are below |
| Are there many files? | `rg -c ',<ext>,' client/03040008.csv`; more files make a decoder worth more |
| Does the PS4 build declare the class fully? | `rg -n 'rFoo::load' binaries/PS4_02020005/DDOORBIS_*.elf.c`, or the query in [Decode a resource format](decode-a-resource-format.md#2-read-the-class-and-its-loader) |
| Does it exist in both seasons? | run the script for both builds; a format in Season 2 and Season 3 has a PS4_02020005 layout to start from |

| Family | Unsupported extensions, client 03040008 | Example path |
| --- | --- | --- |
| UI | `.gui`, `.cecp`, the `.edt_*` family | `ui\01_hud\action00.gui`, `ui\05_edit\camera_param.cecp`, `obj\pl\pl000000\edit\preset\body\human_m_muscle.edt_muscle` |
| Animation | `.mot_filter`, `.motparam`, `.ikctrl` | `obj\pl\pl000000\param\etc\motion_filter.mot_filter`, `obj\pl\pl000000\edit\motion\character_edit.motparam`, `obj\pl\pl000000\ik\human_no_fbik.ikctrl` |
| Physics | `.col`, `.shake_ctrl` | `param\game_common.col`, `obj\pl\pl000000\ik\human_damage.shake_ctrl` |
| Audio | `.aser` | `sound\se\mt\mt_atribase.aser` |

Start from Season 2 when the class has no Season 3 pattern: its debug symbols give the base of the layout, and Season 3 is then a comparison against it.

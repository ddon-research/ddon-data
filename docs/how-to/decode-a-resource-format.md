# Decode a resource format

This page is for a reverse engineer who has chosen a client resource class and wants a validated ImHex pattern for it: you read the class and its loader in IDA, write the pattern, validate it, and adapt it to Season 3. You need IDA 9.5 with the databases of [Query an IDA database read-only](query-ida-read-only.md), ImHex with its command line, and the client files of the build (`D:\DDON_02030004`, `D:\DDON_03040008`). To pick a class, see [Choose a resource target](choose-a-resource-target.md); the steps close on a [worked example](#worked-example-rlandinfo).

**Status:** not run. ImHex is not on `PATH` here, so the validation commands are read against `research/scripts/validate_pattern.sh`; the IDA steps use the commands of [Query an IDA database read-only](query-ida-read-only.md). The example's bytes and JSON were read on 2026-11-04.

## 1. Name the class

Each file extension maps to one resource class, in `client/03040008-resources.csv`: `.lai,rLandInfo`. Take the class name from there.

## 2. Read the class and its loader

PS4 02020005 is the one build with debug symbols, so its DWARF gives the declared structure. Make a private copy and read it, as in [Query an IDA database read-only](query-ida-read-only.md):

```bash
bash research/ida/private-copy.sh ps4 mylook
```

From the database, read:

- the struct of the class and of each nested class, with base classes and field offsets;
- `<class>::load`, which gives the magic (a constant compared with the first read), the version (an integer compared with the second read) and the order of the reads;
- the array structures and nested types the loader reads through.

Without IDA, the same decompiled function and types are in the raw export, at a line `rg` finds:

```bash
rg -n 'rLandInfo::load' binaries/PS4_02020005/DDOORBIS_1.elf.c binaries/PS4_02020005/DDOORBIS_2.elf.c binaries/PS4_02020005/DDOORBIS_3.elf.c
rg -n '^struct __cppobj rLandInfo\b' binaries/PS4_02020005/DDOORBIS.elf.h
```

`C:\ddon-dwarf-reconstructor-rust` rebuilds C++ for resource classes from the same DWARF. `D:\ddon-data-s2\recompilation` holds C++ for Season 2 where it is present; check a layout against it, because IDA can misorder stack arguments.

### The archived alternative: Ghidra

[ddon-ghidra-scripts](https://github.com/ddon-research/ddon-ghidra-scripts) (archived, cloned at `D:\ddon-ghidra-scripts`) gives the same two views through PyGhidra. It needs Ghidra 11.4 or later with the PS4 project imported and the DWARF symbols applied, and a `.env` file beside the script with the paths and settings; its setup is `headless-scripts/ddon-binary-analyzer/README.adoc` there. Run it in `D:\ddon-ghidra-scripts\headless-scripts`, and keep the outputs outside the repository, or delete them afterwards:

```bash
./run_ghidra_analysis.sh dwarf "rResourceName" "DDOORBIS.elf" > rResourceName.h
./run_ghidra_analysis.sh function "rResourceName::load" "DDOORBIS.elf" > rResourceName_load.cpp
```

## 3. Write the pattern

Write `research/03040008/r<Type>-pattern.cpp`, following the binary layout exactly, with enums from the debug symbols. The Season 2 and Season 1 patterns are in their own repositories: `ddon-data-s2/research/02030004/` and `ddon-data-s1/research/01020003/`. Start from a sibling when one exists.

Use the base structures of the committed patterns:

```cpp
struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};

struct MtArray
{
    u32 mLength;
};

struct MtTypedArray<T> : MtArray
{
    T arr[mLength];
};
```

Both `char magicString[]` (NUL-terminated) and `char magicString[4]` occur in `research/03040008/`; each reads a 4-byte magic with a trailing NUL.

| In the C++ | In the pattern |
| --- | --- |
| `rResourceName::cClassName` | `rResourceName_cClassName` |
| `uint32_t`, `int32_t`, `uint64_t` | `u32`, `s32`, `u64` |
| `_vptr$ClassName` | left out: it is not in the file |
| padding fields | left out unless they matter |
| a template | a concrete struct, or the pattern language's own template as above |
| the magic constant of `load`, such as `0x49414c` | its bytes: `4C 41 49 00`, `"LAI\0"` |
| many instances | `#pragma pattern_limit` for a large file |

End the file with one placement at offset 0, as `rLandInfo rlandinfo_at_0x00 @0x00;` does.

## 4. Validate it

Run the pattern on real files, first of the build its layout came from:

```bash
imhex --pl format --pattern <pattern> --input <file>
```

`research/scripts/validate_pattern.sh <pattern> <file or directory> [fields]` does the same over a file or a directory, and checks that each named field appears in the output. Its exit status is 0 when all pass, 1 when a run or a field fails, and 2 for bad arguments or when `imhex` is not on `PATH`. In a directory it only finds `*.lai`, `*.arc`, `*.lot`, `*.nll`, `*.qst`, `*.gui` and `*.gmd`.

Success is JSON with the expected field values. Then run the same pattern on the other season's file. A Season 2 pattern typically fails on Season 3 data.

| Failure | Meaning | Do |
| --- | --- | --- |
| `Pattern Error: runtime error: Array grew past set limit of 65536` | field misalignment: a wrong value was read as `mLength`, seldom a large array | find the misaligned field; add `#pragma array_limit <number>` only after confirming the array really is that large |
| no error, wrong data | the file version changed between seasons | compare `magicVersion` and the fields behind it |
| JSON truncated or missing fields | fields were added between the debug symbols and the build | go to the next step |

## 5. Adapt it to Season 3

The debug symbols are of PS4 02020005, a Season 2 build, and describe PC 03040008 only approximately. Season 3 changes need hand work:

1. Compare the two files in a hex editor. Confirm the magic and the version first.
2. Hypothesize where fields were added and what type they have. For the PC reader, make a private copy with target `pc` or `pc-handlers`. The reader of PC 03040008 decides a Season 3 layout ([Evidence model](../explanation/evidence-model.md)).
3. Change the pattern by one field and test it with ImHex; repeat until it ends at the end of the file.
4. Write down what differs, in a comment in the pattern.

## 6. Cross-check against the extractor

Compare the output with the JSON of the same file under `client/03040008/`. The extractor's JSON corroborates a layout; it does not prove one. A format the extractor does not support has no JSON: say so.

## Worked example: rLandInfo

The class `rLandInfo` holds lands and areas, in `.lai` files. Its files are `D:\DDON_02030004\nativePC\rom\game_common\scr\land_list.lai` (client 02030004) and `D:\DDON_03040008\nativePC\rom\base\scr\land_list.lai` (client 03040008).

**The class**, PS4 02020005, as the archived Ghidra DWARF view prints it. The `.elf.h` export gives the same members without the offsets.

```cpp
struct rLandInfo : public cResource {
  MtTypedArray<rLandInfo::cLandInfo> mLandInfo;  // offset: 112, size: 32
};  // Total size: 144 bytes

struct rLandInfo::cLandInfo : public MtObject {
  uint32_t mLandId;  // offset: 8, size: 4
  MtTypedArray<rLandInfo::cLandInfo::cLandAreaInfo> mAreaArray;  // offset: 16, size: 32
};  // Total size: 48 bytes

struct rLandInfo::cLandInfo::cLandAreaInfo : public MtObject {
  uint32_t mAreaId;  // offset: 8, size: 4
};  // Total size: 16 bytes
```

**The loader**, PS4 02020005, `binaries/PS4_02020005/DDOORBIS_2.elf.c`: `rLandInfo::load` compares its first read with `4800844` (`0x49414C`, the bytes `LAI\0`) and its second with `2`, then reads the array. So the file is magic, version, `MtArray<rLandInfo::cLandInfo>`.

**The Season 2 pattern** is `ddon-data-s2/research/02030004/rLandInfo-pattern.cpp`. It is the base structures above, then:

```cpp
struct rLandInfo_cLandInfo_cLandAreaInfo : MtObject
{
    u32 mAreaId;
};

struct rLandInfo_cLandInfo : MtObject
{
    u32 mLandId;
    MtTypedArray<rLandInfo_cLandInfo_cLandAreaInfo> mAreaArray;
};

struct rLandInfo : cResource
{
    MtTypedArray<rLandInfo_cLandInfo> mLandInfo;
};

rLandInfo rlandinfo_at_0x00 @0x00;
```

**Its validation** on the 02030004 file, in the shape the pattern's author recorded (ImHex not run here). The file holds 3 lands with 12, 1 and 4 areas:

```bash
imhex --pl format --pattern rLandInfo-pattern.cpp --input D:/DDON_02030004/nativePC/rom/game_common/scr/land_list.lai
```

```json
{
    "rlandinfo_at_0x00": {
        "magicString": "LAI%00",
        "magicVersion": 2,
        "mLandInfo": {
            "mLength": 3,
            "arr": [
                {
                    "mLandId": 1,
                    "mAreaArray": {
                        "mLength": 12,
                        "arr": [
                            {"mAreaId": 1}, {"mAreaId": 2}, {"mAreaId": 3},
                            {"mAreaId": 4}, {"mAreaId": 5}, {"mAreaId": 6},
                            {"mAreaId": 7}, {"mAreaId": 8}, {"mAreaId": 9},
                            {"mAreaId": 10}, {"mAreaId": 11}, {"mAreaId": 12}
                        ]
                    }
                },
                {
                    "mLandId": 2,
                    "mAreaArray": {
                        "mLength": 1,
                        "arr": [{"mAreaId": 13}]
                    }
                },
                {
                    "mLandId": 3,
                    "mAreaArray": {
                        "mLength": 4,
                        "arr": [
                            {"mAreaId": 14}, {"mAreaId": 15},
                            {"mAreaId": 16}, {"mAreaId": 17}
                        ]
                    }
                }
            ]
        }
    }
}
```

**The same pattern on the 03040008 file** fails, in the shape recorded:

```text
Pattern Error: 18:18 -> runtime error: Array grew past set limit of 65536
  -->   in 02030004\rLandInfo-pattern.cpp:18:18
18 |     T arr[mLength];
                      ^

If this is intended, try increasing the limit using '#pragma array_limit <new_limit>'.
```

The error is misalignment. The bytes show why (`xxd`, 2026-11-04):

```text
client 02030004: 4c41 4900 0200 0000 0300 0000 0100 0000  LAI.............
client 03040008: 4c41 4900 0400 0000 0a00 0000 0100 0000  LAI.............
                 0101 0c00 0000 0100 0000 0200 0000 0300  ................
```

The version is 4 where Season 2 has 2. After `mLandId` come two bytes, `01 01`, and only then `0c00 0000`, the 12 areas. Season 2 reads `0x000c0101` as the count.

**The Season 3 pattern**, `research/03040008/rLandInfo-pattern.cpp`, adds the two fields:

```cpp
struct rLandInfo_cLandInfo : MtObject
{
    u32 mLandId;
    bool mIsDispNews;
    u8 mGameMode;
    MtTypedArray<rLandInfo_cLandInfo_cLandAreaInfo> mAreaArray;
};
```

**The cross-check**: `client/03040008/base/scr/land_list.lai.json` has `FileHeader.VersionNumber` 4 and a `LandInfoList` whose first entry has `LandId` 1, `IsDispNews`, `GameMode` and an `AreaArray` of 12. The extractor agrees on the layout, and the names `IsDispNews` and `GameMode` are the pattern's reading of them, not a proof.

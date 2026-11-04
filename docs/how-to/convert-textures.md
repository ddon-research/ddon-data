# Convert textures

This page is for anyone who wants the images of a DDON client as PNG files. You extract `.tex` and `.dds` from the `.arc` archives with ARCtool, then convert them with one of two scripts in `research/textures/`. You need an unpacked client with its `native*/*rom` tree (`nativePC/rom` on PC, `nativePS3/ps3_rom` on PS3, `nativePS4/ps4_rom` on PS4), [ARCtool](http://www.fluffyquack.com/tools/) by Fluffy Quack for ARC to TEX, and for the conversion [ImageMagick](https://imagemagick.org/script/download.php) or DirectXTex's `texconv.exe` and `texdiag.exe`.

## Steps

1. Choose a root from which to extract every texture, such as `rom/ui`, and change into it.

2. Extract recursively with ARCtool. On Windows in Git Bash, drive `D:`, with ARCtool in `D:\research\ARCtool`:

   ```bash
   for file in $(find "$(pwd | sed 's/\/d/D:/')" -type f -name '*.arc'); do "/d/research/ARCtool/ARCtool.exe" -ddo -texRE6 -alwayscomp -pc -v 7 "$file"; done;
   ```

3. Convert every `.dds` under a folder to PNG, with one of the scripts:

   ```bash
   research/textures/convert-with-direcxtex.sh [-m|--mirror] <folder>
   research/textures/convert-with-magick.sh [-m|--mirror] <folder>
   ```

   | Script | Tool | How it decides |
   | --- | --- | --- |
   | `convert-with-direcxtex.sh` | `texconv.exe`, inspecting each file with `texdiag.exe` | derives per-file flags: `-srgbi` for plain `_UNORM` formats, none for `_SRGB` or HDR ones |
   | `convert-with-magick.sh` | `magick`, as many workers as `nproc` gives | the same for every file: `-colorspace sRGB -define png:color-type=6` |

   The PNGs go to `<folder>_png/`, flat by default. `-m` mirrors the source tree under it. Two files of one name overwrite each other without it.

4. Check a few PNGs by eye. A texture that looks washed out or too dark has a gamma problem: compare with the other script.

## Without the scripts

Plain loops do the same with `magick convert`, for a tree of few files. Next to each `.dds`:

```bash
for file in $(find "$(pwd | sed 's/\/d/D:/')" -type f -name '*.dds'); do magick convert $file "$(dirname "$file")/$(basename "$file" .dds).png"; done
```

Or in a `<folder>_png` beside each folder:

```bash
for d in $(find "$(pwd | sed 's/\/d/D:/')" -maxdepth 1 -mindepth 1 -type d); do (mkdir -p "${d}_png"; for file in $(find ${d} -type f -name '*.dds'); do magick convert "$file" "${d}_png/$(basename "$file" .dds).png"; done;) done;
```

#!/usr/bin/env bash
# convert-dds.sh – DDS → PNG via texconv (DirectXTex) on MSYS2 / Git Bash
set -ou pipefail  # -e intentionally omitted; process_file guards with || return 1

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

print_usage() {
    cat << 'EOF'
Usage: convert-dds.sh [-m|--mirror] <target_directory>

Recursively converts DDS textures to PNG using texconv (DirectXTex).
Inspects each file with texdiag to derive per-file conversion flags.

Options:
  -m, --mirror  Mirror the source directory tree under <target_dir>_png/
  -h, --help    Show this help and exit.

Arguments:
  target_directory  Root folder to scan for .dds files (POSIX or Windows path).
EOF
    exit 0
}

# ---------------------------------------------------------------------------
# Path helpers  (MSYS2 / Git Bash — no WSL)
# ---------------------------------------------------------------------------

# POSIX → Windows path for tools that require Win32 paths (texconv, texdiag).
to_win()   { cygpath -w -- "$1"; }

# Any path (Windows or POSIX) → canonical POSIX for internal bash operations.
to_posix() { cygpath -u -- "$1" 2>/dev/null || realpath -- "$1"; }

# ---------------------------------------------------------------------------
# texdiag helpers
# ---------------------------------------------------------------------------

# Read a named field from "texdiag info" output.
#   texdiag_info_field <file> <field>   →  e.g. "BC1_UNORM"
texdiag_info_field() {
    local file="$1" field="$2"
    texdiag.exe info "$(to_win "$file")" 2>/dev/null \
        | grep -i "^[[:space:]]*${field}[[:space:]]*=" \
        | awk -F'=' '{ gsub(/^[[:space:]]+|[[:space:]\r]+$/, "", $2); print $2 }'
}

# Extract the alpha-channel minimum value from "texdiag analyze".
# Output format: "   Minimum - (R,RRRR G,GGGG B,BBBB A,AAAA)"
# Locale may use commas as decimal separators; we normalise to dots.
#   texdiag_alpha_min <file>   →  e.g. "0.000000" or "1.000000"
texdiag_alpha_min() {
    texdiag.exe analyze "$(to_win "$1")" 2>/dev/null \
        | awk '/Minimum/ {
            match($0, /\(([^)]+)\)/, m)
            n = split(m[1], v, " ")
            val = v[n]          # last token = alpha channel
            gsub(",", ".", val)
            print val
        }'
}

# Returns 0 (success / "true") when every pixel is fully opaque.
alpha_is_opaque() {
    local a_min
    a_min=$(texdiag_alpha_min "$1")
    [[ -n "$a_min" ]] && awk "BEGIN { exit !(${a_min} + 0 >= 1.0) }"
}

# ---------------------------------------------------------------------------
# Flag selection
# ---------------------------------------------------------------------------

# Derive the texconv flags appropriate for a single DDS file.
#
# Gamma note (-srgbi):
#   Game textures are authored for sRGB display even when the DDS header uses a
#   plain _UNORM format code (no explicit _SRGB suffix).  Without -srgbi, WIC
#   treats the decoded values as linear and applies a sRGB gamma curve on PNG
#   export — producing the "too bright / oversaturated" output.  Tagging the
#   input as already-sRGB passes values through unchanged, matching the
#   direct-copy behaviour of ImageMagick.
#
# Alpha note (-sepalpha):
#   -sepalpha is for custom/packed alpha channels that do NOT represent
#   transparency.  For genuine transparency alpha (straight / punch-through),
#   the DirectXTex docs state "the default behavior works fine", so we omit it.
#   The "RGB zeroed under alpha=0" WIC quirk only affects fully-transparent
#   pixels whose color data is irrelevant to the composited result.
select_flags() {
    local file="$1"
    local flags="-nologo -ft png -y"

    local fmt
    fmt=$(texdiag_info_field "$file" "format")

    case "${fmt^^}" in
        BC1_UNORM|BC2_UNORM|BC3_UNORM|BC7_UNORM \
        |B8G8R8A8_UNORM|B8G8R8X8_UNORM \
        |R8G8B8A8_UNORM|R8G8B8X8_UNORM)
            flags+=" -srgbi"
            ;;
        # *_UNORM_SRGB variants carry an explicit sRGB tag — no -srgbi needed.
        # HDR / float formats (BC6H, R16_FLOAT, etc.) must not receive -srgbi.
    esac

    echo "$flags"
}

# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------

process_file() {
    local file="$1"
    local target_dir="$2"
    local mirror="$3"

    # Determine output directory.
    local out_root="${target_dir%/}_png"
    local out_dir="$out_root"

    if [[ "$mirror" == "true" ]]; then
        local rel_dir
        rel_dir=$(dirname "${file#${target_dir}/}")
        [[ "$rel_dir" != "." ]] && out_dir="${out_root}/${rel_dir}"
    fi

    mkdir -p "$out_dir" \
        || { printf 'Error: cannot create output dir "%s"\n' "$out_dir" >&2; return 1; }

    local flags
    flags=$(select_flags "$file") || return 1

    printf 'Converting : %s\n  Format   : %s\n  Flags    : %s\n' \
        "$file" "$(texdiag_info_field "$file" "format")" "$flags"

    # SC2086: word-split on $flags is intentional — they are discrete CLI tokens.
    # shellcheck disable=SC2086
    texconv.exe $flags -o "$(to_win "$out_dir")" "$(to_win "$file")" || return 1
}

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

main() {
    local mirror="false"
    local target_dir=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--mirror) mirror="true"; shift ;;
            -h|--help)   print_usage ;;
            -*)
                printf 'Error: unknown flag "%s"\n' "$1" >&2
                print_usage
                ;;
            *)
                if [[ -z "$target_dir" ]]; then
                    target_dir="$1"
                else
                    printf 'Error: extraneous argument "%s"\n' "$1" >&2
                    print_usage
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$target_dir" ]]; then
        printf 'Error: no target directory specified.\n' >&2
        print_usage
    fi

    target_dir=$(to_posix "$target_dir")

    if [[ ! -d "$target_dir" ]]; then
        printf 'Error: "%s" is not a directory.\n' "$target_dir" >&2
        exit 1
    fi

    local total=0 ok=0 fail=0

    while IFS= read -r -d '' file; do
        total=$((total + 1))
        if process_file "$file" "$target_dir" "$mirror"; then
            ok=$((ok + 1))
        else
            fail=$((fail + 1))
            printf '  !! FAILED: %s\n' "$file" >&2
        fi
    done < <(find "$target_dir" -type f -name '*.dds' -print0)

    printf '\nDone — %d/%d converted, %d failed.\n' "$ok" "$total" "$fail"
}

main "$@"
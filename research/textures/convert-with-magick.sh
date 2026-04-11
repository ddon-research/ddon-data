#!/usr/bin/env bash

set -eou pipefail

print_usage() {
    cat << EOF
Usage: $(basename "$0") [-m|--mirror] <target_directory>

Description:
  Recursively converts DDS textures to PNG using ImageMagick (magick) 
  for raw linear color extraction. Executes concurrently.

Options:
  -m, --mirror      Preserve the internal directory structure in the output root.
  -h, --help        Display this help message and exit.
EOF
    exit 1
}

process_texture() {
    local file="$1"
    local target_dir="$2"
    local mirror_flag="$3"
    
    local out_root="${target_dir%/}_png"
    local out_dir="$out_root"

    if [[ "$mirror_flag" == "true" ]]; then
        local rel_dir
        rel_dir=$(dirname "${file#$target_dir/}")
        if [[ "$rel_dir" != "." ]]; then
            out_dir="$out_root/$rel_dir"
        fi
    fi

    mkdir -p "$out_dir"
    
    local out_file="$out_dir/$(basename "$file" .dds).png"

    # ImageMagick raw execution: 
    # Force sRGB colorspace tagging to prevent internal gamma shifting, 
    # extract alpha natively, export RGBA PNG.
    echo "Worker [$$]: Converting $file"
    magick "$file" -colorspace sRGB -define png:color-type=6 "$out_file"
}

if [[ "${1:-}" == "--worker" ]]; then
    process_texture "$2" "$3" "$4"
    exit 0
fi

main() {
    local mirror="false"
    local target_dir=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--mirror)
                mirror="true"
                shift
                ;;
            -h|--help)
                print_usage
                ;;
            -*)
                echo "Error: Unrecognized flag '$1'" >&2
                print_usage
                ;;
            *)
                if [[ -z "$target_dir" ]]; then
                    target_dir="$1"
                else
                    echo "Error: Extraneous argument '$1'" >&2
                    print_usage
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$target_dir" ]]; then
        print_usage
    fi

    if [[ ! -d "$target_dir" ]]; then
        echo "Error: Target directory '$target_dir' does not exist." >&2
        exit 1
    fi

    target_dir=$(realpath "$target_dir")
    local cores=$(nproc)

    echo "Initializing thread pool: $cores concurrent workers (ImageMagick)..."

    find "$target_dir" -type f -name '*.dds' -print0 | \
        xargs -0 -P "$cores" -I {} bash "$0" --worker "{}" "$target_dir" "$mirror"

    echo "Pipeline execution complete."
}

main "$@"
#!/bin/bash
# find-unsupported-extensions.sh
# Identify resource extensions not supported by ddon-extractor
#
# Usage:
#   ./find-unsupported-extensions.sh [version]
#   
# Examples:
#   ./find-unsupported-extensions.sh 02030004    # Season 2 analysis
#   ./find-unsupported-extensions.sh 03040008    # Season 3 analysis

set -e

VERSION=${1:-"02030004"}
WORKSPACE_ROOT="/d"

# File paths
SUPPORTED_FILE="$WORKSPACE_ROOT/ddon-extractor/docs/deserialization/supported-file-extensions.csv"
if [ "$VERSION" = "02030004" ]; then
    RESOURCES_FILE="$WORKSPACE_ROOT/ddon-data-s2/client/$VERSION-resources.csv"
    FILEPATHS_FILE="$WORKSPACE_ROOT/ddon-data-s2/client/$VERSION.csv"
else
    RESOURCES_FILE="$WORKSPACE_ROOT/ddon-data/client/$VERSION-resources.csv"
    FILEPATHS_FILE="$WORKSPACE_ROOT/ddon-data/client/$VERSION.csv"
fi

# Temporary files
TMP_DIR="/tmp/extension-analysis-$$"
mkdir -p "$TMP_DIR"
SUPPORTED_EXT="$TMP_DIR/supported_extensions.txt"
RESOURCE_EXT="$TMP_DIR/resource_extensions.txt"
UNSUPPORTED_EXT="$TMP_DIR/unsupported_extensions.txt"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "=== Extension Coverage Analysis for Version $VERSION ==="
echo

# Check if files exist
if [ ! -f "$SUPPORTED_FILE" ]; then
    echo "ERROR: Supported extensions file not found: $SUPPORTED_FILE"
    exit 1
fi

if [ ! -f "$RESOURCES_FILE" ]; then
    echo "ERROR: Resources file not found: $RESOURCES_FILE"
    echo "Available resource files:"
    find "$WORKSPACE_ROOT/ddon-data"* -name "*-resources.csv" 2>/dev/null || echo "  None found"
    exit 1
fi

if [ ! -f "$FILEPATHS_FILE" ]; then
    echo "WARNING: File paths CSV not found: $FILEPATHS_FILE"
    echo "  File examples will not be available"
fi

echo "Input files:"
echo "  Supported: $SUPPORTED_FILE"
echo "  Resources: $RESOURCES_FILE"
echo "  File Paths: $FILEPATHS_FILE"
echo

# Extract supported extensions (skip header, remove leading dot)
echo "Extracting supported extensions..."
grep -v '^#' "$SUPPORTED_FILE" | cut -d',' -f1 | sed 's/^\.//' | sort | uniq > "$SUPPORTED_EXT"
SUPPORTED_COUNT=$(wc -l < "$SUPPORTED_EXT")
echo "  Found $SUPPORTED_COUNT supported extensions"

# Extract extensions from resource files (skip header, remove leading dot)
echo "Extracting resource extensions..."
grep -v '^#' "$RESOURCES_FILE" | cut -d',' -f1 | sed 's/^\.//' | sort | uniq > "$RESOURCE_EXT"
RESOURCE_COUNT=$(wc -l < "$RESOURCE_EXT")
echo "  Found $RESOURCE_COUNT unique extensions in resources"

# Find unsupported extensions
echo "Finding unsupported extensions..."
comm -23 "$RESOURCE_EXT" "$SUPPORTED_EXT" > "$UNSUPPORTED_EXT"
UNSUPPORTED_COUNT=$(wc -l < "$UNSUPPORTED_EXT")
echo "  Found $UNSUPPORTED_COUNT unsupported extensions"
echo

# Show unsupported extensions
if [ "$UNSUPPORTED_COUNT" -gt 0 ]; then
    echo "=== Unsupported Extensions ==="
    
    # Calculate how many resource extensions are supported
    SUPPORTED_IN_RESOURCES=$(comm -12 "$RESOURCE_EXT" "$SUPPORTED_EXT" | wc -l)
    
    echo "Extensions found in $VERSION resources: $RESOURCE_COUNT"
    echo "  - Supported by ddon-extractor: $SUPPORTED_IN_RESOURCES"
    echo "  - Not supported by ddon-extractor: $UNSUPPORTED_COUNT"
    echo "  - Coverage: $(( (SUPPORTED_IN_RESOURCES * 100) / RESOURCE_COUNT ))%"
    echo
    
    echo "Unsupported extensions (each appears in exactly 1 resource file):"
    while read -r ext; do
        # Get example file from file paths CSV
        if [ -f "$FILEPATHS_FILE" ]; then
            example=$(grep -v "^Path," "$FILEPATHS_FILE" | grep "\.$ext," | head -1 | cut -d',' -f2)
            if [ -n "$example" ]; then
                echo "  - .$ext (e.g., $example)"
            else
                echo "  - .$ext (no files found)"
            fi
        else
            echo "  - .$ext (file paths not available)"
        fi
    done < "$UNSUPPORTED_EXT" | sort
else
    echo "All $RESOURCE_COUNT extensions found in resources are supported by ddon-extractor!"
fi



echo
echo "Generated temporary files in: $TMP_DIR"
echo "Run with different version: $0 03040008"
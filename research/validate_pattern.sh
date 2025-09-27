#!/bin/bash

# ImHex Pattern Validation Script
# 
# This script validates ImHex patterns against resource files and checks for expected fields.
# It supports both single file validation and batch validation across multiple test files.
#
# Usage:
#   ./validate_pattern.sh <pattern_file> <test_file_or_directory> <expected_fields>
#
# Parameters:
#   pattern_file:     Path to the ImHex pattern file (.cpp or .hexpat)
#   test_file_or_dir: Single resource file to test, or directory containing test files
#   expected_fields:  Comma-separated list of field names to verify in output
#
# Examples:
#   # Single file validation
#   ./validate_pattern.sh ./patterns/rLandInfo-pattern.cpp ./test-data/land_list.lai "mLandId,mIsDispNews"
#   
#   # Directory batch validation
#   ./validate_pattern.sh ./patterns/rItemList-pattern.cpp ./test-data/items/ "mItemId,mCategory"
#
# Exit codes:
#   0 - All validations passed
#   1 - Pattern execution failed or missing expected fields
#   2 - Invalid arguments or missing files

set -euo pipefail

# Color output for better visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_status "$GREEN" "✓ $1"
}

print_error() {
    print_status "$RED" "✗ $1"
}

print_warning() {
    print_status "$YELLOW" "⚠ $1"
}

print_info() {
    print_status "$BLUE" "ℹ $1"
}

# Function to validate a single pattern against a single file
validate_single_file() {
    local pattern="$1"
    local test_file="$2"
    local expected_fields="$3"
    local file_passed=true

    print_info "Testing pattern against: $(basename "$test_file")"
    
    # Check if test file exists
    if [[ ! -f "$test_file" ]]; then
        print_error "Test file not found: $test_file"
        return 1
    fi

    # Run ImHex pattern validation and capture both stdout and stderr
    local result
    local exit_code
    result=$(imhex --pl format --pattern "$pattern" --input "$test_file" 2>&1) || exit_code=$?

    if [[ ${exit_code:-0} -eq 0 ]] && [[ -n "$result" ]] && ! echo "$result" | grep -q "Pattern Error\|runtime error\|Error:"; then
        print_success "Pattern executed successfully"
        
        # Check for expected fields if provided
        if [[ -n "$expected_fields" ]]; then
            print_info "Checking for expected fields..."
            IFS=',' read -ra fields <<< "$expected_fields"
            for field in "${fields[@]}"; do
                # Trim whitespace
                field=$(echo "$field" | xargs)
                if echo "$result" | grep -q "\"$field\""; then
                    print_success "Found expected field: $field"
                else
                    print_error "Missing expected field: $field"
                    file_passed=false
                fi
            done
        fi
        
        # Show a preview of the decoded data (first few lines)
        print_info "Pattern output preview:"
        echo "$result" | head -20 | sed 's/^/  /'
        if [[ $(echo "$result" | wc -l) -gt 20 ]]; then
            echo "  ... (output truncated, $(echo "$result" | wc -l) total lines)"
        fi
    else
        print_error "Pattern execution failed"
        print_error "Error details: $result"
        file_passed=false
    fi

    if [[ "$file_passed" == true ]]; then
        return 0
    else
        return 1
    fi
}

# Function to find resource files in a directory
find_resource_files() {
    local directory="$1"
    # Look for common DDON resource file extensions
    local extensions=("*.lai" "*.arc" "*.lot" "*.nll" "*.qst" "*.gui" "*.gmd")
    
    for ext in "${extensions[@]}"; do
        find "$directory" -type f -name "$ext" 2>/dev/null || true
    done
}

# Main validation function
main() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <pattern_file> <test_file_or_directory> [expected_fields]"
        echo ""
        echo "Examples:"
        echo "  $0 ./patterns/rLandInfo.hexpat ./test-data/land_list.lai \"mLandId,mIsDispNews\""
        echo "  $0 ./patterns/rItemList.cpp ./test-data/items/ \"mItemId,mCategory\""
        exit 2
    fi

    local pattern="$1"
    local test_target="$2"
    local expected_fields="${3:-}"

    # Validate inputs
    if [[ ! -f "$pattern" ]]; then
        print_error "Pattern file not found: $pattern"
        exit 2
    fi

    if [[ ! -e "$test_target" ]]; then
        print_error "Test target not found: $test_target"
        exit 2
    fi

    # Check if imhex is available
    if ! command -v imhex &> /dev/null; then
        print_error "ImHex not found in PATH. Please ensure ImHex is installed and accessible."
        exit 2
    fi

    print_info "Validating pattern: $pattern"
    
    local total_files=0
    local passed_files=0
    local failed_files=0

    if [[ -f "$test_target" ]]; then
        # Single file validation
        total_files=1
        if validate_single_file "$pattern" "$test_target" "$expected_fields"; then
            ((passed_files++))
        else
            ((failed_files++))
        fi
    elif [[ -d "$test_target" ]]; then
        # Directory batch validation
        print_info "Scanning directory for resource files: $test_target"
        
        local files
        mapfile -t files < <(find_resource_files "$test_target")
        
        if [[ ${#files[@]} -eq 0 ]]; then
            print_warning "No resource files found in directory: $test_target"
            exit 2
        fi

        total_files=${#files[@]}
        print_info "Found $total_files resource files to test"
        echo ""

        for file in "${files[@]}"; do
            echo "----------------------------------------"
            if validate_single_file "$pattern" "$file" "$expected_fields"; then
                ((passed_files++))
            else
                ((failed_files++))
            fi
            echo ""
        done
    else
        print_error "Test target is neither a file nor a directory: $test_target"
        exit 2
    fi

    # Final summary
    echo "========================================"
    print_info "Validation Summary:"
    print_info "Total files tested: $total_files"
    
    if [[ $passed_files -gt 0 ]]; then
        print_success "Passed: $passed_files"
    fi
    
    if [[ $failed_files -gt 0 ]]; then
        print_error "Failed: $failed_files"
    fi

    if [[ $failed_files -eq 0 ]]; then
        print_success "All validations passed!"
        exit 0
    else
        print_error "Some validations failed!"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
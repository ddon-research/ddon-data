# Dragon's Dogma Online Reverse Engineering - AI Agent Guide

## Project Overview

This is a **reverse engineering research repository** for Dragon's Dogma Online (DDON), focusing on:
- **Client binary disassembly** (PS4 debug symbols via IDA/Ghidra)
- **Network packet decryption** and protocol analysis  
- **Resource file extraction** and format documentation
- **Cross-referencing** between binary structures, packets, and game resources

## Key Architecture Components

### 1. Multi-Source Data Pipeline
- `binaries/PS4_*/` - IDA/Ghidra dumps with debug symbols (struct definitions, function signatures)
- `client/` - JSON extracts from game files using `ddon-extractor` tool
- `packets/` - Network capture decryption pipeline with automated key bruteforcing
- `research/` - ImHex patterns, analysis scripts, target identification tools, and documentation

### 2. Versioning Strategy
Data is organized by game version (e.g., `03040008`, `PS4_02020005`) with:
- Cross-version comparison capabilities
- Historical preservation of earlier seasons
- Version-specific tooling and patterns

## Critical Workflows

### Client Resource Analysis
```bash
# Standard extraction pattern
ddon-extractor -> client/<version>/*.json
# Generate indices and statistics  
find client/<version> -name "*.json" | jq '...' > analysis.csv
```

### Automated Reverse Engineering Workflow
**Preferred approach using Ghidra automation** (eliminates manual binary inspection):

```bash
# 1. Extract C++ struct definitions from DWARF symbols
& "C:\Program Files\Git\bin\bash.exe" -c "cd /d/ddon-data/research/ghidra/headless-scripts && ./run_ghidra_analysis.sh dwarf 'rResourceName' 'DDOORBIS.elf'"

# 2. Get function decompilation (e.g., load/save methods)
& "C:\Program Files\Git\bin\bash.exe" -c "cd /d/ddon-data/research/ghidra/headless-scripts && ./run_ghidra_analysis.sh function 'rResourceName::load' 'DDOORBIS.elf'"

# 3. Generate ImHex pattern from struct definitions
# Create pattern file in research/<version>/r*-pattern.cpp

# 4. Validate pattern with ImHex CLI
imhex --pl format --pattern rResource-pattern.cpp --input resource.file
```

### Packet Decryption Pipeline
```bash
# Automated decryption (execute via Git Bash on Windows)
& "C:\Program Files\Git\bin\bash.exe" -c "cd /d/ddon-data/packets/keys && ./decrypt-pcapng-streams-all-in-one.sh capture.pcapng"
# Dependencies: tshark, Arrowgene.Ddon.Cli, ddon_common_key_bruteforce
```

### ImHex Pattern Creation Process
**Automated pattern validation workflow:**
1. **DWARF Symbol Extraction** - Use Ghidra scripts to get C++ definitions
2. **Pattern Creation** - Convert to ImHex pattern syntax with proper inheritance
3. **CLI Validation** - Test against resource files: `imhex --pl format --pattern <pattern> --input <file>`
4. **Cross-Version Testing** - Validate Season 2 → Season 3 compatibility
5. **Integration** - Cross-reference with JSON client data

## File Format Conventions

### ImHex Patterns
- Named `r<ResourceType>-pattern.cpp` (e.g., `rItemList-pattern.cpp`)
- Include enum definitions from debug symbols
- Use `#pragma pattern_limit` for large files
- Structure matches PS4 binary layout exactly

### CSV Exports
- Headers format: `<version>-<type>.csv` (e.g., `03040008-headers.csv`)
- Include hex dumps in format: `00000000: 0100 0000	....`
- Cross-reference fields: NpcId, Position.X/Y/Z, area names

### Shell Scripts  
- Use bash (run via Git Bash on Windows with specific syntax)
- **Execution Method**: `& "C:\Program Files\Git\bin\bash.exe" -c "command"`
- Heavy use of `jq` for JSON processing
- `find ... -exec jq` pattern for batch processing
- Results typically piped to CSV files
- **Only create bash/shell scripts** - no batch (.bat) or PowerShell (.ps1) files unless explicitly requested

## Essential Tool Dependencies

**Required for automated development:**
- **PyGhidra** - Headless binary analysis and DWARF symbol extraction
- **ImHex CLI** - Pattern validation and batch resource decoding  
- `tshark` - Network analysis and stream extraction
- `jq` - JSON processing and data extraction  
- `xxd` - Hex dumps for header analysis

**External tools (binaries expected in working directory):**
- `Arrowgene.Ddon.Cli` - Packet decryption
- `ddon_common_key_bruteforce` - Key discovery
- `ddon-extractor` - Client resource extraction

**Ghidra Configuration:**
- Environment setup in `research/ghidra/headless-scripts/.env` 
- PyGhidra path, project directory, and script locations
- Default parameters for symbol exploration and decompilation depth

## Data Correlation Patterns

### Cross-Reference Strategy
- **Binary structs** ↔ **ImHex patterns** ↔ **JSON extracts** ↔ **Network packets**  
- Use NpcId, ItemId as primary keys across data sources
- Validate field layouts against multiple sources
- Position data format: `{X, Y, Z}` coordinates

### Naming Conventions
- Enums: `rItemList_ITEM_CATEGORY` (from debug symbols)
- Resource types: `r<Name>` prefix (e.g., `rItemList`, `rLayout`)
- File extensions map to specific binary formats (hundreds of known types)

### Key Discovery Heuristics  
Packet decryption uses expected plaintext patterns:
- Login: `0100000234000000`
- Game-select/Game: `2C00000234000000`
- Search bounds: ~15k depth, ~40s wall-time
- TCP stream filters based on port/window_size/data_len

## Project-Specific Considerations

- **Windows environment** - Use PowerShell for simple tasks, Git Bash for shell scripts
- **Git Bash Execution** - Always use `& "C:\Program Files\Git\bin\bash.exe" -c "command"` syntax from PowerShell
- **Shell scripts only** - Create bash scripts (.sh) for automation, not batch (.bat) or PowerShell (.ps1) files
- **Automated workflows** - Prefer Ghidra headless scripts over manual binary inspection
- **ImHex CLI validation** - Use command line for pattern testing and batch processing
- **Version awareness** - Always specify game version when working with data
- **Cross-season compatibility** - Season 2 debug symbols work for Season 3 with minor adjustments
- **Pattern iteration** - Use trial-and-error approach with ImHex CLI for version differences
- **Research preservation** - Historical patterns and notes are maintained for reference
- **Target identification** - Use `research/find-unsupported-extensions.sh` to systematically identify next reverse engineering targets

When working with this codebase, prioritize understanding the data flow between binary analysis, resource extraction, and network protocol reverse engineering.
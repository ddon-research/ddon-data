# Pharos OOAnalyzer - Running Large Binary Analysis

## Overview

This setup provides a complete workflow for analyzing large 32-bit Windows executables with Pharos OOAnalyzer using Docker. The script implements the recommended multi-step process from the Pharos documentation for handling large binaries efficiently.

## Analysis Steps

The script performs a 4-step analysis:

1. **Partitioning**: Disassembles the binary and identifies functions using `partition`
2. **Fact Generation**: Analyzes functions and generates Prolog facts using `ooanalyzer`
3. **Prolog Reasoning**: Performs object-oriented analysis using `ooprolog`
4. **JSON Export**: Exports results to JSON format for IDA Pro/Ghidra

### Run Command

```bash
PHAROS_MAX_MEMORY=55000 PHAROS_TIMEOUT=90 PHAROS_THREADS=16 ./run.sh /path/to/DDO_DUMP_Mutex.exe
```

## Expected Runtime (to be verified)

For a binary with >200k functions:
- **Step 1 (Partition)**: 30 minutes - 2 hours
- **Step 2 (Fact Generation)**: 2-8 hours (with 16 threads)
- **Step 3 (Prolog Reasoning)**: 1-4 hours
- **Step 4 (JSON Export)**: < 5 minutes

**Total**: 3-14 hours (highly variable based on binary complexity)

## Output Files

All outputs are written to: `<binary-directory>/pharos-<filename>/`

```
DDO_DUMP_Mutex.ser              # Serialized partition (reusable)
DDO_DUMP_Mutex-facts.pl         # Prolog facts from binary
DDO_DUMP_Mutex-results.pl       # Prolog reasoning results
DDO_DUMP_Mutex.json             # JSON output for IDA/Ghidra
DDO_DUMP_Mutex-partition.log    # Step 1 detailed log
DDO_DUMP_Mutex-ooanalyzer.log   # Step 2 detailed log
DDO_DUMP_Mutex-ooprolog.log     # Step 3 & 4 detailed log
DDO_DUMP_Mutex-summary.txt      # Quick summary of all outputs
```

## Common Issues

### Out of Memory (OOM)
- Reduce `PHAROS_MAX_MEMORY` or increase swap space
- Check Docker Desktop memory limits (Settings > Resources)

### Timeout Errors
```
FSEM[ERROR]: Analysis of function 0x00492DA0 failed: relative CPU time exceeded
```
- Increase `PHAROS_TIMEOUT` (e.g., 120 or 180 seconds)

### Missing new()/delete() Methods
```
OOAN[ERROR]: No new() methods were found. Heap objects may not be detected.
```
- Review results after Prolog step completes
- Manually identify and re-run with `--new-method=0xADDR --delete-method=0xADDR`

## Recovery from Failures

Because the script saves intermediate results:

- **After Step 1 completes**: You have `.ser` file - no need to re-partition
- **After Step 2 completes**: You have `-facts.pl` - can re-run Prolog only
- **After Step 3 completes**: You have `-results.pl` - can regenerate JSON

## Documentation References

- [Large Binary Analysis Guide](https://github.com/cmu-sei/pharos/blob/master/share/prolog/oorules/README.md)
- [OOAnalyzer Tool Documentation](https://github.com/cmu-sei/pharos/blob/master/tools/ooanalyzer/ooanalyzer.pod)
- [IDA Pro Plugin](https://github.com/cmu-sei/pharos/blob/master/tools/ooanalyzer/ida/README.md)
- [Ghidra Plugin (Kaiju)](https://github.com/CERTCC/kaiju/blob/main/docs/OOAnalyzerImporter.md)

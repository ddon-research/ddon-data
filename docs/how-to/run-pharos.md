# Run Pharos

This page is for anyone who wants OOAnalyzer's class recovery on a large 32-bit Windows executable such as a DDO dump (PC 03040008). You run `research/pharos/run.sh`, which works in Docker in four steps, and read its JSON into IDA Pro or Ghidra. You need Docker and `docker-compose` on `PATH`.

**Status:** not run for this page (`run.sh --help` only), and the times below are estimates that nobody measured.

## Steps

1. Run the script on the executable; the output goes to `<binary directory>/pharos-<name>/`, or to a folder given as a second argument:

   ```bash
   PHAROS_MAX_MEMORY=55000 PHAROS_TIMEOUT=90 PHAROS_THREADS=16 research/pharos/run.sh /path/to/DDO_DUMP_Mutex.exe
   ```

   | Variable | Default | Meaning |
   | --- | --- | --- |
   | `PHAROS_IMAGE` | `ghcr.io/cmu-sei/pharos:master` | Docker image |
   | `PHAROS_MAX_MEMORY` | `50000` | maximum memory in MB for the partition and the analysis |
   | `PHAROS_TIMEOUT` | `60` | per-function timeout in seconds |
   | `PHAROS_THREADS` | the container's `nproc` | threads of `ooanalyzer` |

2. Wait for the four steps, which `research/pharos/scripts/analyze.sh` runs inside the container:

   | Step | Tool | Does | Estimate, binary of over 200k functions |
   | --- | --- | --- | --- |
   | 1. Partition | `partition` | disassembles and finds functions | 30 minutes to 2 hours |
   | 2. Fact generation | `ooanalyzer` | analyses functions, writes Prolog facts | 2 to 8 hours with 16 threads |
   | 3. Prolog reasoning | `ooprolog` | object-oriented analysis | 1 to 4 hours |
   | 4. JSON export | `ooprolog` | results as JSON for IDA Pro and Ghidra | under 5 minutes |

   In total 3 to 14 hours, highly variable with the binary.

3. Success prints `Analysis complete!` and these files, for an input `DDO_DUMP_Mutex.exe`. On failure the script exits with the failing step's status and names the log folder.

   ```text
   DDO_DUMP_Mutex.ser              # Serialized partition (reusable)
   DDO_DUMP_Mutex-facts.pl         # Prolog facts from binary
   DDO_DUMP_Mutex-results.pl       # Prolog reasoning results
   DDO_DUMP_Mutex.json             # JSON output for IDA/Ghidra
   DDO_DUMP_Mutex-partition.log    # Step 1 detailed log
   DDO_DUMP_Mutex-ooanalyzer.log   # Step 2 detailed log
   DDO_DUMP_Mutex-ooprolog.log     # Step 3 & 4 detailed log
   DDO_DUMP_Mutex-summary.txt      # Quick summary of all outputs
   ```

4. Load the JSON with the [IDA Pro plugin](https://github.com/cmu-sei/pharos/blob/master/tools/ooanalyzer/ida/README.md) or the [Ghidra plugin (Kaiju)](https://github.com/CERTCC/kaiju/blob/main/docs/OOAnalyzerImporter.md).

## When it fails

| Sign | What to do |
| --- | --- |
| Out of memory | reduce `PHAROS_MAX_MEMORY` or increase swap; check the memory limit of Docker Desktop (Settings > Resources) |
| `FSEM[ERROR]: Analysis of function 0x00492DA0 failed: relative CPU time exceeded` | increase `PHAROS_TIMEOUT`, to 120 or 180 seconds |
| `OOAN[ERROR]: No new() methods were found. Heap objects may not be detected.` | review the results after the Prolog step; identify the methods by hand and re-run with `--new-method=0xADDR --delete-method=0xADDR`. `run.sh` has no way to pass these: run `ooanalyzer` by hand in the container |

## Resuming

The intermediate files survive a failure, but `research/pharos/scripts/analyze.sh` always runs from step 1. To resume, run the later tools by hand in the container, on the file of the last finished step:

| Finished | You have | No need to |
| --- | --- | --- |
| Step 1 | `.ser` | re-partition |
| Step 2 | `-facts.pl` | run more than Prolog |
| Step 3 | `-results.pl` | do more than regenerate the JSON |

## Further reading

- [Large binary analysis guide](https://github.com/cmu-sei/pharos/blob/master/share/prolog/oorules/README.md)
- [OOAnalyzer tool documentation](https://github.com/cmu-sei/pharos/blob/master/tools/ooanalyzer/ooanalyzer.pod)

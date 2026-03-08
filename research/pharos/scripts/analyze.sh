#!/usr/bin/env bash
# Container script that runs inside Docker
# All paths and configuration come from environment variables
set -euo pipefail

# Environment variables (with defaults)
binary="/input/${BINARY_NAME:?BINARY_NAME not set}"
base="${BASE_NAME:?BASE_NAME not set}"
threads=${THREADS:-$(nproc 2>/dev/null || echo 1)}
max_mem=${MAX_MEMORY:-50000}
timeout=${TIMEOUT:-60}

# Output paths
ser="/output/${base}.ser"
facts="/output/${base}-facts.pl"
results="/output/${base}-results.pl"
json="/output/${base}.json"
partition_log="/output/${base}-partition.log"
ooanalyzer_log="/output/${base}-ooanalyzer.log"
ooprolog_log="/output/${base}-ooprolog.log"
summary="/output/${base}-summary.txt"

# Verify binary exists
if [[ ! -f $binary ]]; then
  echo "ERROR: Binary not available inside container: $binary" >&2
  exit 1
fi

# Display configuration
echo "[container] Using partition: $(command -v partition)"
echo "[container] Using ooanalyzer: $(command -v ooanalyzer)"
echo "[container] Using ooprolog: $(command -v ooprolog)"
echo "[container] Binary: $binary"
echo "[container] Threads: $threads"
echo "[container] Max memory: ${max_mem} MB"
echo "[container] Per-function timeout: ${timeout} seconds"
echo

# Add binary info to summary
set +e
file "$binary" >"$summary" 2>&1
echo >>"$summary"
set -e

# Step 1: Partition
echo "[container] ============================================================="
echo "[container] Step 1/4: Partitioning (extracting functions)" | tee -a "$summary"
echo "[container] ============================================================="
{
  partition \
    --serialize "$ser" \
    --maximum-memory "$max_mem" \
    --no-semantics \
    "$binary"
} 2>&1 | tee "$partition_log"

if [[ ! -f "$ser" ]]; then
  echo "[container] ERROR: Partition failed - serialize file not created" >&2
  exit 1
fi

echo "[container] Partitioning complete: $ser"
echo

# Step 2: OOAnalyzer fact generation
echo "[container] ============================================================="
echo "[container] Step 2/4: OOAnalyzer fact generation" | tee -a "$summary"
echo "[container] ============================================================="
{
  ooanalyzer \
    --serialize "$ser" \
    --maximum-memory "$max_mem" \
    --no-semantics \
    --prolog-facts "$facts" \
    --threads "$threads" \
    --per-function-timeout "$timeout" \
    "$binary"
} 2>&1 | tee "$ooanalyzer_log"

if [[ ! -f "$facts" ]]; then
  echo "[container] ERROR: OOAnalyzer failed - facts file not created" >&2
  exit 1
fi

echo "[container] Fact generation complete: $facts"
echo

# Step 3: Prolog reasoning
echo "[container] ============================================================="
echo "[container] Step 3/4: Prolog reasoning" | tee -a "$summary"
echo "[container] ============================================================="
{
  ooprolog \
    --facts "$facts" \
    --results "$results" \
    --log-level=6
} >"$ooprolog_log" 2>&1

if [[ ! -f "$results" ]]; then
  echo "[container] ERROR: Prolog reasoning failed - results file not created" >&2
  exit 1
fi

echo "[container] Prolog reasoning complete: $results"
echo

# Step 4: JSON export
echo "[container] ============================================================="
echo "[container] Step 4/4: Exporting JSON" | tee -a "$summary"
echo "[container] ============================================================="
{
  ooprolog \
    --results "$results" \
    --json "$json"
} >>"$ooprolog_log" 2>&1

if [[ ! -f "$json" ]]; then
  echo "[container] ERROR: JSON export failed - JSON file not created" >&2
  exit 1
fi

echo "[container] JSON export complete: $json"
echo

# Summary
echo >>"$summary"
cat <<EOT >>"$summary"
=============================================================================
Analysis Results
=============================================================================
Partition log:  $partition_log
OOAnalyzer log: $ooanalyzer_log
Prolog log:     $ooprolog_log

Serialize:      $ser
Facts:          $facts
Results:        $results
JSON:           $json
=============================================================================

EOT

echo "[container] ============================================================="
echo "[container] Analysis complete! Review $summary for details."
echo "[container] ============================================================="

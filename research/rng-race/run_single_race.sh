#!/bin/bash
set -o errexit -o nounset -o pipefail
# single-race search for session-2 logins; p window 20000 after session-1 game key, depth 200000
run() { echo "== $1 seed=$2 p0=$3"; ./racescan.exe "$4" login "$2" "$3" $(( $3 + 20000 )) 200000; }
{
run stream1 2344 2048 595926b303b7f85afb4a34af1349b7b9
run stream4 2457 1910 18401f9bc6939953a01b93f9a2e47feb
run stream5 26242 2002 c795bc90ee34c751a985f7f6cffcb3dd
run stream55 5537 1896 8f1db1f9ea524eed47f5ad91ee2e42ff
run stream61 4921 2441 c0daf367ea7953e6ada871b8fc053646
run stream7 2334 2199 f99329e46999bd42901dedb74c3e096e
} 2>&1 | tee single_race.log

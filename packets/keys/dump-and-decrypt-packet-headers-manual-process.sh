#!/bin/bash

##
# Functions
##
function extractTcpStreams() {
	capture="$1"
	
	# Extract the number of tcp streams.
	streams=$(tshark -T fields -e tcp.stream -r "$capture" | sort -n | uniq)
	
	# Since wireshark performs a clean TCP reassembly/dissection, this tends to take up some time. E.g. ~1-2h for all known pcapng files.
	for s in $(echo "$streams"); do
		tshark -2 -q -z follow,tcp,yaml,$(expr $s) -r "$capture" > "${capture}_tcp-stream-$(expr $s).yaml"
	done
}

# INFO: this function merely outlines the flow, but it does not work in an automated way due to a myriad of factors in choosing the right key and right stream.
# Requires the server CLI executable to be available in the path.
function decryptTcpStream() {
	yaml="$1"
	key="$2"

	# Parsing of timestamp might fail if dot is not used as decimal separator, but it might also depend on the region/locale.
	perl -i -p -e "s/(\d),(\d)/$1\.$2/g" "$yaml"
	
	# Sorting "properly" is hard, beware of the "wrong" order.
	# The lowest TCP stream number == first login session, after which the follow-up streams "should" each be game select & game streams.
	# But sometimes another unrelated stream might be interspersed.
	# Thus the flow might look like this: identify first stream, look up key for login #0, attempt to decrypt, if no invalid packets are found everything is OK
	loginStreams=$(grep -l -e "port: 52100" $capture_tcp-stream-*.yaml | sort -rn)
	
	./Arrowgene.Ddon.Cli.exe packet "$yaml" "$key"
}

function dumpPacketHeaderData() {
	capture="$1"
	outFile="$2"
	filter="$3"
	
	# Retrieve useful TCP information in a comma-separated format
	summary=$(tshark -2 -T fields -e frame.number -e frame.time_relative -e tcp.stream -E separator=, -r "$capture" "$filter")
	# Retrieve the first 32 bytes of data after the 0060 size indicator
	data=$(tshark -2 -T fields -e data -r "$capture" "$filter" | cut -c 5- | cut -c -32)
	readarray -t summaryArray < <(echo "$summary")
	readarray -t dataArray < <(echo "$data")
	
	for ((i = 0; i < ${#summaryArray[@]}; i++)); do
		#stream_file,packet_series_counter,packet_header_data,packet_number,packet_time_relative,packet_tcp_stream
		echo "$capture,$i,${dataArray[i]},${summaryArray[i]}" | tee -a "$outFile"
	done
}

# Requires the ddon_common_key_bruteforce executable to be available in the path.
function processHeader() {
	outFile="$1"
	data="$2"
	expectedPlaintext="$3"
	
	# A majority of keys within the first session are available within <50s, mostly in the 2-6s realm. The key depth increases and reaches the currently known max of ~7000.
	output=$(timeout 30 ./ddon_common_key_bruteforce.exe "$data" "$expectedPlaintext" --end_second 40 --key_depth 15000)
	echo -n "$data," | tee -a "$outFile"
	echo -n "$output" | grep "Found match at" | grep -o -e "ms.*" | tee -a "$outFile"
	echo "" | tee -a "$outFile"
}

function dumpPacketHeaderDecryptionKeys() {
	csv="$1"
	outFile="$2"
	expectedPlaintext="$3"
	export -f processHeader
	
	# Extract all to-be-decrypted 32 bytes of header data.
	packet_header_data=$(awk -F ',' '!/^#/ {print $3}' "$csv")
	readarray -t header_data_array < <(echo "$packet_header_data")
	
	# On Windows at least this does not seem to clean up nicely, especially when interrupting the process.
	# This can cause an exhaustion of available semaphores sooner or later and cause stuck proceses, thus clean it up manually.
	rm -rf ~/.parallel/semaphores
	for data in "${header_data_array[@]}"; do
		sem -j 2 processHeader "$outFile" "$data" "$expectedPlaintext"
	done
	sem --wait
}

##
# Setup
##
loginPacketCsv=login-packets.csv
loginPacketKeysCsv="$(basename $loginPacketCsv .csv)-keys.csv"
gameSelectPacketCsv=game-select-packets.csv
gameSelectPacketKeysCsv="$(basename $gameSelectPacketCsv .csv)-keys.csv"
gamePacketCsv=game-packets.csv
gamePacketKeysCsv="$(basename $gamePacketCsv .csv)-keys.csv"

##
# Wireshark filters
##
# Wireshark additionally has interesting preferences which can be enabled to improve live analysis:
# TCP: Validate the TCP checksum if possible, Allow subdissector to reassemble TCP streams, Reassemble out-of-order segments, Try heuristic sub-dissectors first, 
# Protocols: Look for incomplete dissectors, Ignore duplicate frames
# The below filters are based on trial and error and should be relatively accurate, but false positives might still be possible.
##
loginFilter="tcp && tcp.port eq 52100 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60"
gameSelectFilter="tcp && tcp.port eq 52000 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60"
gameFilter="tcp && tcp.port eq 52000 && tcp.window_size eq 65792 && data.len eq 98 && data contains 00:60"

##
# Main
##
echo "INFO: Make sure to have ddon_common_key_bruteforce.exe & all *.pcapng files in the same folder as this script."

echo "#stream_file,packet_series_counter,packet_header_data,packet_number,packet_time_relative,packet_tcp_stream" | tee "$loginPacketCsv"
echo "#stream_file,packet_series_counter,packet_header_data,packet_number,packet_time_relative,packet_tcp_stream" | tee "$gameSelectPacketCsv"
echo "#stream_file,packet_series_counter,packet_header_data,packet_number,packet_time_relative,packet_tcp_stream" | tee "$gamePacketCsv"

echo "#packet_header_data,decryption_key_milliseconds,decryption_key_depth,decryption_key" | tee "$loginPacketKeysCsv"
echo "#packet_header_data,decryption_key_milliseconds,decryption_key_depth,decryption_key" | tee "$gameSelectPacketKeysCsv"
echo "#packet_header_data,decryption_key_milliseconds,decryption_key_depth,decryption_key" | tee "$gamePacketKeysCsv"

for f in *.pcapng; do
	extractTcpStreams "$f"
	dumpPacketHeaderData "$f" "$loginPacketCsv" "$loginFilter"
	dumpPacketHeaderData "$f" "$gameSelectFilter" "$gameSelectFilter"
	dumpPacketHeaderData "$f" "$gamePacketCsv" "$gameFilter"
done

dumpPacketHeaderDecryptionKeys "$loginPacketCsv" "$loginPacketKeysCsv" "0100000234000000"
dumpPacketHeaderDecryptionKeys "$gameSelectPacketCsv" "$gameSelectPacketKeysCsv" "2C00000234000000"
dumpPacketHeaderDecryptionKeys "$gamePacketCsv" "$gamePacketKeysCsv" "2C00000234000000"

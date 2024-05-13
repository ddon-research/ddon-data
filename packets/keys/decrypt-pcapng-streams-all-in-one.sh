#!/bin/bash

function dumpAndDecryptPacketHeaderAndTCPStream() {
	capture="$1"
	outputFolder="$2"
	outputKeysFile="$3"
	filter="$4"
	type="$5"
	expectedPlaintext="$6"
	
	# Retrieve useful TCP information in a comma-separated format
	# Only retain the first packet within a single TCP stream, because once that is cracked, the others should have be using same key
	summary=$(tshark -T fields -E separator=, -e frame.number -e frame.time_relative -e tcp.stream -e data -r "${capture}" "${filter}" | sort -u -t, -k3,3)
	if [[ -n "${summary}" ]]; then
		# Retrieve the first 32 bytes of data after the 0060 size indicator
		data=$(awk -F',' '{print substr($4, 5, 32)}' <<< "${summary}")
		readarray -t summaryArray <<< "${summary}"
		readarray -t dataArray <<< "${data}"
		
		for ((i = 0; i < ${#summaryArray[@]}; i++)); do
			outputLine="${capture},${i},${summaryArray[i]%,*},${dataArray[i]},${type},"
			
			# A majority of keys within the first session are available within <50s. Currently known max key depth is ~7k.
			decryptionOutput=$(./ddon_common_key_bruteforce "${dataArray[i]}" "${expectedPlaintext}" --end_second 40 --key_depth 15000)
			decryptionResult=$(grep -o -E 'ms[0-9]+, i:[0-9]+, key:.*' <<< "${decryptionOutput}")
			if [[ -z "${decryptionResult}" ]]; then
				outputLine+=",,"
			else
				outputLine+=$(perl -ne 'print /^ms([0-9]+,) i:([0-9]+,) key:\s(.*)\s*$/' <<< "${decryptionResult}")
				
				tcpStreamNumber=$(awk -F',' '{print $5}' <<< "${outputLine}")
				tcpStreamYamlFile="${outputFolder}/$(basename "${capture}")_tcp-stream-${tcpStreamNumber}.yaml"
				tshark -2 -q -z follow,tcp,yaml,"${tcpStreamNumber}" -r "${capture}" | perl -p -e 's/([0-9]),([0-9])/$1\.$2/g' > "${tcpStreamYamlFile}"
				
				key=$(awk -F',' '{print $10}' <<< "${outputLine}")
				./Arrowgene.Ddon.Cli packet "${tcpStreamYamlFile}" "${key}"
			fi
			
			#stream_file,packet_series_counter,packet_number,packet_time_relative,packet_tcp_stream,packet_header_data,packet_type,decryption_key_milliseconds,decryption_key_depth,decryption_key
			tee -a "${outputFolder}/${outputKeysFile}" <<< "${outputLine}"
		done
	fi
}

# The below filters are based on trial and error and should be relatively accurate, but false positives might still be possible.
loginFilter="tcp && tcp.port eq 52100 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60"
gameSelectFilter="tcp && tcp.port eq 52000 && tcp.window_size eq 130560 && data.len eq 98 && data contains 00:60"
gameFilter="tcp && tcp.port eq 52000 && tcp.window_size eq 65792 && data.len eq 98 && data contains 00:60"

if [[ ! $(command -v -- tshark) ]]; then
	echo "ERROR: Wireshark CLI 'tshark' is not available!" 1>&2
	exit 1
fi
if [[ ! $(command -v -- ./ddon_common_key_bruteforce) ]]; then
	echo "ERROR: DDON key bruteforcer CLI 'ddon_common_key_bruteforce' is not available in the current folder!" 1>&2
	exit 1
fi
if [[ ! $(command -v -- ./Arrowgene.Ddon.Cli) ]]; then
	echo "ERROR: DDON YAML TCP stream decryption CLI 'Arrowgene.Ddon.Cli' is not available in the current folder!" 1>&2
	exit 1
fi

csvHeader="#stream_file,packet_series_counter,packet_number,packet_time_relative,packet_tcp_stream,packet_header_data,packet_type,decryption_key_milliseconds,decryption_key_depth,decryption_key"
input="$1"
outputFolder="$2"

if [[ -z "${outputFolder}" ]]; then
	outputFolder="decrypted"
fi

if [[ -d "${input}" ]]; then
	echo "Dumping and decrypting for folder: ${input}"
	outputKeysFile="keys-all-in-one.csv"
	if [[ ! -d "${outputFolder}" ]]; then
		mkdir -p "${outputFolder}"
	fi
	echo "${csvHeader}" > "${outputFolder}/${outputKeysFile}"
	
	for f in "${input}"/*.pcapng; do
		echo "Dumping and decrypting for file: ${f}"
		dumpAndDecryptPacketHeaderAndTCPStream "$f" "${outputFolder}" "${outputKeysFile}" "${loginFilter}" "login" "0100000234000000"
		dumpAndDecryptPacketHeaderAndTCPStream "$f" "${outputFolder}" "${outputKeysFile}" "${gameSelectFilter}" "game-select" "2C00000234000000"
		dumpAndDecryptPacketHeaderAndTCPStream "$f" "${outputFolder}" "${outputKeysFile}" "${gameFilter}" "game" "2C00000234000000"
	done
	
	exit 0
fi

if [[ -f "${input}" ]]; then
	outputKeysFile="$(basename "${input}")-keys.csv"
	if [[ ! -d "${outputFolder}" ]]; then
		mkdir -p "${outputFolder}"
	fi
	echo "${csvHeader}" > "${outputFolder}/${outputKeysFile}"
	
	echo "Dumping and decrypting for file: ${input}"
	dumpAndDecryptPacketHeaderAndTCPStream "${input}" "${outputFolder}" "${outputKeysFile}" "${loginFilter}" "login" "0100000234000000"
	dumpAndDecryptPacketHeaderAndTCPStream "${input}" "${outputFolder}" "${outputKeysFile}" "${gameSelectFilter}" "game-select" "2C00000234000000"
	dumpAndDecryptPacketHeaderAndTCPStream "${input}" "${outputFolder}" "${outputKeysFile}" "${gameFilter}" "game" "2C00000234000000"
	
	exit 0
fi

echo "ERROR: First argument is neither an existing file nor directory!" 1>&2
echo "Usage: $0 <file|folder>"
exit 1

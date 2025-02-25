#!/bin/bash


for f in $(realpath encrypted_streams/*.yaml); do
	if [[ $f =~ (stream[0-9]+).*tcp-stream-([0-9]+) ]]; then
		export streamName="${BASH_REMATCH[1]}"
		export tcpStreamNumber="${BASH_REMATCH[2]}"
		decryptionKey=$(awk -F',' '{match($1,/.*(stream[0-9]+).*/,stream)}{if (stream[1] == "'$streamName'" && $5 == "'$tcpStreamNumber'") print $10}' <<< cat keys/keys-all-in-one.csv)
		echo "file=$f"
		echo "streamName=$streamName, tcpStreamNumber=$tcpStreamNumber, decryptionKey=$decryptionKey"
		
		"Arrowgene.Ddon.Cli" packet "${f}" --key="${decryptionKey}" --export-decrypted-packets --byte-dump=, --byte-dump-header --byte-dump-prefix=0x --structure-dump --utf8-dump
	fi
done


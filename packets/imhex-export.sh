#!/bin/bash
shopt -s nullglob

filter=$1 #S2C_QUEST_JOIN_LOBBY_QUEST_INFO_NTC,LOBBY_DATA_MSG
pattern=../research/03040008/packets/$2-pattern.cpp #S2C_JOIN_LOBBY_QUEST_INFO_NOTICE,C2S_LOBBY_DATA_MSG_REQ
maxParallelProcs=1

if [[ ! -f "${pattern}" ]]; then
	echo "ERROR: pattern file could not be found"
	exit 1
fi

if (( maxParallelProcs > 1 )); then
	for f in decrypted_raw/**/*"${filter}"*; do
		mkdir -p ./decrypted_json/$(dirname $f)
		echo $f
	done | xargs -P ${maxParallelProcs} -I {} imhex --pl format --pattern "${pattern}" --input {} --output ./decrypted_json/$(dirname {})/$(basename {}).json
else
	for f in decrypted_raw/**/*"${filter}"*; do
		mkdir -p ./decrypted_json/$(dirname $f)
		echo $f
		imhex --pl format --pattern "${pattern}" --input $f --output ./decrypted_json/$(dirname $f)/$(basename $f).json
	done
fi

rsync -a decrypted_json/decrypted_raw/ decrypted_json
rm -rf decrypted_json/decrypted_raw

#  grep -h -R -o "msgId.*" --include \*LOBBY_DATA_MSG_NTC\*.json ./decrypted_json | sort | uniq

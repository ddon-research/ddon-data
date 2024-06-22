#!/bin/bash

cd packets
cd decrypted_annotated

grep -h -e "C2S" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-c2s-packets.txt
grep -h -e "S2C" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-s2c-packets.txt
grep -h -e "L2C" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-l2c-packets.txt
grep -h -e "C2L" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-c2l-packets.txt
grep -h -e "Unknown Pcap" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-unknown-packets.txt

while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-c2s-packets.txt > ../decrypted-tcp-streams-unique-c2s-packets-count.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-s2c-packets.txt > ../decrypted-tcp-streams-unique-s2c-packets-count.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-l2c-packets.txt > ../decrypted-tcp-streams-unique-l2c-packets-count.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-c2l-packets.txt > ../decrypted-tcp-streams-unique-c2l-packets-count.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-unknown-packets.txt > ../decrypted-tcp-streams-unique-unknown-packets-count.txt

rm ../decrypted-tcp-streams-unique-c2s-packets.txt
rm ../decrypted-tcp-streams-unique-s2c-packets.txt
rm ../decrypted-tcp-streams-unique-l2c-packets.txt
rm ../decrypted-tcp-streams-unique-c2l-packets.txt
rm ../decrypted-tcp-streams-unique-unknown-packets.txt

grep -h -e "C2S" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-client-packets.txt
grep -h -e "S2C" * | perl -p -e "s/Server|Client //g;" -e "s/Pcap.*//g;" -e "s/#\d+//g;" -e "s/\s+/ /" | sort | uniq > ../decrypted-tcp-streams-unique-server-packets.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-client-packets.txt > ../decrypted-tcp-streams-unique-client-packets-count.txt
while read h; do count=$(grep -h -e "$h" * | wc -l); echo $h,$count; done < ../decrypted-tcp-streams-unique-server-packets.txt > ../decrypted-tcp-streams-unique-server-packets-count.txt

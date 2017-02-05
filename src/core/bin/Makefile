all: reader_process client_process server_process kill_router pcap_packet_sniff routing_table stress_increase routing_table_read gettime thread_spawn

reader_process: reader.c
	gcc -o reader reader.c

client_process: client.c
	gcc -o client client.c -lm

server_process: server.c
	gcc -o server server.c -lm

kill_router : kill_routing_daemon.c
	gcc -o kill_routing_daemon kill_routing_daemon.c

pcap_packet_sniff: pcap_packet_sniffer.c
	gcc -o pcap_packet_sniffer pcap_packet_sniffer.c ../dilation-code/scripts/TimeKeeper_functions.c ../dilation-code/scripts/utility_functions.c -lpcap -lm

routing_table: routing_table_monitor.c
	gcc -o routing_table_monitor routing_table_monitor.c ../dilation-code/scripts/TimeKeeper_functions.c ../dilation-code/scripts/utility_functions.c -lm

routing_table_read: routing_table_reader.c
	gcc -o routing_table_reader routing_table_reader.c -lm

stress_increase: stress_increaser.c
	gcc -o stress_increaser stress_increaser.c

gettime: gettimepid.c
	gcc -o gettimepid gettimepid.c

thread_spawn: thread_spawner.c
	gcc -o thread_spawner thread_spawner.c -lpthread

clean:
	rm *.o
	rm reader server client kill_routing_daemon pcap_packet_sniffer
	rm routing_table_monitor routing_table_reader stress_increaser gettimepid thread_spawner


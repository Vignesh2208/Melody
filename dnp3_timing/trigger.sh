bro -b -C -r ./Ameren-DNP3/pcaps/DNP3_TestData021914.pcap  dnp3_parser_bro/ /usr/local/bro/share/bro/policy/tuning/json-logs.bro 

python plots/latency_hist.py dnp3.log


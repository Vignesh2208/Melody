bro -b -C -r $1  dnp3_parser_bro/ /usr/local/bro/share/bro/policy/tuning/json-logs.bro 

python plots/latency_hist.py dnp3.log


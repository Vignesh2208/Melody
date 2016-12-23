echo "Generating $1.log"
bro -b -C -r $1  dnp3_parser_bro/ /usr/local/bro/share/bro/policy/tuning/json-logs.bro
mv dnp3.log "$1.log"

echo "Generating $2.log"
bro -b -C -r $2  dnp3_parser_bro/ /usr/local/bro/share/bro/policy/tuning/json-logs.bro
mv dnp3.log "$2.log"

echo "Generating $3.log"
bro -b -C -r $3  dnp3_parser_bro/ /usr/local/bro/share/bro/policy/tuning/json-logs.bro
mv dnp3.log "$3.log"

python plots/latency_hists_plotly.py "$1.log" "$2.log" "$3.log"


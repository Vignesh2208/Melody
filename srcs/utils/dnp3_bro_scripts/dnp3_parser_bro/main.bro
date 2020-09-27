##! A very basic DNP3 analysis script that just logs requests and replies.

module DNP3;

@load ./consts

export {
	redef enum Log::ID += { LOG };

	type Info: record {
		## Time of the request.
		request_ts: time           &log &optional;
		## Time of the response.
		response_ts:time           &log &optional;
		## duration latency of the request-response transaction
		latency:    interval       &log &optional;
		## duration latency of the request-response transaction
		periodicity: interval      &log &optional;
		## Unique identifier for the connection.
		uid:        string         &log;
		## Identifier for the connection.
		id:         conn_id        &log;
		## The name of the function message in the request.
		fc_request: string         &log &optional;
		## The name of the function message in the reply.
		fc_reply:   string         &log &optional;
		## The response's "internal indication number".
		iin:        count          &log &optional;
	};

	## Event that can be handled to access the DNP3 record as it is sent on
	## to the logging framework.
	global log_dnp3: event(rec: Info);
}

redef record connection += {
	dnp3: Info &optional;
};

const ports = { 20000/tcp , 20000/udp };
redef likely_server_ports += { ports };
global watching_dnp3: table[string] of time &create_expire=10secs;
global last_dnp3_resp: table[string] of time &create_expire=10secs;

event bro_init() &priority=5
	{
	Log::create_stream(DNP3::LOG, [$columns=Info, $ev=log_dnp3, $path="dnp3"]);
	Analyzer::register_for_ports(Analyzer::ANALYZER_DNP3_TCP, ports);
	}

event dnp3_application_request_header(c: connection, is_orig: bool, application_control: count, fc: count)
	{
	if ( ! c?$dnp3 )
		c$dnp3 = [$uid=c$uid, $id=c$id];

	c$dnp3$request_ts = network_time();
	c$dnp3$fc_request = function_codes[fc];
    watching_dnp3[c$uid] = network_time();

	if (c$uid in last_dnp3_resp)
		{
		c$dnp3$periodicity = network_time() - last_dnp3_resp[c$uid];
		Log::write(LOG, c$dnp3);
		delete c$dnp3;
		}
	}

event dnp3_application_response_header(c: connection, is_orig: bool, application_control: count, fc: count, iin: count)
	{
	if ( ! c?$dnp3 )
		c$dnp3 = [$uid=c$uid, $id=c$id];

	c$dnp3$fc_reply = function_codes[fc];
	c$dnp3$iin = iin;

    c$dnp3$response_ts = network_time();
    last_dnp3_resp[c$uid] = network_time();

    if (c$uid in watching_dnp3) 
      {
      c$dnp3$latency = network_time() - watching_dnp3[c$uid];
	  Log::write(LOG, c$dnp3);
	  delete c$dnp3;
      }

	}

event connection_state_remove(c: connection) &priority=-5
	{
	if ( ! c?$dnp3 )
		return;

	Log::write(LOG, c$dnp3);
	delete c$dnp3;
	}

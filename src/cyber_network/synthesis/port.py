__author__ = 'Rakesh Kumar'

import string

class Port(object):

    def __init__(self, sw, port_json, mininet_intf=None):

        self.sw = sw
        self.port_id = None
        self.curr_speed = None
        self.max_speed = None

        self.mac_address = None
        self.port_number = None
        self.state = None
        self.attached_host = None

        if not port_json and mininet_intf:
            self.parse_mininet_intf(mininet_intf)
        else:

            if self.sw.network_graph.controller == "ryu":
                self.parse_ryu_port_json(port_json)

            elif self.sw.network_graph.controller == "onos":
                self.parse_onos_port_json(port_json)

    def parse_onos_port_json(self, port_json):

        self.port_number = int(port_json["port"])
        self.port_id = str(self.sw.node_id) + ":" + str(self.port_number)
        self.mac_address = None
        self.state = "up"

    def parse_ryu_port_json(self, port_json):

        self.port_id = str(self.sw.node_id) + ":" + str(port_json["port_no"])
        self.port_number = port_json["port_no"]
        self.mac_address = port_json["hw_addr"]

        if "curr_speed" in port_json:
            self.curr_speed = int(port_json["curr_speed"])
        if "max_speed" in port_json:
            self.max_speed = int(port_json["max_speed"])

        self.state = "up"

    def parse_mininet_intf(self, intf):

        self.port_number = int(string.split(intf.name,"-")[1][3:])
        self.mac_address = intf.MAC()
        self.port_id = str(self.sw.node_id) + ":" + str(self.port_number)

        self.state = "up"

    def __str__(self):

        return str(self.port_id)

__author__ = 'Rakesh Kumar'

import sys
import logging
import codecs
from collections import MutableMapping as DictMixin
from netaddr import IPNetwork
#from UserDict import DictMixin

field_names = ["in_port",
               "ethernet_type",
               "ethernet_source",
               "ethernet_destination",
               "src_ip_addr",
               "dst_ip_addr",
               "ip_protocol",
               "tcp_destination_port",
               "tcp_source_port",
               "udp_destination_port",
               "udp_source_port",
               "vlan_id",
               "has_vlan_tag"]

ryu_field_names_mapping = {"in_port": "in_port",
                           "eth_type": "ethernet_type",
                           "eth_src": "ethernet_source",
                           "eth_dst": "ethernet_destination",
                           "nw_src": "src_ip_addr",
                           "nw_dst": "dst_ip_addr",
                           "ip_proto": "ip_protocol",
                           "tcp_dst": "tcp_destination_port",
                           "tcp_src": "tcp_source_port",
                           "udp_dst": "udp_destination_port",
                           "udp_src": "udp_source_port",
                           "vlan_vid": "vlan_id"}

ryu_field_names_mapping_reverse = {"in_port": "in_port",
                                   "ethernet_type": "eth_type",
                                   "ethernet_source": "eth_src",
                                   "ethernet_destination": "eth_dst",
                                   "src_ip_addr": "nw_src",
                                   "dst_ip_addr": "nw_dst",
                                   "ip_protocol": "nw_proto",
                                   "tcp_destination_port": "tcp_dst",
                                   "tcp_source_port": "tcp_src",
                                   "udp_destination_port": "udp_dst",
                                   "udp_source_port": "udp_src",
                                   "vlan_id": "vlan_vid"}

onos_field_names_mapping = {"IN_PORT": "in_port",
                            "ETH_TYPE": "ethernet_type",
                            "ETH_SRC": "ethernet_source",
                            "ETH_DST": "ethernet_destination",
                            "IPV4_SRC": "src_ip_addr",
                            "IPV4_DST": "dst_ip_addr",
                            "IP_PROTO": "ip_protocol",
                            "TCP_DST": "tcp_destination_port",
                            "TCP_SRC": "tcp_source_port",
                            "UDP_DST": "udp_destination_port",
                            "UDP_SRC": "udp_source_port",
                            "VLAN_VID": "vlan_id"}

onos_field_names_mapping_reverse = {"in_port": ("IN_PORT", "port"),
                                    "ethernet_type": ("ETH_TYPE", "ethType"),
                                    "ethernet_source": ("ETH_SRC", "mac"),
                                    "ethernet_destination": ("ETH_DST", "mac"),
                                    "src_ip_addr": ("IPV4_SRC", "ip"),
                                    "dst_ip_addr": ("IPV4_DST", "ip"),
                                    "ip_protocol": ("IP_PROTO", "protocol"),
                                    "tcp_destination_port": ("TCP_DST", "tcpPort"),
                                    "tcp_source_port": ("TCP_SRC", "tcpPort"),
                                    "udp_destination_port": ("UDP_DST", "udpPort"),
                                    "udp_source_port": ("UDP_SRC", "udpPort"),
                                    "vlan_id": ("VLAN_VID", "vlanId")}


class OdlMatchJsonParser():
    def __init__(self, match_json=None):
        self.field_values = {}
        self._parse(match_json)

    def _parse(self, match_json):

        for field_name in field_names:

            try:
                if field_name == "in_port":
                    self[field_name] = match_json["in-port"]

                elif field_name == "ethernet_type":
                    self[field_name] = match_json["ethernet-match"]["ethernet-type"]["type"]

                elif field_name == "ethernet_source":
                    self[field_name] = match_json["ethernet-match"]["ethernet-source"]["address"]

                elif field_name == "ethernet_destination":
                    self[field_name] = match_json["ethernet-match"]["ethernet-destination"]["address"]

                elif field_name == "src_ip_addr":
                    self[field_name] = match_json["src_ip_addr"]

                elif field_name == "dst_ip_addr":
                    self[field_name] = match_json["dst_ip_addr"]

                elif field_name == "ip_protocol":
                    self[field_name] = match_json["ip-match"]["ip-protocol"]

                elif field_name == "tcp_destination_port":
                    self[field_name] = match_json["tcp-destination-port"]

                elif field_name == "tcp_source_port":
                    self[field_name] = match_json["tcp-source-port"]

                elif field_name == "udp_destination_port":
                    self[field_name] = match_json["udp-destination-port"]

                elif field_name == "udp_source_port":
                    self[field_name] = match_json["udp-source-port"]

                elif field_name == "vlan_id":
                    self[field_name] = match_json["vlan-match"]["vlan-id"]["vlan-id"]

            except KeyError:
                continue

    def __getitem__(self, item):
        return self.field_values[item]

    def __setitem__(self, field_name, value):
        self.field_values[field_name] = value

    def __delitem__(self, field_name):
        del self.field_values[field_name]

    def keys(self):
        return self.field_values.keys()


class Match(DictMixin):
    def __getitem__(self, item):
        return self.match_field_values[item]

    def __setitem__(self, key, value):
        self.match_field_values[key] = value

    def __delitem__(self, key):
        del self.match_field_values[key]

    def __len__(self):
        return len(self.match_field_values)

    def __iter__(self):
        for i in self.match_field_values:
            yield i

    def keys(self):
        return self.match_field_values.keys()

    def __init__(self, match_json=None, controller=None, flow=None, is_wildcard=True):

        self.flow = flow
        self.match_field_values = {}

        if match_json and controller == "onos":
            self.add_element_from_onos_match_json(match_json)
        elif match_json and controller == "ryu":
            self.add_element_from_ryu_match_json(match_json)
        elif match_json and controller == "sel":
            self.add_element_from_sel_match_json(match_json)
        elif is_wildcard:
            for field_name in field_names:
                self.match_field_values[field_name] = sys.maxsize

    def is_match_field_wildcard(self, field_name):
        return self.match_field_values[field_name] == sys.maxsize

    def add_element_from_onos_match_json(self, match_json):

        def get_onos_match_field(field_name, match_json):

            for onos_field_dict in match_json:
                if onos_field_dict["type"] == onos_field_names_mapping_reverse[field_name][0]:
                    return onos_field_dict[onos_field_names_mapping_reverse[field_name][1]]

            raise KeyError

        for field_name in field_names:

            try:
                if field_name == "in_port":
                    in_port_str = get_onos_match_field(field_name, match_json)
                    self[field_name] = int(in_port_str)

                elif field_name == "ethernet_type":
                    eth_type_str = get_onos_match_field(field_name, match_json)
                    self[field_name] = int(eth_type_str, 16)

                elif field_name == "ethernet_source":
                    mac_str = get_onos_match_field(field_name, match_json)
                    mac_int = int(mac_str.replace(":", ""), 16)
                    self[field_name] = mac_int

                elif field_name == "ethernet_destination":
                    mac_str = get_onos_match_field(field_name, match_json)
                    mac_int = int(mac_str.replace(":", ""), 16)
                    self[field_name] = mac_int

                # TODO: Add graceful handling of IP addresses
                elif field_name == "src_ip_addr":
                    ip_str = get_onos_match_field(field_name, match_json)
                    self[field_name] = IPNetwork(ip_str)
                elif field_name == "dst_ip_addr":
                    ip_str = get_onos_match_field(field_name, match_json)
                    self[field_name] = IPNetwork(ip_str)

                elif field_name == "ip_protocol":
                    ip_proto_str = get_onos_match_field(field_name, match_json)
                    self[field_name] = int(ip_proto_str)

                elif field_name == "tcp_destination_port":
                    self[field_name] = int(get_onos_match_field(field_name, match_json))

                elif field_name == "tcp_source_port":
                    self[field_name] = int(get_onos_match_field(field_name, match_json))

                elif field_name == "udp_destination_port":
                    self[field_name] = int(get_onos_match_field(field_name, match_json))

                elif field_name == "udp_source_port":
                    self[field_name] = int(get_onos_match_field(field_name, match_json))

                elif field_name == "vlan_id":

                    vlan_id = get_onos_match_field(field_name, match_json)

                    if vlan_id == 4096:
                        self[field_name] = sys.maxsize
                        self["has_vlan_tag"] = 1
                    else:
                        self[field_name] = 0x1000 + vlan_id
                        self["has_vlan_tag"] = 1

            except KeyError:
                self[field_name] = sys.maxsize

                if field_name == 'vlan_id':
                    self["has_vlan_tag"] = sys.maxsize

                continue

    def add_element_from_sel_match_json(self, match_json):

        for field_name in field_names:
            try:
                if field_name == "in_port":
                    self[field_name] = int(match_json["inPort"])

                elif field_name == "ethernet_type":
                    self[field_name] = int(match_json["ethType"])

                elif field_name == "ethernet_source":
                    mac_int = int(match_json["ethSrc"].replace(":", ""), 16)
                    self[field_name] = mac_int

                elif field_name == "ethernet_destination":
                    mac_int = int(match_json["ethDst"].replace(":", ""), 16)
                    self[field_name] = mac_int

                # TODO: Add graceful handling of IP addresses
                elif field_name == "src_ip_addr":
                    self[field_name] = IPNetwork(match_json["ipv4Src"])
                elif field_name == "dst_ip_addr":
                    self[field_name] = IPNetwork(match_json["ipv4Dst"])

                elif field_name == "ip_protocol":
                    self[field_name] = int(match_json["ipProto"])
                elif field_name == "tcp_destination_port":
                    self[field_name] = int(match_json["tcpDst"])
                elif field_name == "tcp_source_port":
                    self[field_name] = int(match_json["tcpSrc"])
                elif field_name == "udp_destination_port":
                    self[field_name] = int(match_json["udpDst"])
                elif field_name == "udp_source_port":
                    self[field_name] = int(match_json["udpSrc"])
                elif field_name == "vlan_id":
                    self[field_name] = int(match_json[u"vlanVid"])

            except (AttributeError, TypeError, ValueError):
                self[field_name] = sys.maxsize
                continue

    def add_element_from_ryu_match_json(self, match_json):

        for field_name in field_names:

            try:
                if field_name == "in_port":
                    try:
                        self[field_name] = int(match_json["in_port"])

                    except ValueError:
                        parsed_in_port = match_json["in-port"].split(":")[2]
                        self[field_name] = int(parsed_in_port)

                elif field_name == "ethernet_type":
                    self[field_name] = int(match_json["eth_type"])

                elif field_name == "ethernet_source":
                    mac_int = int(match_json[u"eth_src"].replace(":", ""), 16)
                    self[field_name] = mac_int

                elif field_name == "ethernet_destination":
                    mac_int = int(match_json[u"eth_dst"].replace(":", ""), 16)
                    self[field_name] = mac_int

                # TODO: Add graceful handling of IP addresses
                elif field_name == "src_ip_addr":
                    self[field_name] = IPNetwork(match_json["nw_src"])
                elif field_name == "dst_ip_addr":
                    self[field_name] = IPNetwork(match_json["nw_dst"])

                elif field_name == "ip_protocol":
                    self[field_name] = int(match_json["nw_proto"])
                elif field_name == "tcp_destination_port":

                    if match_json["nw_proto"] == 6:
                        self[field_name] = int(match_json["tp_dst"])
                    else:
                        self[field_name] = match_json["zzzz"]

                elif field_name == "tcp_source_port":

                    if match_json["nw_proto"] == 6:
                        self[field_name] = int(match_json["tp_src"])
                    else:
                        self[field_name] = match_json["zzzz"]

                elif field_name == "udp_destination_port":

                    if match_json["nw_proto"] == 17:
                        self[field_name] = int(match_json["tp_dst"])
                    else:
                        self[field_name] = match_json["zzzz"]

                elif field_name == "udp_source_port":

                    if match_json["nw_proto"] == 17:
                        self[field_name] = int(match_json["tp_src"])
                    else:
                        self[field_name] = match_json["zzzz"]

                elif field_name == "vlan_id":

                    if match_json[u"vlan_vid"] == "0x1000/0x1000":
                        self[field_name] = sys.maxsize
                        self["has_vlan_tag"] = 1
                    else:
                        self[field_name] = 0x1000 + int(match_json[u"vlan_vid"])
                        self["has_vlan_tag"] = 1

            except KeyError:
                self[field_name] = sys.maxsize

                if field_name == 'vlan_id':
                    self["has_vlan_tag"] = sys.maxsize

                continue

    def generate_onos_match_json(self, match_json, has_vlan_tag_check):

        match_json = []

        def get_onos_match_field_dict(field_name, val):
            match_field_dict = {"type": onos_field_names_mapping_reverse[field_name][0],
                                       onos_field_names_mapping_reverse[field_name][1]: val}
            return match_field_dict

        for field_name in field_names:

            if has_vlan_tag_check:
                if field_name == "vlan_id":
                    val = int("0x1000", 16)
                    match_json.append(get_onos_match_field_dict(field_name, val))

            if field_name in self and self[field_name] != sys.maxsize:

                if field_name == "ethernet_source" or field_name == "ethernet_destination":


                    mac_hex_str = hex(self[field_name])[2:]
                    if len(mac_hex_str) == 11:
                        mac_hex_str = "0" + mac_hex_str
                    mac_hex_str = str(':'.join(str(codecs.encode(s.encode('utf-8'), 'hex_codec'), 'utf-8') for s in bytes.fromhex(mac_hex_str).decode('utf-8')))
                    match_json.append(get_onos_match_field_dict(field_name, mac_hex_str))

                elif field_name == "ethernet_type":
                    eth_type_str = hex(self[field_name])
                    eth_type_str = eth_type_str[0:2] + "0" + eth_type_str[2:]
                    match_json.append(get_onos_match_field_dict(field_name, eth_type_str))
                else:
                    match_json.append(get_onos_match_field_dict(field_name, self[field_name]))

        return match_json

    def generate_sel_match_json(self, match):
        if "in_port" in self and self["in_port"] != sys.maxsize:
            # TODO(abhilash) check what does SEL want in case of port_in;
            # it errors out if you let the port number (self["port_in"]) pass
            # through as value. IPv4 keeps it quiet, but I am not subytesre if it
            # wants that.
            match.__setattr__("in_port", str(self["in_port"]))

        if "ethernet_type" in self and self["ethernet_type"] != sys.maxsize:
            # Picked up the values from
            # http://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers.xhtml
            match.__setattr__("eth_type", str(self["ethernet_type"]))

        if "ethernet_source" in self and self["ethernet_source"] != sys.maxsize:
            mac_int = self["ethernet_source"]
            mac_hex_str = hex(mac_int)[2:]
            mac_hex_str = str(':'.join(str(codecs.encode(s.encode('utf-8'), 'hex_codec'), 'utf-8') for s in bytes.fromhex(mac_hex_str).decode('utf-8')))
                    
            match.__setattr__("eth_src", mac_hex_str)

        if "ethernet_destination" in self and self["ethernet_destination"] != sys.maxsize:
            mac_int = self["ethernet_destination"]
            mac_hex_str = format(mac_int, "012x")
            mac_hex_str = str(':'.join(str(codecs.encode(s.encode('utf-8'), 'hex_codec'), 'utf-8') for s in bytes.fromhex(mac_hex_str).decode('utf-8')))
                    
            match.__setattr__("eth_dst", mac_hex_str)

        if "src_ip_addr" in self and self["src_ip_addr"] != sys.maxsize:
            match.__setattr__("ipv4_src", self["src_ip_addr"])

        if "dst_ip_addr" in self and self["dst_ip_addr"] != sys.maxsize:
            match.__setattr__("ipv4_dst", self["dst_ip_addr"])

        if ("tcp_destination_port" in self and self["tcp_destination_port"] != sys.maxsize) or \
                ("tcp_source_port" in self and self["tcp_source_port"] != sys.maxsize):
            self["ip_protocol"] = 6
            match.__setattr__("ip_proto", str(self["ip_protocol"]))

        if "tcp_destination_port" in self and self["tcp_destination_port"] != sys.maxsize:
            match.__setattr__("tcp_dst", self["tcp_destination_port"])

        if "tcp_source_port" in self and self["tcp_source_port"] != sys.maxsize:
            match.__setattr__("tcp_src", self["tcp_source_port"])

        if "udp_destination_port" in self and self["udp_destination_port"] != sys.maxsize:
            match.__setattr__("udp_dst", self["udp_destination_port"])

        if "udp_source_port" in self and self["udp_source_port"] != sys.maxsize:
            match.__setattr__("udp_src", self["udp_source_port"])

        if "vlan_id" in self and self["vlan_id"] != sys.maxsize:
            match.__setattr__("vlan_id", str(self["vlan_id"]))

        return match

    def generate_ryu_match_json(self, match_json, has_vlan_tag_check=False):

        for field_name in field_names:

            if has_vlan_tag_check:
                if field_name == "vlan_id":
                    match_json[ryu_field_names_mapping_reverse[field_name]] = "0x1000/0x1000"

            if field_name in self and self[field_name] != sys.maxsize:

                if field_name == "ethernet_source" or field_name == "ethernet_destination":

                    mac_hex_str = hex(self[field_name])[2:]
                    if len(mac_hex_str) == 11:
                        mac_hex_str = "0" + mac_hex_str

                    if len(mac_hex_str) == 1:
                        mac_hex_str = "00000000000" + mac_hex_str
                    elif len(mac_hex_str) == 2:
                        mac_hex_str = "0000000000" + mac_hex_str

                    mac_hex_str = str(':'.join(str(codecs.encode(s.encode('utf-8'), 'hex_codec'), 'utf-8') for s in bytes.fromhex(mac_hex_str).decode('utf-8')))
                    match_json[ryu_field_names_mapping_reverse[field_name]] = mac_hex_str

                else:
                    match_json[ryu_field_names_mapping_reverse[field_name]] = self[field_name]

        return match_json

    def generate_match_json(self, controller, match_json, has_vlan_tag_check=False):

        if controller == "ryu":
            return self.generate_ryu_match_json(match_json, has_vlan_tag_check)
        elif controller == "onos":
            return self.generate_onos_match_json(match_json, has_vlan_tag_check)
        elif controller == "sel":
            return self.generate_sel_match_json(match_json, has_vlan_tag_check)
        else:
            raise NotImplementedError

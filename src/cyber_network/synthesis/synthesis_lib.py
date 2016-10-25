__author__ = 'Rakesh Kumar'

import pprint
import time
import json
import os
import sys
import urllib

from model.match import Match

from collections import defaultdict


class SynthesisLib(object):

    def __init__(self, controller_host, controller_port, network_graph):

        self.network_graph = network_graph

        self.controller_host = controller_host
        self.controller_port = controller_port

        self.group_id_cntr = 1
        self.flow_id_cntr = 1
        self.queue_id_cntr = 1

        self.h = self.network_graph.network_configuration.h
        self.synthesized_primary_paths = defaultdict(defaultdict)
        self.synthesized_failover_paths = defaultdict(defaultdict)

        if self.network_graph.controller == "onos":
            self.onos_app_id = "50"
            self.delete_all_onos_rules()
            self.delete_all_onos_groups()
        elif self.network_graph.controller == "ryu":
            self.delete_all_ryu_rules()
        elif self.network_graph.controller == "sel":
            raise NotImplementedError

    def delete_all_onos_rules(self):
        remaining_url = "flows/application/" + self.onos_app_id
        url = self.network_graph.network_configuration.controller_api_base_url + remaining_url
        resp, content = self.h.request(url, "GET")

        prev_app_flows = json.loads(content)
        for flow in prev_app_flows["flows"]:
            remaining_url = "flows/" + urllib.quote(flow["deviceId"]) + "/" + flow["id"]
            url = self.network_graph.network_configuration.controller_api_base_url + remaining_url
            resp, content = self.h.request(url, "DELETE")

    def delete_all_onos_groups(self):
        remaining_url = "groups"
        url = self.network_graph.network_configuration.controller_api_base_url + remaining_url
        resp, content = self.h.request(url, "GET")
        prev_groups = json.loads(content)
        for group in prev_groups["groups"]:
            remaining_url = "groups/" + urllib.quote(group["deviceId"]) + "/" + group["appCookie"]
            url = self.network_graph.network_configuration.controller_api_base_url + remaining_url
            resp, content = self.h.request(url, "DELETE")

    def delete_all_ryu_rules(self):
        os.system("sudo ovs-vsctl -- --all destroy QoS")
        os.system("sudo ovs-vsctl -- --all destroy Queue")

    def record_primary_path(self, src_host, dst_host, switch_port_tuple_list):

        port_path = []

        for sw_name, ingress_port_number, egress_port_number in switch_port_tuple_list:
            port_path.append(sw_name + ":ingress" + str(ingress_port_number))
            port_path.append(sw_name + ":egress" + str(egress_port_number))

        self.synthesized_primary_paths[src_host.node_id][dst_host.node_id] = port_path

    def record_failover_path(self, src_host, dst_host, e, switch_port_tuple_list):

        port_path = []

        if src_host.node_id not in self.synthesized_failover_paths:
            if dst_host.node_id not in self.synthesized_failover_paths[src_host.node_id]:
                self.synthesized_failover_paths[src_host.node_id][dst_host.node_id] = defaultdict(defaultdict)
        else:
            if dst_host.node_id not in self.synthesized_failover_paths[src_host.node_id]:
                self.synthesized_failover_paths[src_host.node_id][dst_host.node_id] = defaultdict(defaultdict)

        for sw_name, ingress_port_number, egress_port_number in switch_port_tuple_list:
            port_path.append(sw_name + ":ingress" + str(ingress_port_number))
            port_path.append(sw_name + ":egress" + str(egress_port_number))

        self.synthesized_failover_paths[src_host.node_id][dst_host.node_id][e[0]][e[1]] = port_path

    def save_synthesized_paths(self, conf_path):
        with open(conf_path + "synthesized_primary_paths.json", "w") as outfile:
            json.dump(self.synthesized_primary_paths, outfile)

        with open(conf_path + "synthesized_failover_paths.json", "w") as outfile:
            json.dump(self.synthesized_failover_paths, outfile)

    def push_queue(self, sw, port, min_rate, max_rate):

        self.queue_id_cntr = self.queue_id_cntr + 1
        min_rate_str = str(min_rate * 1000000)
        max_rate_str = str(max_rate * 1000000)
        sw_port_str = sw + "-" + "eth" + str(port)

        queue_cmd = "sudo ovs-vsctl -- set Port " + sw_port_str + " qos=@newqos -- " + \
                    "--id=@newqos create QoS type=linux-htb other-config:max-rate=" + "1000000000" + \
                    " queues=" + str(self.queue_id_cntr) + "=@q" + str(self.queue_id_cntr) + " -- " + \
                    "--id=@q" + str(self.queue_id_cntr) + " create Queue other-config:min-rate=" + min_rate_str + \
                    " other-config:max-rate=" + max_rate_str

        os.system(queue_cmd)
        time.sleep(1)

        return self.queue_id_cntr

    def sel_get_node_id(self, switch):
        # for node in ConfigTree.nodesHttpAccess(self.sel_session).read_collection():
        for node in ConfigTree.NodesEntityAccess(self.sel_session).read_collection():
            if node.linked_key == "OpenFlow:{}".format(switch[1:]):
                return node.id

    def push_change(self, url, pushed_content):

        time.sleep(0.2)

        if self.network_graph.controller == "ryu":

            resp, content = self.h.request(url, "POST",
                                           headers={'Content-Type': 'application/json; charset=UTF-8'},
                                           body=json.dumps(pushed_content))

        elif self.network_graph.controller == "onos":

            resp, content = self.h.request(url, "POST",
                                           headers={'Content-Type': 'application/json; charset=UTF-8'},
                                           body=json.dumps(pushed_content))

        elif self.network_graph.controller == "sel":
            if isinstance(pushed_content, ConfigTree.Flow):
                # flows = ConfigTree.flowsHttpAccess(self.sel_session)
                flows = ConfigTree.FlowsEntityAccess(self.sel_session)
                pushed_content.node = self.sel_get_node_id(pushed_content.node)
                result = flows.create_single(pushed_content)
            elif isinstance(pushed_content, ConfigTree.Group):
                # groups = ConfigTree.groupsHttpAccess(self.sel_session)
                groups = ConfigTree.GroupsEntityAccess(self.sel_session)
                result = groups.create_single(pushed_content)
            else:
                raise NotImplementedError
        #resp = {"status": "200"}
        #pprint.pprint(pushed_content)
        if resp["status"].startswith("2"):
            print "Pushed Successfully:", pushed_content.keys()[0]
            #print resp["status"]
        else:
            print "Problem Pushing:", pushed_content.keys()[0]
            print "resp:", resp, "content:", content
            pprint.pprint(pushed_content)

    def create_ryu_flow_url(self):
        return "http://localhost:8080/stats/flowentry/add"

    def create_ryu_group_url(self):
        return "http://localhost:8080/stats/groupentry/add"

    def create_onos_flow_url(self, flow):
        flow_url = self.network_graph.network_configuration.controller_api_base_url + "flows/" + \
                   urllib.quote(flow["deviceId"]) + "?appId=" + self.onos_app_id

        return flow_url

    def create_onos_group_url(self, group):
        group_url = self.network_graph.network_configuration.controller_api_base_url + "groups/" + \
                    urllib.quote(group["deviceId"])

        return group_url

    def push_flow(self, sw, flow):

        url = None
        if self.network_graph.controller == "ryu":
            url = self.create_ryu_flow_url()

        elif self.network_graph.controller == "sel":
            flow.enabled = True

        elif self.network_graph.controller == "onos":
            url = self.create_onos_flow_url(flow)

        self.push_change(url, flow)

    def push_group(self, sw, group):

        url = None
        if self.network_graph.controller == "ryu":
            url = self.create_ryu_group_url()

        elif self.network_graph.controller == "sel":
            pass

        elif self.network_graph.controller == "onos":
            url = self.create_onos_group_url(group)

        else:
            raise NotImplementedError

        self.push_change(url, group)

    def create_base_flow(self, sw, table_id, priority):

        if self.network_graph.controller == "ryu":
            flow = dict()
            flow["dpid"] = sw[1:]
            flow["cookie"] = self.flow_id_cntr
            flow["cookie_mask"] = 1
            flow["table_id"] = table_id
            flow["idle_timeout"] = 0
            flow["hard_timeout"] = 0
            flow["priority"] = priority + 10
            flow["flags"] = 1
            flow["match"] = {}
            flow["instructions"] = []

        elif self.network_graph.controller == "sel":

            flow = ConfigTree.Flow()
            flow.node = sw
            flow.buffer_id = 0
            flow.cookie = self.flow_id_cntr
            flow.priority = priority + 10
            flow.table_id = table_id
            flow.error_state = ConfigTree.ErrorState.in_progress()

        elif self.network_graph.controller == "onos":
            flow = dict()
            flow["tableId"] = table_id
            flow["priority"] = priority + 10
            flow["timeout"] = 0
            flow["isPermanent"] = True
            flow["deviceId"] = self.network_graph.node_id_to_onos_sw_device_id_mapping(sw)
            flow["treatment"] = {"instructions": []}
            flow["selector"] = {"criteria": []}

        else:
            raise NotImplementedError

        self.flow_id_cntr += 1
        return flow

    def create_base_group(self, sw):

        if self.network_graph.controller == "ryu":
            group = dict()
            group["dpid"] = sw[1:]
            group["type"] = ""
            group["group_id"] = self.group_id_cntr
            group["buckets"] = []

        elif self.network_graph.controller == "sel":
            assert not sw == None
            group = ConfigTree.Group()
            group.id = str(self.group_id_cntr)
            group.group_id = self.group_id_cntr
            group.node = self.sel_get_node_id(sw)
            group.error_state=ConfigTree.ErrorState.in_progress()

        elif self.network_graph.controller == "onos":
            group = dict()
            group["type"] = ""
            group["appCookie"] = "0x32"
            group["groupId"] = str(self.group_id_cntr)
            group["buckets"] = []
            group["deviceId"] = self.network_graph.node_id_to_onos_sw_device_id_mapping(sw)
        else:
            raise NotImplementedError

        self.group_id_cntr += 1

        return group

    def populate_flow_action_instruction(self, flow, action_list, apply_immediately):

        if self.network_graph.controller == "ryu":

            if not action_list:
                flow["instructions"] = []
            else:

                if apply_immediately:
                    flow["instructions"] = [{"type": "APPLY_ACTIONS",
                                             "actions": action_list}]
                else:
                    flow["instructions"] = [{"type": "WRITE_ACTIONS",
                                             "actions": action_list}]

        elif self.network_graph.controller == "onos":
            if not action_list:
                flow["treatment"]["instructions"] = []
            else:

                if apply_immediately:
                    flow["treatment"]["instructions"] = action_list
                else:
                    raise NotImplementedError
                    flow["treatment"]["instructions"] = action_list

        elif self.network_graph.controller == "sel":
            instruction = ConfigTree.WriteActions()
            instruction.instruction_type = ConfigTree.OfpInstructionType.write_actions()
            for action in action_list:
                instruction.actions.append(action)
            flow.instructions.append(instruction)

            # if apply_immediately:
            #     instruction = ConfigTree.ApplyActions()
            #     instruction.instruction_type = "ApplyActions"
            #     # instruction.instruction_type = "WriteActions"
            #     # instruction.instruction_type = ConfigTree.OfpInstructionType.write_actions()
            #     for action in action_list:
            #         instruction.actions.append(action)
            # else:
            #     instruction = ConfigTree.WriteActions()
            #     instruction.instruction_type = ConfigTree.OfpInstructionType.write_actions()
            #     for action in action_list:
            #         instruction.actions.append(action)
            # flow.instructions.append(instruction)

        else:
            raise NotImplementedError

        return flow

    def push_table_miss_goto_next_table_flow(self, sw, table_id):

        # Create a lowest possible flow
        flow = self.create_base_flow(sw, table_id, 0)

        #Compile instruction
        #  Assert that packet be sent to table with this table_id + 1

        if self.network_graph.controller == "ryu":
            flow["instructions"] = [{"type": "GOTO_TABLE",  "table_id": str(table_id + 1)}]

        elif self.network_graph.controller == "sel":
            go_to_table_instruction = ConfigTree.GoToTable()
            go_to_table_instruction.instruction_type = "GotoTable"
            go_to_table_instruction.table_id = table_id + 1
            flow.instructions.append(go_to_table_instruction)

        elif self.network_graph.controller == "onos":
            flow["treatment"]["instructions"].append({"type": "TABLE", "tableId": table_id + 1})

        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

    def push_flow_with_group_and_set_vlan(self, sw, flow_match, table_id, vlan_id, group_id, priority, apply_immediately):

        flow = self.create_base_flow(sw, table_id, priority)

        if self.network_graph.controller == "ryu":
            flow["match"] = flow_match.generate_match_json(self.network_graph.controller, flow["match"],
                                                           has_vlan_tag_check=True)

            action_list = [{"type": "SET_FIELD", "field": "vlan_vid", "value": vlan_id + 0x1000},
                           {"type": "GROUP", "group_id": group_id}]

            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

        elif self.network_graph.controller == "sel":

            raise NotImplemented

            match = flow_match.generate_match_json(self.network_graph.controller, flow.match)
            group_action = ConfigTree.GroupAction()
            group_action.action_type = "Group"
            group_action.set_order = 0
            group_action.group_id = group_id
            flow.match = match

            set_vlan_id_action = ConfigTree.SetFieldAction()
            set_vlan_id_action.action_type = ConfigTree.OfpActionType.set_field()

            vlan_set_match = ConfigTree.VlanVid()
            vlan_set_match.value = str(vlan_id)

            set_vlan_id_action.field = vlan_set_match

            action_list = [set_vlan_id_action, group_action]

            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

        return flow

    def push_match_per_in_port_destination_instruct_group_flow(self, sw, table_id, group_id, priority,
                                                               flow_match, apply_immediately):

        flow = self.create_base_flow(sw, table_id, priority)

        if self.network_graph.controller == "ryu":
            flow["match"] = flow_match.generate_match_json(self.network_graph.controller, flow["match"])
            action_list = [{"type": "GROUP", "group_id": group_id}]
            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

        elif self.network_graph.controller == "onos":
            flow["selector"]["criteria"] = flow_match.generate_match_json(self.network_graph.controller,
                                                                          flow["selector"]["criteria"])
            action_list = [{"type": "GROUP", "groupId": group_id}]
            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

        elif self.network_graph.controller == "sel":
            match = flow_match.generate_match_json(self.network_graph.controller, flow.match)
            action = ConfigTree.GroupAction()
            action.action_type = "Group"
            action.set_order = 0
            action.group_id = group_id
            flow.match = match
            self.populate_flow_action_instruction(flow, [action], apply_immediately)

        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

        return flow

    def get_out_and_watch_port(self, intent):
        out_port = None
        watch_port = None

        if intent.in_port == intent.out_port:
            out_port = self.network_graph.OFPP_IN
            watch_port = intent.out_port
        else:
            out_port = intent.out_port
            watch_port = intent.out_port

        return out_port, watch_port

    def push_fast_failover_group(self, sw, primary_intent, failover_intent):

        group = self.create_base_group(sw)
        group_id = None

        if self.network_graph.controller == "ryu":

            group["type"] = "FF"

            bucket_primary = {}
            bucket_failover = {}

            out_port, watch_port = self.get_out_and_watch_port(primary_intent)
            bucket_primary["actions"] = [{"type": "OUTPUT", "port": out_port}]
            bucket_primary["watch_port"] = watch_port
            bucket_primary["watch_group"] = 4294967295

            out_port, watch_port = self.get_out_and_watch_port(failover_intent)
            bucket_failover["actions"] = [{"type": "OUTPUT", "port": out_port}]
            bucket_failover["watch_port"] = watch_port
            bucket_primary["watch_group"] = 4294967295

            group["buckets"] = [bucket_primary, bucket_failover]
            group_id = group["group_id"]

        elif self.network_graph.controller == "sel":

            group = self.create_base_group(sw)
            group.group_type = "FastFailover"
            out_port, watch_port = self.get_out_and_watch_port(primary_intent)

            bucket_primary = ConfigTree.Bucket()
            action = ConfigTree.OutputAction()
            action.action_type = ConfigTree.OfpActionType.output()
            action.out_port = out_port

            bucket_primary.actions.append(action)
            bucket_primary.watch_port = watch_port
            bucket_primary.id = "0"
            # No idea how to set the weight of this bucket.
            group.buckets.append(bucket_primary)

            out_port, watch_port = self.get_out_and_watch_port(failover_intent)
            bucket_failover = ConfigTree.Bucket()
            action = ConfigTree.OutputAction()
            action.action_type = ConfigTree.OfpActionType.output()
            action.out_port = out_port
            bucket_failover.actions.append(action)
            bucket_failover.watch_port = watch_port
            bucket_failover.id = "1"

            group.buckets.append(bucket_failover)
            group_id = group.group_id


        else:
            raise NotImplementedError

        self.push_group(sw, group)

        return group_id

    def push_fast_failover_group_set_vlan_action(self, sw, intent_list, set_vlan_tags):

        group = self.create_base_group(sw)
        group_id = None

        if self.network_graph.controller == "ryu":
            group["type"] = "FF"
            bucket_list = []
            for i in range(len(intent_list)):

                intent = intent_list[i]

                out_port, watch_port = self.get_out_and_watch_port(intent)
                bucket = {}
                bucket["actions"] = [{"type": "SET_FIELD", "field": "vlan_vid", "value": set_vlan_tags[i] + 0x1000},
                                     {"type": "OUTPUT", "port": out_port}]

                bucket["watch_port"] = watch_port
                bucket["watch_group"] = 4294967295
                bucket_list.append(bucket)

            group["buckets"] = bucket_list
            group_id = group["group_id"]

        elif self.network_graph.controller == "sel":

            raise NotImplemented

            group = self.create_base_group(sw)
            group.group_type = "FastFailover"
            out_port, watch_port = self.get_out_and_watch_port(primary_intent)

            bucket_primary = ConfigTree.Bucket()
            action = ConfigTree.OutputAction()
            action.action_type = ConfigTree.OfpActionType.output()
            action.out_port = out_port

            bucket_primary.actions.append(action)
            bucket_primary.watch_port = watch_port
            bucket_primary.id = "0"
            # No idea how to set the weight of this bucket.
            group.buckets.append(bucket_primary)

            out_port, watch_port = self.get_out_and_watch_port(failover_intent)
            bucket_failover = ConfigTree.Bucket()
            action = ConfigTree.OutputAction()
            action.action_type = ConfigTree.OfpActionType.output()
            action.out_port = out_port
            bucket_failover.actions.append(action)
            bucket_failover.watch_port = watch_port
            bucket_failover.id = "1"

            group.buckets.append(bucket_failover)
            group_id = group.group_id

        else:
            raise NotImplementedError

        self.push_group(sw, group)

        return group_id

    def push_select_all_group(self, sw, intent_list):

        if not intent_list:
            raise Exception("Need to have either one or two forwarding intents")

        group = self.create_base_group(sw)
        group_id = None

        if self.network_graph.controller == "ryu":
            group["type"] = "ALL"
            group["buckets"] = []

            for intent in intent_list:
                this_bucket = {}

                output_action = {"type": "OUTPUT", "port": intent.out_port}

                if intent.min_rate and intent.max_rate:
                    q_id = self.push_queue(sw, intent.out_port, intent.min_rate, intent.max_rate)
                    enqueue_action = {"type": "SET_QUEUE", "queue_id": q_id, "port": intent.out_port}
                    action_list = [enqueue_action, output_action]
                    this_bucket["actions"] = [output_action]
                else:
                    action_list = [output_action]

                this_bucket["actions"] = action_list
                group["buckets"].append(this_bucket)

            group_id = group["group_id"]

        elif self.network_graph.controller == "onos":
            group["type"] = "ALL"
            for intent in intent_list:
                this_bucket = {"treatment": {"instructions": [{"type": "OUTPUT", "port": intent.out_port}]}}
                group["buckets"].append(this_bucket)

            group_id = group["groupId"]

        elif self.network_graph.controller == "sel":
            group.group_type = "All"
            for intent in intent_list:
                out_port, watch_port = self.get_out_and_watch_port(intent)
                action = ConfigTree.OutputAction()
                action.out_port = out_port
                action.action_type =ConfigTree.OfpActionType.output()
                action.max_length = 65535
                bucket = ConfigTree.Bucket()
                bucket.actions.append(action)
                bucket.watch_port = 4294967295
                bucket.watch_group = 4294967295
                group.buckets.append(bucket)
            group_id = group.group_id
        else:
            raise NotImplementedError
        self.push_group(sw, group)

        return group_id

    def push_select_all_group_set_vlan_action(self, sw, intent_list, modified_tag):

        if not intent_list:
            raise Exception("Need to have either one or two forwarding intents")

        group = self.create_base_group(sw)
        group_id = None

        if self.network_graph.controller == "ryu":
            group["type"] = "ALL"
            group["buckets"] = []

            for intent in intent_list:
                this_bucket = {}

                set_vlan_action = {"type": "SET_FIELD", "field": "vlan_vid", "value": modified_tag + 0x1000}
                output_action = {"type": "OUTPUT", "port": intent.out_port}

                action_list = [set_vlan_action, output_action]

                this_bucket["actions"] = action_list
                group["buckets"].append(this_bucket)

            group_id = group["group_id"]

        elif self.network_graph.controller == "sel":
            raise NotImplemented
        else:
            raise NotImplementedError

        self.push_group(sw, group)

        return group_id

    def push_destination_host_mac_intent_flow(self, sw, mac_intent, table_id, priority):

        mac_intent.flow_match["vlan_id"] = sys.maxsize
        flow = self.create_base_flow(sw, table_id, priority)

        output_action = None

        if self.network_graph.controller == "ryu":
            flow["match"] = mac_intent.flow_match.generate_match_json(self.network_graph.controller, flow["match"])
            output_action = {"type": "OUTPUT", "port": mac_intent.out_port}

            action_list = [output_action]

            self.populate_flow_action_instruction(flow, action_list, mac_intent.apply_immediately)
            self.push_flow(sw, flow)

        elif self.network_graph.controller == "onos":
            flow["selector"]["criteria"] = mac_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                                     flow["selector"]["criteria"])
            output_action = {"type": "OUTPUT", "port": mac_intent.out_port}
            action_list = [output_action]
            self.populate_flow_action_instruction(flow, action_list, mac_intent.apply_immediately)
            self.push_flow(sw, flow)

        elif self.network_graph.controller == "sel":
            raise NotImplementedError

        return flow

    def push_destination_host_mac_vlan_intent_flow(self, sw, mac_intent, table_id, priority):

        flow = self.create_base_flow(sw, table_id, priority)

        pop_vlan_action = None
        output_action = None

        if self.network_graph.controller == "ryu":
            flow["match"] = mac_intent.flow_match.generate_match_json(self.network_graph.controller, flow["match"],
                                                                      has_vlan_tag_check=True)
            pop_vlan_action = {"type": "POP_VLAN"}
            output_action = {"type": "OUTPUT", "port": mac_intent.out_port}

        elif self.network_graph.controller == "sel":
            flow.match = mac_intent.flow_match.generate_match_json(self.network_graph.controller, flow.match)
            pop_vlan_action = ConfigTree.PopVlanAction()
            pop_vlan_action.action_type = ConfigTree.OfpActionType.pop_vlan()

            output_action = ConfigTree.OutputAction()
            output_action.out_port = mac_intent.out_port
            output_action.action_type = ConfigTree.OfpActionType.output()

        elif self.network_graph.controller == "onos":
            flow["selector"]["criteria"] = mac_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                                     flow["selector"]["criteria"],
                                                                                     has_vlan_tag_check=True)
            pop_vlan_action = {"type": "L2MODIFICATION", "subtype": "VLAN_POP"}
            output_action = {"type": "OUTPUT", "port": mac_intent.out_port}

        else:
            raise NotImplementedError

        action_list = None
        if mac_intent.min_rate and mac_intent.max_rate:
            q_id = self.push_queue(sw, mac_intent.out_port, mac_intent.min_rate, mac_intent.max_rate)
            if self.network_graph.controller == "ryu":
                enqueue_action = {"type": "SET_QUEUE", "queue_id": q_id, "port": mac_intent.out_port}
                action_list = [pop_vlan_action, enqueue_action, output_action]
        else:
            action_list = [pop_vlan_action, output_action]

        self.populate_flow_action_instruction(flow, action_list, mac_intent.apply_immediately)
        self.push_flow(sw, flow)

        return flow

    def push_destination_host_mac_intents(self, sw, mac_intents, mac_forwarding_table_id, pop_vlan=True):

        if mac_intents:

            if len(mac_intents) > 1:
                print "There are more than one mac intents for a single dst, will install only one"

            if pop_vlan:
                self.push_destination_host_mac_vlan_intent_flow(sw,
                                                                mac_intents[0],
                                                                mac_forwarding_table_id,
                                                                100)

            self.push_destination_host_mac_intent_flow(sw, mac_intents[0], mac_forwarding_table_id, 10)

    def push_vlan_tagged_table_jump_rule(self, sw, flow_match, src_table, dst_table):
        flow = self.create_base_flow(sw, src_table, 1)

        if self.network_graph.controller == "ryu":
            flow["match"] = flow_match.generate_match_json(self.network_graph.controller,
                                                           flow["match"],
                                                           has_vlan_tag_check=True)

            flow["instructions"] = [{"type": "GOTO_TABLE",  "table_id": str(dst_table)}]

        elif self.network_graph.controller == "onos":
            flow["selector"]["criteria"] = flow_match.generate_match_json(self.network_graph.controller,
                                                                          flow["selector"]["criteria"],
                                                                          has_vlan_tag_check=True)

            flow["treatment"]["instructions"].append({"type": "TABLE", "tableId": dst_table})

        elif self.network_graph.controller == "sel":
            raise NotImplementedError
        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

    def push_flow_vlan_tag(self, sw, flow_match, vlan_tag_push_rules_table_id, apply_immediately):

        flow = self.create_base_flow(sw, vlan_tag_push_rules_table_id, 1)

        # Compile instructions
        if self.network_graph.controller == "ryu":

            # Compile match
            flow["match"] = flow_match.generate_match_json(self.network_graph.controller, flow["match"])

            action_list = [{"type": "PUSH_VLAN", "ethertype": 0x8100}]

            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

            flow["instructions"].append({"type": "GOTO_TABLE", "table_id": str(vlan_tag_push_rules_table_id + 1)})

        elif self.network_graph.controller == "sel":

            raise NotImplemented

            flow.match = flow_match.generate_match_json(self.network_graph.controller, flow.match)

            vlan_set_match = ConfigTree.VlanVid()
            vlan_set_match.value = str(push_vlan_intent.required_vlan_id)

            push_vlan_action = ConfigTree.PushVlanAction()
            push_vlan_action.ether_type = 0x8100
            push_vlan_action.action_type = ConfigTree.OfpActionType.push_vlan()

            go_to_table_instruction = ConfigTree.GoToTable()
            go_to_table_instruction.instruction_type = ConfigTree.OfpInstructionType.goto_table()
            go_to_table_instruction.table_id = str(vlan_tag_push_rules_table_id + 1)

            flow.instructions.append(go_to_table_instruction)
            action_list = [push_vlan_action]
            self.populate_flow_action_instruction(flow, action_list, apply_immediately)

        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

    def push_vlan_push_intents(self, sw, push_vlan_intents, vlan_tag_push_rules_table_id):

        for push_vlan_intent in push_vlan_intents:
            flow = self.create_base_flow(sw, vlan_tag_push_rules_table_id, 1)

            # Compile instructions
            if self.network_graph.controller == "ryu":

                # Compile match
                flow["match"] = push_vlan_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                                flow["match"])

                action_list = [{"type": "PUSH_VLAN", "ethertype": 0x8100},
                               {"type": "SET_FIELD", "field": "vlan_vid", "value": push_vlan_intent.required_vlan_id + 0x1000}]

                self.populate_flow_action_instruction(flow, action_list, push_vlan_intent.apply_immediately)

                flow["instructions"].append({"type": "GOTO_TABLE", "table_id": str(vlan_tag_push_rules_table_id + 1)})

            elif self.network_graph.controller == "sel":
                flow.match = push_vlan_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                             flow.match)
                set_vlan_id_action = ConfigTree.SetFieldAction()
                set_vlan_id_action.action_type = ConfigTree.OfpActionType.set_field()

                vlan_set_match = ConfigTree.VlanVid()
                vlan_set_match.value = str(push_vlan_intent.required_vlan_id)

                set_vlan_id_action.field = vlan_set_match

                push_vlan_action = ConfigTree.PushVlanAction()
                push_vlan_action.ether_type = 0x8100
                push_vlan_action.action_type = ConfigTree.OfpActionType.push_vlan()

                go_to_table_instruction = ConfigTree.GoToTable()
                go_to_table_instruction.instruction_type = ConfigTree.OfpInstructionType.goto_table()
                go_to_table_instruction.table_id = str(vlan_tag_push_rules_table_id + 1)

                flow.instructions.append(go_to_table_instruction)
                action_list = [push_vlan_action, set_vlan_id_action]
                self.populate_flow_action_instruction(flow, action_list, push_vlan_intent.apply_immediately)

            else:
                raise NotImplementedError

            self.push_flow(sw, flow)

    def push_vlan_push_intents_2(self, sw, push_vlan_intent, vlan_tag_push_rules_table_id, group_id, apply_immediately):

        flow = self.create_base_flow(sw, vlan_tag_push_rules_table_id, 1)

        # Compile instructions
        if self.network_graph.controller == "ryu":

            flow["match"] = push_vlan_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                            flow["match"])

            action_list = [{"type": "PUSH_VLAN", "ethertype": 0x8100},
                           {"type": "SET_FIELD", "field": "vlan_vid", "value": push_vlan_intent.required_vlan_id + 0x1000},
                           {"type": "GROUP", "group_id": group_id}]


            self.populate_flow_action_instruction(flow, action_list, push_vlan_intent.apply_immediately)

        elif self.network_graph.controller == "onos":
            flow["selector"]["criteria"] = push_vlan_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                            flow["selector"]["criteria"])

            action_list = [{"type": "L2MODIFICATION", "subtype": "VLAN_PUSH"},
                           {"type": "L2MODIFICATION", "subtype": "VLAN_ID", "vlanId": push_vlan_intent.required_vlan_id},
                           {"type": "GROUP", "groupId": group_id}]

            self.populate_flow_action_instruction(flow, action_list, push_vlan_intent.apply_immediately)

        elif self.network_graph.controller == "sel":
            flow.match = push_vlan_intent.flow_match.generate_match_json(self.network_graph.controller,
                                                                         flow.match)
            set_vlan_id_action = ConfigTree.SetFieldAction()
            set_vlan_id_action.action_type = ConfigTree.OfpActionType.set_field()

            vlan_set_match = ConfigTree.VlanVid()
            vlan_set_match.value = str(push_vlan_intent.required_vlan_id)

            set_vlan_id_action.field = vlan_set_match

            push_vlan_action = ConfigTree.PushVlanAction()
            push_vlan_action.ether_type = 0x8100
            push_vlan_action.action_type = ConfigTree.OfpActionType.push_vlan()

            group_action = ConfigTree.GroupAction()
            group_action.action_type = "Group"
            group_action.set_order = 0
            group_action.group_id = group_id

            action_list = [push_vlan_action, set_vlan_id_action, group_action]
            self.populate_flow_action_instruction(flow, action_list, push_vlan_intent.apply_immediately)

        else:
            raise NotImplementedError

        self.push_flow(sw, flow)

    def push_mac_acl_rules(self, sw, table_number, src_host, dst_host):

        # Get a vanilla flow with an empty action list so it can be dropped
        flow = self.create_base_flow(sw, table_number, 100)
        action_list = []

        # Make and push the flow
        if self.network_graph.controller == "ryu":
            flow["match"]["eth_src"] = src_host.mac_addr
            flow["match"]["eth_dst"] = dst_host.mac_addr
        else:
            raise NotImplemented

        self.populate_flow_action_instruction(flow, action_list, True)
        self.push_flow(sw, flow)

    def push_loop_preventing_drop_rules(self, sw, table_number):

        for h_id in self.network_graph.host_ids:

            # Get concerned only with hosts that are directly connected to this sw
            h_obj = self.network_graph.get_node_object(h_id)
            if h_obj.sw.node_id != sw:
                continue

            # Get a vanilla flow
            flow = self.create_base_flow(sw, table_number, 100)
            action_list = []

            # Compile match with in_port and destination mac address
            if self.network_graph.controller == "ryu":
                flow["match"]["in_port"] = h_obj.switch_port.port_number
                flow["match"]["eth_dst"] = h_obj.mac_addr

            elif self.network_graph.controller == "onos":

                flow_match = Match(is_wildcard=True)
                flow_match["ethernet_type"] = 0x0800
                mac_int = int(h_obj.mac_addr.replace(":", ""), 16)
                flow_match["ethernet_destination"] = int(mac_int)
                flow_match["in_port"] = int(h_obj.switch_port.port_number)

                flow["selector"]["criteria"] = flow_match.generate_match_json(self.network_graph.controller,
                                                                              flow["selector"]["criteria"])

            elif self.network_graph.controller == "sel":
                flow.match.in_port = str(h_obj.switch_port.port_number)
                flow.match.eth_dst = h_obj.mac_addr

                drop_action = ConfigTree.Action()
                drop_action.action_type = "Drop"
                # Empty list for drop action
                action_list = [drop_action]
            #    action_list = []

            # Make and push the flow
            self.populate_flow_action_instruction(flow, action_list, True)
            self.push_flow(sw, flow)

    def push_host_vlan_tagged_packets_drop_rules(self, sw, host_vlan_tagged_drop_table):

        for h_id in self.network_graph.host_ids:

            # Get concerned only with hosts that are directly connected to this sw
            h_obj = self.network_graph.get_node_object(h_id)
            if h_obj.sw.node_id != sw:
                continue

            # Get a vanilla flow
            flow = self.create_base_flow(sw, host_vlan_tagged_drop_table, 100)
            action_list = []

            if self.network_graph.controller == "ryu":
                flow["match"]["in_port"] = h_obj.switch_port.port_number
                flow["match"]["vlan_vid"] = self.network_graph.graph.node[sw]["sw"].synthesis_tag

            elif self.network_graph.controller == "onos":
                flow_match = Match(is_wildcard=True)
                flow_match["ethernet_type"] = 0x0800
                flow_match["in_port"] = int(h_obj.switch_port.port_number)
                flow_match["vlan_id"] = self.network_graph.graph.node[sw]["sw"].synthesis_tag

                flow["selector"]["criteria"] = flow_match.generate_match_json(self.network_graph.controller,
                                                                              flow["selector"]["criteria"])

            elif self.network_graph.controller == "sel":
                raise NotImplementedError

            # Make and push the flow
            self.populate_flow_action_instruction(flow, action_list, True)
            self.push_flow(sw, flow)
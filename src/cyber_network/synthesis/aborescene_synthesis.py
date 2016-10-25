__author__ = 'Rakesh Kumar'

import networkx as nx
import sys

from collections import defaultdict
from copy import deepcopy
from synthesis.synthesis_lib import SynthesisLib
from model.intent import Intent


class AboresceneSynthesis(object):

    def __init__(self, params):

        self.network_graph = None
        self.synthesis_lib = None

        self.params = params

        # VLAN tag constitutes 12 bits.
        # We use 2 left most bits for representing the tree_id
        # And the 10 right most bits for representing the destination switch's id
        self.num_bits_for_k = 2
        self.num_bits_for_switches = 10

        self.apply_group_intents_immediately = params["apply_group_intents_immediately"]

        self.sw_intent_lists = defaultdict(defaultdict)

        # As a packet arrives, these are the tables it is evaluated against, in this order:

        # If the packet belongs to a local host, just pop any tags and send it along.
        self.local_mac_forwarding_rules = 0

        # Rules for taking packets arriving from other switches with vlan tags.
        self.other_switch_vlan_tagged_packet_rules = 1

        # If the packet belongs to some other switch, compute the vlan tag based on the destination switch
        # and the tree that would be used and send it along to next table
        self.tree_vlan_tag_push_rules = 2

        # Use the vlan tag as a match and forward using appropriate tree
        self.aborescene_forwarding_rules = 3

    def __str__(self):
        params_str = ''
        for k, v in self.params.items():
            params_str += "_" + str(k) + "_" + str(v)
        return self.__class__.__name__ + params_str

    def compute_shortest_path_tree(self, dst_sw):

        spt = nx.DiGraph()

        mdg = self.network_graph.get_mdg()

        paths = nx.shortest_path(mdg, source=dst_sw.node_id)

        for src in paths:

            if src == dst_sw.node_id:
                continue

            for i in range(len(paths[src]) - 1):
                spt.add_edge(paths[src][i], paths[src][i+1])

        return spt

    def compute_k_edge_disjoint_aborescenes(self, k, dst_sw):

        k_eda = []

        mdg = self.network_graph.get_mdg()

        dst_sw_preds = list(mdg.predecessors(dst_sw.node_id))
        dst_sw_succs = list(mdg.successors(dst_sw.node_id))

        # Remove the predecessor edges to dst_sw, to make it the "root"
        for pred in dst_sw_preds:
            mdg.remove_edge(pred, dst_sw.node_id)

        # Initially, remove all successors edges of dst_sw as well
        for succ in dst_sw_succs:
            mdg.remove_edge(dst_sw.node_id, succ)

        for i in range(k):

            # Assume there are always k edges as the successor of the dst_sw, kill all but one
            for j in range(k):
                if i == j:
                    mdg.add_edge(dst_sw.node_id, dst_sw_succs[j])
                else:
                    if mdg.has_edge(dst_sw.node_id, dst_sw_succs[j]):
                        mdg.remove_edge(dst_sw.node_id, dst_sw_succs[j])

            # Compute and store one
            msa = nx.minimum_spanning_arborescence(mdg)
            k_eda.append(msa)

            # If there are predecessors of dst_sw now, we could not find k msa, so break
            if len(list(msa.predecessors(dst_sw.node_id))) > 0:
                print "Could not find k msa."
                break

            # Remove its arcs from mdg
            for arc in msa.edges():
                mdg.remove_edge(arc[0], arc[1])

        return k_eda

    def compute_sw_intent_lists(self, dst_sw, flow_match, tree, tree_id):
        for src_n in tree:
            src_sw = self.network_graph.get_node_object(src_n)
            for pred in tree.predecessors(src_n):
                link_port_dict = self.network_graph.get_link_ports_dict(src_n, pred)
                out_port = link_port_dict[src_n]

                intent = Intent("primary", flow_match, "all", out_port)
                intent.tree_id = tree_id

                if src_sw in self.sw_intent_lists:
                    if dst_sw in self.sw_intent_lists[src_sw]:
                        self.sw_intent_lists[src_sw][dst_sw].append(intent)
                    else:
                        self.sw_intent_lists[src_sw][dst_sw] = [intent]
                else:
                    self.sw_intent_lists[src_sw][dst_sw] = [intent]

    def install_failover_group_vlan_tag_flow(self, src_sw, dst_sw, k):

        # Tags: as they are applied to packets leaving on a given tree in the failover buckets.
        modified_tags = []
        for i in range(k):
            modified_tags.append(int(dst_sw.synthesis_tag) | (i + 1 << self.num_bits_for_switches))

        sw_intent_list = deepcopy(self.sw_intent_lists[src_sw][dst_sw])

        # Push a fail-over group with each bucket containing a modify VLAN tag action,
        # Each one of these buckets represent actions to be applied to send the packet in one tree
        group_id = self.synthesis_lib.push_fast_failover_group_set_vlan_action(src_sw.node_id,
                                                                               sw_intent_list,
                                                                               modified_tags)

        # Push a group/vlan_id setting flow rule
        flow_match = deepcopy(sw_intent_list[0].flow_match)
        flow_match["vlan_id"] = int(dst_sw.synthesis_tag) | (1 << self.num_bits_for_switches)

        flow = self.synthesis_lib.push_match_per_in_port_destination_instruct_group_flow(
                src_sw.node_id,
                self.aborescene_forwarding_rules,
                group_id,
                1,
                flow_match,
                self.apply_group_intents_immediately)

        # Need to install some more rules to handle the IN_PORT as out_port case.
        for adjacent_sw_id, link_data in self.network_graph.get_adjacent_switch_link_data(src_sw.node_id):

            sw_intent_list = deepcopy(self.sw_intent_lists[src_sw][dst_sw])

            # If the intent is such that it is sending the packet back out to the adjacent switch...
            if sw_intent_list[1].out_port == link_data.link_ports_dict[src_sw.node_id]:

                # Push a fail-over group with each bucket containing a modify VLAN tag action,
                # Each one of these buckets represent actions to be applied to send the packet in one tree

                sw_intent_list[1].in_port = link_data.link_ports_dict[src_sw.node_id]
                group_id = self.synthesis_lib.push_fast_failover_group_set_vlan_action(src_sw.node_id,
                                                                                       sw_intent_list,
                                                                                       modified_tags)

                # Push a group/vlan_id setting flow rule
                flow_match = deepcopy(sw_intent_list[0].flow_match)
                flow_match["vlan_id"] = int(dst_sw.synthesis_tag) | (1 << self.num_bits_for_switches)
                flow_match["in_port"] = link_data.link_ports_dict[src_sw.node_id]

                flow = self.synthesis_lib.push_match_per_in_port_destination_instruct_group_flow(
                        src_sw.node_id,
                        self.aborescene_forwarding_rules,
                        group_id,
                        2,
                        flow_match,
                        self.apply_group_intents_immediately)

    def install_all_group_vlan_tag_flow(self, src_sw, dst_sw, k):

        # Tags: as they are applied to packets leaving on a given tree in the failover buckets.
        modified_tag = int(dst_sw.synthesis_tag) | (2 << self.num_bits_for_switches)

        sw_intent_list = [self.sw_intent_lists[src_sw][dst_sw][1]]

        # Push a failover group with each bucket containing a modify VLAN tag action,
        # Each one of these buckets represent actions to be applied to send the packet in one tree
        group_id = self.synthesis_lib.push_select_all_group_set_vlan_action(src_sw.node_id,
                                                                            sw_intent_list,
                                                                            modified_tag)

        # Push a group/vlan_id setting flow rule
        flow_match = deepcopy(sw_intent_list[0].flow_match)
        flow_match["vlan_id"] = int(dst_sw.synthesis_tag) | (2 << self.num_bits_for_switches)

        flow = self.synthesis_lib.push_match_per_in_port_destination_instruct_group_flow(
                src_sw.node_id,
                self.aborescene_forwarding_rules,
                group_id,
                1,
                flow_match,
                self.apply_group_intents_immediately)

    def push_sw_intent_lists(self, flow_match, k):

        for src_sw in self.sw_intent_lists:
            print "-- Pushing at Switch:", src_sw.node_id
            for dst_sw in self.sw_intent_lists[src_sw]:

                # Install the rules to put the vlan tags on for hosts that are at this destination switch
                self.push_src_sw_vlan_push_intents(src_sw, dst_sw, flow_match)
                self.install_failover_group_vlan_tag_flow(src_sw, dst_sw, k)
                self.install_all_group_vlan_tag_flow(src_sw, dst_sw, k)

    def push_src_sw_vlan_push_intents(self, src_sw, dst_sw, flow_match):
        for h_obj in dst_sw.attached_hosts:
            host_flow_match = deepcopy(flow_match)
            mac_int = int(h_obj.mac_addr.replace(":", ""), 16)
            host_flow_match["ethernet_destination"] = int(mac_int)
            host_flow_match["vlan_id"] = sys.maxsize
            host_flow_match["in_port"] = sys.maxsize

            push_vlan_tag_intent = Intent("push_vlan", host_flow_match, "all", "all")

            push_vlan_tag_intent.required_vlan_id = int(dst_sw.synthesis_tag) | (1 << self.num_bits_for_switches)

            self.synthesis_lib.push_vlan_push_intents(src_sw.node_id,
                                                      [push_vlan_tag_intent],
                                                      self.tree_vlan_tag_push_rules)

    def push_local_mac_forwarding_rules_rules(self, sw, flow_match):

        for h_obj in sw.attached_hosts:
            host_flow_match = deepcopy(flow_match)
            mac_int = int(h_obj.mac_addr.replace(":", ""), 16)
            host_flow_match["ethernet_destination"] = int(mac_int)

            edge_ports_dict = self.network_graph.get_link_ports_dict(h_obj.sw.node_id, h_obj.node_id)
            out_port = edge_ports_dict[h_obj.sw.node_id]
            host_mac_intent = Intent("mac", host_flow_match, "all", out_port)

            self.synthesis_lib.push_destination_host_mac_intents(sw.node_id,
                                                                 [host_mac_intent],
                                                                 self.local_mac_forwarding_rules)

    def push_other_switch_vlan_tagged_packet_rules(self, sw, flow_match):

        table_jump_flow_match = deepcopy(flow_match)

        self.synthesis_lib.push_vlan_tagged_table_jump_rule(sw.node_id,
                                                            flow_match,
                                                            self.other_switch_vlan_tagged_packet_rules,
                                                            self.aborescene_forwarding_rules)

    def synthesize_all_switches(self, flow_match, k):

        for sw in self.network_graph.get_switches():

            # Push table switch rules
            self.synthesis_lib.push_table_miss_goto_next_table_flow(sw.node_id, self.local_mac_forwarding_rules)
            self.synthesis_lib.push_table_miss_goto_next_table_flow(sw.node_id, self.other_switch_vlan_tagged_packet_rules)
            self.synthesis_lib.push_table_miss_goto_next_table_flow(sw.node_id, self.tree_vlan_tag_push_rules)

            self.push_other_switch_vlan_tagged_packet_rules(sw, flow_match)

            if sw.attached_hosts:

                self.push_local_mac_forwarding_rules_rules(sw, flow_match)

                k_eda = self.compute_k_edge_disjoint_aborescenes(k, sw)

                for i in range(k):
                    self.compute_sw_intent_lists(sw, flow_match, k_eda[i], i+1)

        self.push_sw_intent_lists(flow_match, k)
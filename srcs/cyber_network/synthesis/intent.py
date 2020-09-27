__author__ = 'Rakesh Kumar'


class Intent:

    def __init__(self, intent_type, flow_match, in_port, out_port, apply_immediately=True,
                 min_rate=None, max_rate=None):

        self.intent_type = intent_type
        self.flow_match = flow_match
        self.in_port = in_port
        self.out_port = out_port
        self.min_rate = min_rate
        self.max_rate = max_rate

        self.tree_id = None
        self.required_vlan_id = None
        self.hash_value = hash(str(self.in_port) + str(self.out_port) + str(self.flow_match))

        self.apply_immediately = apply_immediately

        self.src_host = None
        self.dst_host = None

        self.consolidated_in_a_failover_group = False

    def __hash__(self):
        return self.hash_value

    def __eq__(self, other):
        if other:
            return self.hash_value == other.hash_value
        else:
            return False

    def __str__(self):
        return "Hash Value: " + str(self.hash_value) + " " +\
               "Intent Type: " + str(self.intent_type) + " " + \
               "Flow Match: " + str(self.flow_match) + " " + \
               "In Port: " + str(self.in_port) + " " + \
               "Out Port: " + str(self.out_port)
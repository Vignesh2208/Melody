__author__ = 'Rakesh Kumar'

from action_set import Action, ActionSet


class Bucket:
    def __init__(self, sw, bucket_json, group):

        self.sw = sw
        self.action_list = []
        self.watch_port = None

        self.weight = None
        self.group = group

        if self.sw.network_graph.controller == "onos":
            for action_json in bucket_json["treatment"]["instructions"]:
                self.action_list.append(Action(sw, action_json))

            if "weight" in bucket_json:
                self.weight = str(bucket_json["weight"])

        elif self.sw.network_graph.controller == "sel":
            self.bucket_id = bucket_json['id']

            for action_json in bucket_json["actions"]:
                self.action_list.append(Action(sw, action_json))

            if "watchPort" in bucket_json:
                if bucket_json["watchPort"] != 4294967293:
                    self.watch_port = str(bucket_json["watchPort"])

            if "weight" in bucket_json:
                self.weight = str(bucket_json["weight"])

            self.action_list = sorted(self.action_list, key=lambda action: action.order)

        elif self.sw.network_graph.controller == "ryu":

            for action_json in bucket_json["actions"]:
                self.action_list.append(Action(sw, action_json))

            if "watch_port" in bucket_json:
                if bucket_json["watch_port"] != 4294967295:
                    self.watch_port = self.sw.ports[int(bucket_json["watch_port"])]

            if "weight" in bucket_json:
                self.weight = str(bucket_json["weight"])

        else:
            raise NotImplementedError

        for action in self.action_list:
            action.bucket = self

        self.action_set = ActionSet(self.sw)
        self.action_set.add_all_actions(self.action_list)

    def is_live(self):

        # Check if the watch port is up.
        if self.watch_port:
            return self.watch_port.state == "up"

        # If no watch_port was specified, then assume the bucket is always live
        else:
            return True

    def prior_failed_ports(self):

        prior_failed_ports = []
        i = 0

        while i < len(self.group.bucket_list):

            if self == self.group.bucket_list[i]:
                break

            prior_failed_ports.append(int(self.group.bucket_list[i].watch_port.port_number))
            i += 1

        return prior_failed_ports

    def prior_active_watch_ports(self):
        prior_active_watch_ports = []
        i = 0

        while i < len(self.group.bucket_list):

            if self == self.group.bucket_list[i]:
                break

            prior_watch_port = self.group.bucket_list[i].watch_port
            if prior_watch_port.state == "up":
                prior_active_watch_ports.append(prior_watch_port)

            i += 1

        return prior_active_watch_ports


class Group:
    '''
    As per OF1.3 specification:

    A switch is not required to support all group types, just those marked "Required" below.

    The controller can also query the switch about which of the "Optional" group type it supports.
    Required: all:      Execute all buckets in the group. This group is used for multi-cast or broadcast forwarding.
                        The packet is effectively cloned for each bucket; one packet is processed for each bucket of the
                        group. If a bucket directs a packet explicitly out the ingress port, this packet clone is dropped.
                        If the controller writer wants to forward out the ingress port, the group should include an extra
                        bucket which includes an output action to the OFPP_IN_PORT reserved port.
    Optional: select:   Execute one bucket in the group. Packets are processed by a single bucket in the group,
                        based on a switch-computed selection algorithm (e.g. hash on some user-configured tuple or
                        simple round robin). All configuration and state for the selection algorithm is external to
                        OpenFlow. The selection algorithm should implement equal load sharing and can optionally be
                        based on bucket weights. When a port specified in a bucket in a select group goes down,
                        the switch may restrict bucket selection to the remaining set (those with forwarding actions
                        to live ports) instead of dropping packets destined to that port. This behavior may reduce
                        the disruption of a downed link or switch.

    Required: indirect: Execute the one defined bucket in this group. This group supports only a single bucket.
                        Allows multiple flow entries or groups to point to a common group identifier, supporting
                        faster, more efficient convergence.

    Optional: ff:       Execute the first live bucket. Each action bucket is associated with a specific port and/or
                        group that controls its liveness. The buckets are evaluated in the order defined by the group,
                        and the first bucket which is associated with a live port/group is selected. This group type
                        enables the switch to change forwarding without requiring a round trip to the controller.
                        If no buckets are live, packets are dropped.
    '''

    def __init__(self, sw, group_json):

        self.sw = sw
        self.bucket_list = []

        if self.sw.network_graph.controller == "odl":
            self.group_id = group_json["group-id"]
            self.group_type = group_json["group-type"]

            if group_json["group-type"] == "group-ff":
                self.group_type = self.sw.network_graph.GROUP_FF
            elif group_json["group-type"] == "group-all":
                self.group_type = self.sw.network_graph.GROUP_ALL

            for bucket_json in group_json["buckets"]["bucket"]:
                self.bucket_list.append(Bucket(sw, bucket_json, self))

            #  Sort the bucket_list by bucket-id
            self.bucket_list = sorted(self.bucket_list, key=lambda bucket: bucket.bucket_id)

            # Initialize the active bucket
            self.set_active_bucket()

        elif self.sw.network_graph.controller == "ryu":
            self.group_id = group_json["group_id"]

            if group_json["type"] == u"ALL":
                self.group_type = self.sw.network_graph.GROUP_ALL
            elif group_json["type"] == u"FF":
                self.group_type = self.sw.network_graph.GROUP_FF

            for bucket_json in group_json["buckets"]:
                self.bucket_list.append(Bucket(sw, bucket_json, self))

        elif self.sw.network_graph.controller == "onos":

            self.group_id = self.sw.network_graph.parse_onos_group_id(group_json["id"])
            if group_json["type"] == "ALL":
                self.group_type = self.sw.network_graph.GROUP_ALL
            else:
                raise NotImplementedError

            for bucket_json in group_json["buckets"]:
                self.bucket_list.append(Bucket(sw, bucket_json, self))

        elif self.sw.network_graph.controller == "sel":
            self.group_id = group_json["groupId"]
            self.group_type = group_json["groupType"]

            if group_json["groupType"] == u"FastFailover":
                self.group_type = self.sw.network_graph.GROUP_FF
            elif group_json["groupType"] == u"All":
                self.group_type = self.sw.network_graph.GROUP_ALL

            for bucket_json in group_json["buckets"]:
                self.bucket_list.append(Bucket(sw, bucket_json, self))

            self.bucket_list = sorted(self.bucket_list, key=lambda bucket: bucket.bucket_id)

        if self.group_type == self.sw.network_graph.GROUP_FF:
                self.active_bucket = self.bucket_list[0]

    def get_action_list(self):
        action_list = []

        # If it is a _all_ group, collect all buckets
        if self.group_type == self.sw.network_graph.GROUP_ALL:

            for action_bucket in self.bucket_list:
                action_list.extend(action_bucket.action_list)

        # If it is a fast-failover group, collect the bucket which is active
        elif self.group_type == self.sw.network_graph.GROUP_FF:

            # Add all actions, set the vuln ranks
            i = 0
            while i < len(self.bucket_list):
                this_bucket = self.bucket_list[i]

                for action in this_bucket.action_list:
                    action.vuln_rank = i

                action_list.extend(this_bucket.action_list)

                i += 1

        return action_list

    def get_first_live_bucket(self):

        for bucket in self.bucket_list:
            if bucket.is_live():
                return bucket

        return None

    def set_active_bucket(self):
        self.active_bucket = self.get_first_live_bucket()


class GroupTable:

    def __init__(self, sw, groups_json):

        self.sw = sw
        self.groups = {}

        for group_json in groups_json:
            grp = Group(sw, group_json)
            self.groups[int(grp.group_id)] = grp
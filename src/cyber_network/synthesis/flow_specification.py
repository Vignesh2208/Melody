

class FlowSpecification:
    def __init__(self, src_host_id, dst_host_id, flow_match):
        self.src_host_id = src_host_id
        self.dst_host_id = dst_host_id
        self.flow_match = flow_match

        self.ng_src_host = None
        self.ng_dst_host = None

        self.mn_src_host = None
        self.mn_dst_host = None



class FlowSpecification:
    def __init__(self, src_host_id, dst_host_id, flow_match):
        self.src_host_id = src_host_id
        self.dst_host_id = dst_host_id
        self.configured_rate = configured_rate
        self.flow_match = flow_match

        self.measurement_rates = measurement_rates
        self.tests_duration = tests_duration

        # Store per_rate, list of measurements, each representing a list containing values per iteration
        self.measurements = defaultdict(list)

        self.ng_src_host = None
        self.ng_dst_host = None

        self.mn_src_host = None
        self.mn_dst_host = None

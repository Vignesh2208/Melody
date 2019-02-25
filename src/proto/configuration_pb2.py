# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: configuration.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import pss_pb2 as pss__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='configuration.proto',
  package='melody_configuration',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x13\x63onfiguration.proto\x12\x14melody_configuration\x1a\tpss.proto\"\xa6\x01\n\x11TopologyParameter\x12\x16\n\x0eparameter_name\x18\x01 \x02(\t\x12\x1e\n\x16parameter_value_string\x18\x02 \x01(\t\x12\x1b\n\x13parameter_value_int\x18\x03 \x01(\x05\x12\x1e\n\x16parameter_value_double\x18\x04 \x01(\x01\x12\x1c\n\x14parameter_value_bool\x18\x05 \x01(\x08\"\xf4\x01\n\x1b\x43yberEmulationSpecification\x12\x15\n\rtopology_name\x18\x01 \x02(\t\x12\x11\n\tnum_hosts\x18\x02 \x02(\x05\x12\x14\n\x0cnum_switches\x18\x03 \x02(\x05\x12$\n\x1cinter_switch_link_latency_ms\x18\x04 \x02(\x05\x12#\n\x1bhost_switch_link_latency_ms\x18\x05 \x02(\x05\x12J\n\x19\x61\x64\x64itional_topology_param\x18\x06 \x03(\x0b\x32\'.melody_configuration.TopologyParameter\"Y\n\x11MappedApplication\x12\x16\n\x0e\x61pplication_id\x18\x01 \x02(\t\x12\x17\n\x0f\x61pplication_src\x18\x02 \x02(\t\x12\x13\n\x0blisten_port\x18\x03 \x02(\x05\"\x85\x01\n\x10\x43yberPhysicalMap\x12\x17\n\x0f\x63yber_host_name\x18\x01 \x02(\t\x12\x43\n\x12mapped_application\x18\x02 \x03(\x0b\x32\'.melody_configuration.MappedApplication\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\"\xa8\x01\n\x0e\x42\x61\x63kGroundFlow\x12\x18\n\x10src_cyber_entity\x18\x01 \x02(\t\x12\x18\n\x10\x64st_cyber_entity\x18\x02 \x02(\t\x12\x19\n\x11\x63md_to_run_at_src\x18\x03 \x02(\t\x12\x19\n\x11\x63md_to_run_at_dst\x18\x04 \x02(\t\x12\x17\n\x0f\x66low_start_time\x18\x05 \x02(\x05\x12\x13\n\x0b\x64\x65scription\x18\x06 \x01(\t\"\\\n\x0ePcapReplayFlow\x12\x1d\n\x15involved_cyber_entity\x18\x01 \x03(\t\x12\x16\n\x0epcap_file_path\x18\x02 \x02(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\"\xb3\x02\n\x14ProjectConfiguration\x12\x14\n\x0cproject_name\x18\x01 \x02(\t\x12O\n\x14\x63yber_emulation_spec\x18\x02 \x02(\x0b\x32\x31.melody_configuration.CyberEmulationSpecification\x12\x42\n\x12\x63yber_physical_map\x18\x03 \x03(\x0b\x32&.melody_configuration.CyberPhysicalMap\x12\x35\n\x07\x62g_flow\x18\x04 \x03(\x0b\x32$.melody_configuration.BackGroundFlow\x12\x39\n\x0breplay_flow\x18\x05 \x03(\x0b\x32$.melody_configuration.PcapReplayFlow\"H\n\x0c\x44isturbances\x12\x38\n\x0b\x64isturbance\x18\x01 \x03(\x0b\x32#.melody_powersim_proto.WriteRequest')
  ,
  dependencies=[pss__pb2.DESCRIPTOR,])




_TOPOLOGYPARAMETER = _descriptor.Descriptor(
  name='TopologyParameter',
  full_name='melody_configuration.TopologyParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='parameter_name', full_name='melody_configuration.TopologyParameter.parameter_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parameter_value_string', full_name='melody_configuration.TopologyParameter.parameter_value_string', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parameter_value_int', full_name='melody_configuration.TopologyParameter.parameter_value_int', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parameter_value_double', full_name='melody_configuration.TopologyParameter.parameter_value_double', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parameter_value_bool', full_name='melody_configuration.TopologyParameter.parameter_value_bool', index=4,
      number=5, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=57,
  serialized_end=223,
)


_CYBEREMULATIONSPECIFICATION = _descriptor.Descriptor(
  name='CyberEmulationSpecification',
  full_name='melody_configuration.CyberEmulationSpecification',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='topology_name', full_name='melody_configuration.CyberEmulationSpecification.topology_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='num_hosts', full_name='melody_configuration.CyberEmulationSpecification.num_hosts', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='num_switches', full_name='melody_configuration.CyberEmulationSpecification.num_switches', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='inter_switch_link_latency_ms', full_name='melody_configuration.CyberEmulationSpecification.inter_switch_link_latency_ms', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='host_switch_link_latency_ms', full_name='melody_configuration.CyberEmulationSpecification.host_switch_link_latency_ms', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='additional_topology_param', full_name='melody_configuration.CyberEmulationSpecification.additional_topology_param', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=226,
  serialized_end=470,
)


_MAPPEDAPPLICATION = _descriptor.Descriptor(
  name='MappedApplication',
  full_name='melody_configuration.MappedApplication',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='application_id', full_name='melody_configuration.MappedApplication.application_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='application_src', full_name='melody_configuration.MappedApplication.application_src', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='listen_port', full_name='melody_configuration.MappedApplication.listen_port', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=472,
  serialized_end=561,
)


_CYBERPHYSICALMAP = _descriptor.Descriptor(
  name='CyberPhysicalMap',
  full_name='melody_configuration.CyberPhysicalMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cyber_host_name', full_name='melody_configuration.CyberPhysicalMap.cyber_host_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='mapped_application', full_name='melody_configuration.CyberPhysicalMap.mapped_application', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='melody_configuration.CyberPhysicalMap.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=564,
  serialized_end=697,
)


_BACKGROUNDFLOW = _descriptor.Descriptor(
  name='BackGroundFlow',
  full_name='melody_configuration.BackGroundFlow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='src_cyber_entity', full_name='melody_configuration.BackGroundFlow.src_cyber_entity', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dst_cyber_entity', full_name='melody_configuration.BackGroundFlow.dst_cyber_entity', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cmd_to_run_at_src', full_name='melody_configuration.BackGroundFlow.cmd_to_run_at_src', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cmd_to_run_at_dst', full_name='melody_configuration.BackGroundFlow.cmd_to_run_at_dst', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='flow_start_time', full_name='melody_configuration.BackGroundFlow.flow_start_time', index=4,
      number=5, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='melody_configuration.BackGroundFlow.description', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=700,
  serialized_end=868,
)


_PCAPREPLAYFLOW = _descriptor.Descriptor(
  name='PcapReplayFlow',
  full_name='melody_configuration.PcapReplayFlow',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='involved_cyber_entity', full_name='melody_configuration.PcapReplayFlow.involved_cyber_entity', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pcap_file_path', full_name='melody_configuration.PcapReplayFlow.pcap_file_path', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='melody_configuration.PcapReplayFlow.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=870,
  serialized_end=962,
)


_PROJECTCONFIGURATION = _descriptor.Descriptor(
  name='ProjectConfiguration',
  full_name='melody_configuration.ProjectConfiguration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='project_name', full_name='melody_configuration.ProjectConfiguration.project_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cyber_emulation_spec', full_name='melody_configuration.ProjectConfiguration.cyber_emulation_spec', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cyber_physical_map', full_name='melody_configuration.ProjectConfiguration.cyber_physical_map', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bg_flow', full_name='melody_configuration.ProjectConfiguration.bg_flow', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='replay_flow', full_name='melody_configuration.ProjectConfiguration.replay_flow', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=965,
  serialized_end=1272,
)


_DISTURBANCES = _descriptor.Descriptor(
  name='Disturbances',
  full_name='melody_configuration.Disturbances',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='disturbance', full_name='melody_configuration.Disturbances.disturbance', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1274,
  serialized_end=1346,
)

_CYBEREMULATIONSPECIFICATION.fields_by_name['additional_topology_param'].message_type = _TOPOLOGYPARAMETER
_CYBERPHYSICALMAP.fields_by_name['mapped_application'].message_type = _MAPPEDAPPLICATION
_PROJECTCONFIGURATION.fields_by_name['cyber_emulation_spec'].message_type = _CYBEREMULATIONSPECIFICATION
_PROJECTCONFIGURATION.fields_by_name['cyber_physical_map'].message_type = _CYBERPHYSICALMAP
_PROJECTCONFIGURATION.fields_by_name['bg_flow'].message_type = _BACKGROUNDFLOW
_PROJECTCONFIGURATION.fields_by_name['replay_flow'].message_type = _PCAPREPLAYFLOW
_DISTURBANCES.fields_by_name['disturbance'].message_type = pss__pb2._WRITEREQUEST
DESCRIPTOR.message_types_by_name['TopologyParameter'] = _TOPOLOGYPARAMETER
DESCRIPTOR.message_types_by_name['CyberEmulationSpecification'] = _CYBEREMULATIONSPECIFICATION
DESCRIPTOR.message_types_by_name['MappedApplication'] = _MAPPEDAPPLICATION
DESCRIPTOR.message_types_by_name['CyberPhysicalMap'] = _CYBERPHYSICALMAP
DESCRIPTOR.message_types_by_name['BackGroundFlow'] = _BACKGROUNDFLOW
DESCRIPTOR.message_types_by_name['PcapReplayFlow'] = _PCAPREPLAYFLOW
DESCRIPTOR.message_types_by_name['ProjectConfiguration'] = _PROJECTCONFIGURATION
DESCRIPTOR.message_types_by_name['Disturbances'] = _DISTURBANCES
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TopologyParameter = _reflection.GeneratedProtocolMessageType('TopologyParameter', (_message.Message,), dict(
  DESCRIPTOR = _TOPOLOGYPARAMETER,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.TopologyParameter)
  ))
_sym_db.RegisterMessage(TopologyParameter)

CyberEmulationSpecification = _reflection.GeneratedProtocolMessageType('CyberEmulationSpecification', (_message.Message,), dict(
  DESCRIPTOR = _CYBEREMULATIONSPECIFICATION,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.CyberEmulationSpecification)
  ))
_sym_db.RegisterMessage(CyberEmulationSpecification)

MappedApplication = _reflection.GeneratedProtocolMessageType('MappedApplication', (_message.Message,), dict(
  DESCRIPTOR = _MAPPEDAPPLICATION,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.MappedApplication)
  ))
_sym_db.RegisterMessage(MappedApplication)

CyberPhysicalMap = _reflection.GeneratedProtocolMessageType('CyberPhysicalMap', (_message.Message,), dict(
  DESCRIPTOR = _CYBERPHYSICALMAP,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.CyberPhysicalMap)
  ))
_sym_db.RegisterMessage(CyberPhysicalMap)

BackGroundFlow = _reflection.GeneratedProtocolMessageType('BackGroundFlow', (_message.Message,), dict(
  DESCRIPTOR = _BACKGROUNDFLOW,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.BackGroundFlow)
  ))
_sym_db.RegisterMessage(BackGroundFlow)

PcapReplayFlow = _reflection.GeneratedProtocolMessageType('PcapReplayFlow', (_message.Message,), dict(
  DESCRIPTOR = _PCAPREPLAYFLOW,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.PcapReplayFlow)
  ))
_sym_db.RegisterMessage(PcapReplayFlow)

ProjectConfiguration = _reflection.GeneratedProtocolMessageType('ProjectConfiguration', (_message.Message,), dict(
  DESCRIPTOR = _PROJECTCONFIGURATION,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.ProjectConfiguration)
  ))
_sym_db.RegisterMessage(ProjectConfiguration)

Disturbances = _reflection.GeneratedProtocolMessageType('Disturbances', (_message.Message,), dict(
  DESCRIPTOR = _DISTURBANCES,
  __module__ = 'configuration_pb2'
  # @@protoc_insertion_point(class_scope:melody_configuration.Disturbances)
  ))
_sym_db.RegisterMessage(Disturbances)


# @@protoc_insertion_point(module_scope)

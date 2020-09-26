# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pss.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pss.proto',
  package='melody_powersim_proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n\tpss.proto\x12\x15melody_powersim_proto\"G\n\x06Status\x12\n\n\x02id\x18\x01 \x02(\t\x12\x31\n\x06status\x18\x02 \x02(\x0e\x32!.melody_powersim_proto.StatusType\"%\n\x08Response\x12\n\n\x02id\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\"W\n\x07Request\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0f\n\x07objtype\x18\x02 \x02(\t\x12\r\n\x05objid\x18\x03 \x02(\t\x12\x11\n\tfieldtype\x18\x04 \x02(\t\x12\r\n\x05value\x18\x05 \x02(\t\"Q\n\x0bReadRequest\x12\x11\n\ttimestamp\x18\x01 \x02(\t\x12/\n\x07request\x18\x02 \x03(\x0b\x32\x1e.melody_powersim_proto.Request\"A\n\x0cReadResponse\x12\x31\n\x08response\x18\x01 \x03(\x0b\x32\x1f.melody_powersim_proto.Response\"R\n\x0cWriteRequest\x12\x11\n\ttimestamp\x18\x01 \x02(\t\x12/\n\x07request\x18\x02 \x03(\x0b\x32\x1e.melody_powersim_proto.Request\"<\n\x0bWriteStatus\x12-\n\x06status\x18\x01 \x03(\x0b\x32\x1d.melody_powersim_proto.Status\"\x1c\n\x0eProcessRequest\x12\n\n\x02id\x18\x01 \x02(\t*4\n\nStatusType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\r\n\tSUCCEEDED\x10\x01\x12\n\n\x06\x46\x41ILED\x10\x02\x32\xff\x01\n\x03pss\x12Q\n\x04read\x12\".melody_powersim_proto.ReadRequest\x1a#.melody_powersim_proto.ReadResponse\"\x00\x12R\n\x05write\x12#.melody_powersim_proto.WriteRequest\x1a\".melody_powersim_proto.WriteStatus\"\x00\x12Q\n\x07process\x12%.melody_powersim_proto.ProcessRequest\x1a\x1d.melody_powersim_proto.Status\"\x00'
)

_STATUSTYPE = _descriptor.EnumDescriptor(
  name='StatusType',
  full_name='melody_powersim_proto.StatusType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUCCEEDED', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FAILED', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=563,
  serialized_end=615,
)
_sym_db.RegisterEnumDescriptor(_STATUSTYPE)

StatusType = enum_type_wrapper.EnumTypeWrapper(_STATUSTYPE)
UNKNOWN = 0
SUCCEEDED = 1
FAILED = 2



_STATUS = _descriptor.Descriptor(
  name='Status',
  full_name='melody_powersim_proto.Status',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='melody_powersim_proto.Status.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='melody_powersim_proto.Status.status', index=1,
      number=2, type=14, cpp_type=8, label=2,
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
  serialized_start=36,
  serialized_end=107,
)


_RESPONSE = _descriptor.Descriptor(
  name='Response',
  full_name='melody_powersim_proto.Response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='melody_powersim_proto.Response.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='melody_powersim_proto.Response.value', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=109,
  serialized_end=146,
)


_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='melody_powersim_proto.Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='melody_powersim_proto.Request.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='objtype', full_name='melody_powersim_proto.Request.objtype', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='objid', full_name='melody_powersim_proto.Request.objid', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fieldtype', full_name='melody_powersim_proto.Request.fieldtype', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='melody_powersim_proto.Request.value', index=4,
      number=5, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=148,
  serialized_end=235,
)


_READREQUEST = _descriptor.Descriptor(
  name='ReadRequest',
  full_name='melody_powersim_proto.ReadRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='melody_powersim_proto.ReadRequest.timestamp', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request', full_name='melody_powersim_proto.ReadRequest.request', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=237,
  serialized_end=318,
)


_READRESPONSE = _descriptor.Descriptor(
  name='ReadResponse',
  full_name='melody_powersim_proto.ReadResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='response', full_name='melody_powersim_proto.ReadResponse.response', index=0,
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
  serialized_start=320,
  serialized_end=385,
)


_WRITEREQUEST = _descriptor.Descriptor(
  name='WriteRequest',
  full_name='melody_powersim_proto.WriteRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='melody_powersim_proto.WriteRequest.timestamp', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request', full_name='melody_powersim_proto.WriteRequest.request', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=387,
  serialized_end=469,
)


_WRITESTATUS = _descriptor.Descriptor(
  name='WriteStatus',
  full_name='melody_powersim_proto.WriteStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='melody_powersim_proto.WriteStatus.status', index=0,
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
  serialized_start=471,
  serialized_end=531,
)


_PROCESSREQUEST = _descriptor.Descriptor(
  name='ProcessRequest',
  full_name='melody_powersim_proto.ProcessRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='melody_powersim_proto.ProcessRequest.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=533,
  serialized_end=561,
)

_STATUS.fields_by_name['status'].enum_type = _STATUSTYPE
_READREQUEST.fields_by_name['request'].message_type = _REQUEST
_READRESPONSE.fields_by_name['response'].message_type = _RESPONSE
_WRITEREQUEST.fields_by_name['request'].message_type = _REQUEST
_WRITESTATUS.fields_by_name['status'].message_type = _STATUS
DESCRIPTOR.message_types_by_name['Status'] = _STATUS
DESCRIPTOR.message_types_by_name['Response'] = _RESPONSE
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['ReadRequest'] = _READREQUEST
DESCRIPTOR.message_types_by_name['ReadResponse'] = _READRESPONSE
DESCRIPTOR.message_types_by_name['WriteRequest'] = _WRITEREQUEST
DESCRIPTOR.message_types_by_name['WriteStatus'] = _WRITESTATUS
DESCRIPTOR.message_types_by_name['ProcessRequest'] = _PROCESSREQUEST
DESCRIPTOR.enum_types_by_name['StatusType'] = _STATUSTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Status = _reflection.GeneratedProtocolMessageType('Status', (_message.Message,), {
  'DESCRIPTOR' : _STATUS,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.Status)
  })
_sym_db.RegisterMessage(Status)

Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSE,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.Response)
  })
_sym_db.RegisterMessage(Response)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), {
  'DESCRIPTOR' : _REQUEST,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.Request)
  })
_sym_db.RegisterMessage(Request)

ReadRequest = _reflection.GeneratedProtocolMessageType('ReadRequest', (_message.Message,), {
  'DESCRIPTOR' : _READREQUEST,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.ReadRequest)
  })
_sym_db.RegisterMessage(ReadRequest)

ReadResponse = _reflection.GeneratedProtocolMessageType('ReadResponse', (_message.Message,), {
  'DESCRIPTOR' : _READRESPONSE,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.ReadResponse)
  })
_sym_db.RegisterMessage(ReadResponse)

WriteRequest = _reflection.GeneratedProtocolMessageType('WriteRequest', (_message.Message,), {
  'DESCRIPTOR' : _WRITEREQUEST,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.WriteRequest)
  })
_sym_db.RegisterMessage(WriteRequest)

WriteStatus = _reflection.GeneratedProtocolMessageType('WriteStatus', (_message.Message,), {
  'DESCRIPTOR' : _WRITESTATUS,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.WriteStatus)
  })
_sym_db.RegisterMessage(WriteStatus)

ProcessRequest = _reflection.GeneratedProtocolMessageType('ProcessRequest', (_message.Message,), {
  'DESCRIPTOR' : _PROCESSREQUEST,
  '__module__' : 'pss_pb2'
  # @@protoc_insertion_point(class_scope:melody_powersim_proto.ProcessRequest)
  })
_sym_db.RegisterMessage(ProcessRequest)



_PSS = _descriptor.ServiceDescriptor(
  name='pss',
  full_name='melody_powersim_proto.pss',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=618,
  serialized_end=873,
  methods=[
  _descriptor.MethodDescriptor(
    name='read',
    full_name='melody_powersim_proto.pss.read',
    index=0,
    containing_service=None,
    input_type=_READREQUEST,
    output_type=_READRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='write',
    full_name='melody_powersim_proto.pss.write',
    index=1,
    containing_service=None,
    input_type=_WRITEREQUEST,
    output_type=_WRITESTATUS,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='process',
    full_name='melody_powersim_proto.pss.process',
    index=2,
    containing_service=None,
    input_type=_PROCESSREQUEST,
    output_type=_STATUS,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PSS)

DESCRIPTOR.services_by_name['pss'] = _PSS

# @@protoc_insertion_point(module_scope)

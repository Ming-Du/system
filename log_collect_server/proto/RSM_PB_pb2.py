# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: RSM_PB.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import header_pb2 as header__pb2
import RoadsideSafetyMessage_PB_pb2 as RoadsideSafetyMessage__PB__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='RSM_PB.proto',
  package='common',
  syntax='proto2',
  serialized_pb=_b('\n\x0cRSM_PB.proto\x12\x06\x63ommon\x1a\x0cheader.proto\x1a\x1eRoadsideSafetyMessage_PB.proto\"\\\n\x06RSM_PB\x12\x32\n\x08rsmFrame\x18\x01 \x02(\x0b\x32 .common.RoadsideSafetyMessage_PB\x12\x1e\n\x06header\x18\x02 \x01(\x0b\x32\x0e.common.Header')
  ,
  dependencies=[header__pb2.DESCRIPTOR,RoadsideSafetyMessage__PB__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_RSM_PB = _descriptor.Descriptor(
  name='RSM_PB',
  full_name='common.RSM_PB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='rsmFrame', full_name='common.RSM_PB.rsmFrame', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='header', full_name='common.RSM_PB.header', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=162,
)

_RSM_PB.fields_by_name['rsmFrame'].message_type = RoadsideSafetyMessage__PB__pb2._ROADSIDESAFETYMESSAGE_PB
_RSM_PB.fields_by_name['header'].message_type = header__pb2._HEADER
DESCRIPTOR.message_types_by_name['RSM_PB'] = _RSM_PB

RSM_PB = _reflection.GeneratedProtocolMessageType('RSM_PB', (_message.Message,), dict(
  DESCRIPTOR = _RSM_PB,
  __module__ = 'RSM_PB_pb2'
  # @@protoc_insertion_point(class_scope:common.RSM_PB)
  ))
_sym_db.RegisterMessage(RSM_PB)


# @@protoc_insertion_point(module_scope)

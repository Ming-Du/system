# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: RoadsideSafetyMessage_PB.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import String_PB_pb2 as String__PB__pb2
import Position3D_PB_pb2 as Position3D__PB__pb2
import ParticipantList_PB_pb2 as ParticipantList__PB__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='RoadsideSafetyMessage_PB.proto',
  package='common',
  syntax='proto2',
  serialized_pb=_b('\n\x1eRoadsideSafetyMessage_PB.proto\x12\x06\x63ommon\x1a\x0fString_PB.proto\x1a\x13Position3D_PB.proto\x1a\x18ParticipantList_PB.proto\"\x94\x01\n\x18RoadsideSafetyMessage_PB\x12\x0e\n\x06msgCnt\x18\x01 \x02(\x03\x12\x16\n\x02id\x18\x02 \x02(\x0b\x32\n.String_PB\x12\x1e\n\x06refPos\x18\x03 \x02(\x0b\x32\x0e.Position3D_PB\x12\x30\n\x0cparticipants\x18\x04 \x02(\x0b\x32\x1a.common.ParticipantList_PB')
  ,
  dependencies=[String__PB__pb2.DESCRIPTOR,Position3D__PB__pb2.DESCRIPTOR,ParticipantList__PB__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_ROADSIDESAFETYMESSAGE_PB = _descriptor.Descriptor(
  name='RoadsideSafetyMessage_PB',
  full_name='common.RoadsideSafetyMessage_PB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='msgCnt', full_name='common.RoadsideSafetyMessage_PB.msgCnt', index=0,
      number=1, type=3, cpp_type=2, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='common.RoadsideSafetyMessage_PB.id', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='refPos', full_name='common.RoadsideSafetyMessage_PB.refPos', index=2,
      number=3, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='participants', full_name='common.RoadsideSafetyMessage_PB.participants', index=3,
      number=4, type=11, cpp_type=10, label=2,
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
  serialized_start=107,
  serialized_end=255,
)

_ROADSIDESAFETYMESSAGE_PB.fields_by_name['id'].message_type = String__PB__pb2._STRING_PB
_ROADSIDESAFETYMESSAGE_PB.fields_by_name['refPos'].message_type = Position3D__PB__pb2._POSITION3D_PB
_ROADSIDESAFETYMESSAGE_PB.fields_by_name['participants'].message_type = ParticipantList__PB__pb2._PARTICIPANTLIST_PB
DESCRIPTOR.message_types_by_name['RoadsideSafetyMessage_PB'] = _ROADSIDESAFETYMESSAGE_PB

RoadsideSafetyMessage_PB = _reflection.GeneratedProtocolMessageType('RoadsideSafetyMessage_PB', (_message.Message,), dict(
  DESCRIPTOR = _ROADSIDESAFETYMESSAGE_PB,
  __module__ = 'RoadsideSafetyMessage_PB_pb2'
  # @@protoc_insertion_point(class_scope:common.RoadsideSafetyMessage_PB)
  ))
_sym_db.RegisterMessage(RoadsideSafetyMessage_PB)


# @@protoc_insertion_point(module_scope)
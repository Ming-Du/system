# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ParticipantList_PB.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import ParticipantData_PB_pb2 as ParticipantData__PB__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ParticipantList_PB.proto',
  package='common',
  syntax='proto2',
  serialized_pb=_b('\n\x18ParticipantList_PB.proto\x12\x06\x63ommon\x1a\x18ParticipantData_PB.proto\"I\n\x12ParticipantList_PB\x12\x33\n\x0fparticipantData\x18\x01 \x03(\x0b\x32\x1a.common.ParticipantData_PB')
  ,
  dependencies=[ParticipantData__PB__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PARTICIPANTLIST_PB = _descriptor.Descriptor(
  name='ParticipantList_PB',
  full_name='common.ParticipantList_PB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='participantData', full_name='common.ParticipantList_PB.participantData', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=62,
  serialized_end=135,
)

_PARTICIPANTLIST_PB.fields_by_name['participantData'].message_type = ParticipantData__PB__pb2._PARTICIPANTDATA_PB
DESCRIPTOR.message_types_by_name['ParticipantList_PB'] = _PARTICIPANTLIST_PB

ParticipantList_PB = _reflection.GeneratedProtocolMessageType('ParticipantList_PB', (_message.Message,), dict(
  DESCRIPTOR = _PARTICIPANTLIST_PB,
  __module__ = 'ParticipantList_PB_pb2'
  # @@protoc_insertion_point(class_scope:common.ParticipantList_PB)
  ))
_sym_db.RegisterMessage(ParticipantList_PB)


# @@protoc_insertion_point(module_scope)

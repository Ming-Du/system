# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lightstate.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='lightstate.proto',
  package='lightstate',
  syntax='proto2',
  serialized_pb=_b('\n\x10lightstate.proto\x12\nlightstate\"&\n\x05state\x12\r\n\x05\x63olor\x18\x01 \x01(\t\x12\x0e\n\x06remain\x18\x02 \x01(\x05')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_STATE = _descriptor.Descriptor(
  name='state',
  full_name='lightstate.state',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='color', full_name='lightstate.state.color', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='remain', full_name='lightstate.state.remain', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=32,
  serialized_end=70,
)

DESCRIPTOR.message_types_by_name['state'] = _STATE

state = _reflection.GeneratedProtocolMessageType('state', (_message.Message,), dict(
  DESCRIPTOR = _STATE,
  __module__ = 'lightstate_pb2'
  # @@protoc_insertion_point(class_scope:lightstate.state)
  ))
_sym_db.RegisterMessage(state)


# @@protoc_insertion_point(module_scope)
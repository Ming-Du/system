# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: trajectory_agent_sync_status.proto

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


DESCRIPTOR = _descriptor.FileDescriptor(
  name='trajectory_agent_sync_status.proto',
  package='trajectory_agent',
  syntax='proto2',
  serialized_pb=_b('\n\"trajectory_agent_sync_status.proto\x12\x10trajectory_agent\x1a\x0cheader.proto\"P\n\x19TrajectoryAgentSyncStatus\x12\x1e\n\x06header\x18\x01 \x01(\x0b\x32\x0e.common.Header\x12\x13\n\x0bsync_status\x18\x02 \x01(\x05')
  ,
  dependencies=[header__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_TRAJECTORYAGENTSYNCSTATUS = _descriptor.Descriptor(
  name='TrajectoryAgentSyncStatus',
  full_name='trajectory_agent.TrajectoryAgentSyncStatus',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='trajectory_agent.TrajectoryAgentSyncStatus.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sync_status', full_name='trajectory_agent.TrajectoryAgentSyncStatus.sync_status', index=1,
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
  serialized_start=70,
  serialized_end=150,
)

_TRAJECTORYAGENTSYNCSTATUS.fields_by_name['header'].message_type = header__pb2._HEADER
DESCRIPTOR.message_types_by_name['TrajectoryAgentSyncStatus'] = _TRAJECTORYAGENTSYNCSTATUS

TrajectoryAgentSyncStatus = _reflection.GeneratedProtocolMessageType('TrajectoryAgentSyncStatus', (_message.Message,), dict(
  DESCRIPTOR = _TRAJECTORYAGENTSYNCSTATUS,
  __module__ = 'trajectory_agent_sync_status_pb2'
  # @@protoc_insertion_point(class_scope:trajectory_agent.TrajectoryAgentSyncStatus)
  ))
_sym_db.RegisterMessage(TrajectoryAgentSyncStatus)


# @@protoc_insertion_point(module_scope)

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: probabilistic_fusion_config.proto

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
  name='probabilistic_fusion_config.proto',
  package='perception.fusion',
  syntax='proto2',
  serialized_pb=_b('\n!probabilistic_fusion_config.proto\x12\x11perception.fusion\"\xa3\x03\n\x19ProbabilisticFusionConfig\x12\x17\n\tuse_lidar\x18\x01 \x01(\x08:\x04true\x12\x17\n\tuse_radar\x18\x02 \x01(\x08:\x04true\x12\x18\n\nuse_camera\x18\x03 \x01(\x08:\x04true\x12\"\n\x0etracker_method\x18\x04 \x01(\t:\nPbfTracker\x12.\n\x17\x64\x61ta_association_method\x18\x05 \x01(\t:\rHMAssociation\x12)\n\x12gate_keeper_method\x18\x06 \x01(\t:\rPbfGatekeeper\x12\x1b\n\x13prohibition_sensors\x18\x07 \x03(\t\x12(\n\x1amax_lidar_invisible_period\x18\x08 \x01(\x01:\x04\x30.25\x12\'\n\x1amax_radar_invisible_period\x18\t \x01(\x01:\x03\x30.5\x12)\n\x1bmax_camera_invisible_period\x18\n \x01(\x01:\x04\x30.75\x12 \n\x14max_cached_frame_num\x18\x0b \x01(\x03:\x02\x35\x30')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PROBABILISTICFUSIONCONFIG = _descriptor.Descriptor(
  name='ProbabilisticFusionConfig',
  full_name='perception.fusion.ProbabilisticFusionConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='use_lidar', full_name='perception.fusion.ProbabilisticFusionConfig.use_lidar', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_radar', full_name='perception.fusion.ProbabilisticFusionConfig.use_radar', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_camera', full_name='perception.fusion.ProbabilisticFusionConfig.use_camera', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tracker_method', full_name='perception.fusion.ProbabilisticFusionConfig.tracker_method', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=_b("PbfTracker").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_association_method', full_name='perception.fusion.ProbabilisticFusionConfig.data_association_method', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=_b("HMAssociation").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gate_keeper_method', full_name='perception.fusion.ProbabilisticFusionConfig.gate_keeper_method', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=True, default_value=_b("PbfGatekeeper").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prohibition_sensors', full_name='perception.fusion.ProbabilisticFusionConfig.prohibition_sensors', index=6,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_lidar_invisible_period', full_name='perception.fusion.ProbabilisticFusionConfig.max_lidar_invisible_period', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=True, default_value=float(0.25),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_radar_invisible_period', full_name='perception.fusion.ProbabilisticFusionConfig.max_radar_invisible_period', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=True, default_value=float(0.5),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_camera_invisible_period', full_name='perception.fusion.ProbabilisticFusionConfig.max_camera_invisible_period', index=9,
      number=10, type=1, cpp_type=5, label=1,
      has_default_value=True, default_value=float(0.75),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_cached_frame_num', full_name='perception.fusion.ProbabilisticFusionConfig.max_cached_frame_num', index=10,
      number=11, type=3, cpp_type=2, label=1,
      has_default_value=True, default_value=50,
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
  serialized_start=57,
  serialized_end=476,
)

DESCRIPTOR.message_types_by_name['ProbabilisticFusionConfig'] = _PROBABILISTICFUSIONCONFIG

ProbabilisticFusionConfig = _reflection.GeneratedProtocolMessageType('ProbabilisticFusionConfig', (_message.Message,), dict(
  DESCRIPTOR = _PROBABILISTICFUSIONCONFIG,
  __module__ = 'probabilistic_fusion_config_pb2'
  # @@protoc_insertion_point(class_scope:perception.fusion.ProbabilisticFusionConfig)
  ))
_sym_db.RegisterMessage(ProbabilisticFusionConfig)


# @@protoc_insertion_point(module_scope)

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pbf_gatekeeper_config.proto

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
  name='pbf_gatekeeper_config.proto',
  package='perception.fusion',
  syntax='proto2',
  serialized_pb=_b('\n\x1bpbf_gatekeeper_config.proto\x12\x11perception.fusion\"\x91\x04\n\x13PbfGatekeeperConfig\x12\"\n\x14publish_if_has_lidar\x18\x01 \x01(\x08:\x04true\x12\"\n\x14publish_if_has_radar\x18\x02 \x01(\x08:\x04true\x12#\n\x15publish_if_has_camera\x18\x03 \x01(\x08:\x04true\x12\x1b\n\ruse_camera_3d\x18\x04 \x01(\x08:\x04true\x12$\n\x1cmin_radar_confident_distance\x18\x05 \x01(\x01\x12!\n\x19max_radar_confident_angle\x18\x06 \x01(\x01\x12#\n\x1bmin_camera_publish_distance\x18\x07 \x01(\x01\x12\"\n\x1ainvisible_period_threshold\x18\x08 \x01(\x01\x12\x16\n\x0etoic_threshold\x18\t \x01(\x01\x12#\n\x1buse_track_time_pub_strategy\x18\n \x01(\x08\x12\x1d\n\x15pub_track_time_thresh\x18\x0b \x01(\x05\x12\x1b\n\x13\x65xistence_threshold\x18\x0c \x01(\x01\x12!\n\x19radar_existence_threshold\x18\r \x01(\x01\x12 \n\x12publish_if_has_obu\x18\x0e \x01(\x08:\x04true\x12 \n\x18min_obu_publish_distance\x18\x0f \x01(\x01')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PBFGATEKEEPERCONFIG = _descriptor.Descriptor(
  name='PbfGatekeeperConfig',
  full_name='perception.fusion.PbfGatekeeperConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='publish_if_has_lidar', full_name='perception.fusion.PbfGatekeeperConfig.publish_if_has_lidar', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='publish_if_has_radar', full_name='perception.fusion.PbfGatekeeperConfig.publish_if_has_radar', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='publish_if_has_camera', full_name='perception.fusion.PbfGatekeeperConfig.publish_if_has_camera', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_camera_3d', full_name='perception.fusion.PbfGatekeeperConfig.use_camera_3d', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_radar_confident_distance', full_name='perception.fusion.PbfGatekeeperConfig.min_radar_confident_distance', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_radar_confident_angle', full_name='perception.fusion.PbfGatekeeperConfig.max_radar_confident_angle', index=5,
      number=6, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_camera_publish_distance', full_name='perception.fusion.PbfGatekeeperConfig.min_camera_publish_distance', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='invisible_period_threshold', full_name='perception.fusion.PbfGatekeeperConfig.invisible_period_threshold', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='toic_threshold', full_name='perception.fusion.PbfGatekeeperConfig.toic_threshold', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_track_time_pub_strategy', full_name='perception.fusion.PbfGatekeeperConfig.use_track_time_pub_strategy', index=9,
      number=10, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pub_track_time_thresh', full_name='perception.fusion.PbfGatekeeperConfig.pub_track_time_thresh', index=10,
      number=11, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='existence_threshold', full_name='perception.fusion.PbfGatekeeperConfig.existence_threshold', index=11,
      number=12, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='radar_existence_threshold', full_name='perception.fusion.PbfGatekeeperConfig.radar_existence_threshold', index=12,
      number=13, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='publish_if_has_obu', full_name='perception.fusion.PbfGatekeeperConfig.publish_if_has_obu', index=13,
      number=14, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=True,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_obu_publish_distance', full_name='perception.fusion.PbfGatekeeperConfig.min_obu_publish_distance', index=14,
      number=15, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=51,
  serialized_end=580,
)

DESCRIPTOR.message_types_by_name['PbfGatekeeperConfig'] = _PBFGATEKEEPERCONFIG

PbfGatekeeperConfig = _reflection.GeneratedProtocolMessageType('PbfGatekeeperConfig', (_message.Message,), dict(
  DESCRIPTOR = _PBFGATEKEEPERCONFIG,
  __module__ = 'pbf_gatekeeper_config_pb2'
  # @@protoc_insertion_point(class_scope:perception.fusion.PbfGatekeeperConfig)
  ))
_sym_db.RegisterMessage(PbfGatekeeperConfig)


# @@protoc_insertion_point(module_scope)

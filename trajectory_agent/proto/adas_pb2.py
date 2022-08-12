# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: adas.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='adas.proto',
  package='adas',
  syntax='proto2',
  serialized_pb=_b('\n\nadas.proto\x12\x04\x61\x64\x61s\"\xfa\x02\n\x04View\x12\n\n\x02xl\x18\x01 \x01(\x05\x12\n\n\x02yt\x18\x02 \x01(\x05\x12\n\n\x02xr\x18\x03 \x01(\x05\x12\n\n\x02yb\x18\x04 \x01(\x05\x12\x0c\n\x04type\x18\x05 \x01(\t\x12,\n\x11showImageLocation\x18\x06 \x01(\x0e\x32\x11.adas.CarLocation\x12\x12\n\ndistance_x\x18\x07 \x01(\x01\x12\x12\n\ndistance_y\x18\x08 \x01(\x01\x12\x0b\n\x03lon\x18\t \x01(\x01\x12\x0b\n\x03lat\x18\n \x01(\x01\x12\x0b\n\x03\x61lt\x18\x0b \x01(\x01\x12\x12\n\nsystemTime\x18\x0c \x01(\t\x12\x15\n\rsatelliteTime\x18\r \x01(\t\x12\x0c\n\x04uuid\x18\x0e \x01(\t\x12\r\n\x05\x63\x61rId\x18\x0f \x01(\t\x12\r\n\x05\x63olor\x18\x10 \x01(\t\x12\x0f\n\x07heading\x18\x11 \x01(\x01\x12\r\n\x05speed\x18\x12 \x01(\x01\x12\x0e\n\x06length\x18\x13 \x01(\x02\x12\r\n\x05width\x18\x14 \x01(\x02\x12\x0e\n\x06height\x18\x15 \x01(\x02\x12\x11\n\tdrawlevel\x18\x16 \x01(\x05\"6\n\x08ViwesMsg\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t\x12\x1a\n\x06models\x18\x02 \x03(\x0b\x32\n.adas.View*\\\n\x0b\x43\x61rLocation\x12\r\n\tSame_LINE\x10\x00\x12\r\n\tLeft_LINE\x10\x01\x12\x0e\n\nRight_LINE\x10\x02\x12\x0e\n\nleft2_LINE\x10\x03\x12\x0f\n\x0bRight2_LINE\x10\x04*\xda\x02\n\nActionType\x12\x14\n\x10\x61\x63tion_type_view\x10\x01\x12\x19\n\x15\x61\x63tion_type_obstacles\x10\x02\x12\x15\n\x11\x61\x63tion_type_lanes\x10\x03\x12\x15\n\x11\x61\x63tion_type_state\x10\x04\x12\x14\n\x10\x61\x63tion_type_warn\x10\x05\x12\x15\n\x11\x61\x63tion_type_light\x10\x06\x12\x16\n\x12\x61\x63tion_type_config\x10\x07\x12\x15\n\x11\x61\x63tion_type_gdgps\x10\x08\x12 \n\x1c\x61\x63tion_type_auto_pilot_state\x10\t\x12\x1f\n\x1b\x61\x63tion_type_auto_pilot_mode\x10\n\x12!\n\x1d\x61\x63tion_type_obu_traffic_light\x10\x0b\x12+\n\'action_type_ai_cloud_to_start_autopilot\x10\x0c')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_CARLOCATION = _descriptor.EnumDescriptor(
  name='CarLocation',
  full_name='adas.CarLocation',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='Same_LINE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Left_LINE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Right_LINE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='left2_LINE', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='Right2_LINE', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=457,
  serialized_end=549,
)
_sym_db.RegisterEnumDescriptor(_CARLOCATION)

CarLocation = enum_type_wrapper.EnumTypeWrapper(_CARLOCATION)
_ACTIONTYPE = _descriptor.EnumDescriptor(
  name='ActionType',
  full_name='adas.ActionType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='action_type_view', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_obstacles', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_lanes', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_state', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_warn', index=4, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_light', index=5, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_config', index=6, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_gdgps', index=7, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_auto_pilot_state', index=8, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_auto_pilot_mode', index=9, number=10,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_obu_traffic_light', index=10, number=11,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='action_type_ai_cloud_to_start_autopilot', index=11, number=12,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=552,
  serialized_end=898,
)
_sym_db.RegisterEnumDescriptor(_ACTIONTYPE)

ActionType = enum_type_wrapper.EnumTypeWrapper(_ACTIONTYPE)
Same_LINE = 0
Left_LINE = 1
Right_LINE = 2
left2_LINE = 3
Right2_LINE = 4
action_type_view = 1
action_type_obstacles = 2
action_type_lanes = 3
action_type_state = 4
action_type_warn = 5
action_type_light = 6
action_type_config = 7
action_type_gdgps = 8
action_type_auto_pilot_state = 9
action_type_auto_pilot_mode = 10
action_type_obu_traffic_light = 11
action_type_ai_cloud_to_start_autopilot = 12



_VIEW = _descriptor.Descriptor(
  name='View',
  full_name='adas.View',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='xl', full_name='adas.View.xl', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='yt', full_name='adas.View.yt', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='xr', full_name='adas.View.xr', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='yb', full_name='adas.View.yb', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='adas.View.type', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='showImageLocation', full_name='adas.View.showImageLocation', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='distance_x', full_name='adas.View.distance_x', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='distance_y', full_name='adas.View.distance_y', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lon', full_name='adas.View.lon', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lat', full_name='adas.View.lat', index=9,
      number=10, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='alt', full_name='adas.View.alt', index=10,
      number=11, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='systemTime', full_name='adas.View.systemTime', index=11,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='satelliteTime', full_name='adas.View.satelliteTime', index=12,
      number=13, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='uuid', full_name='adas.View.uuid', index=13,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='carId', full_name='adas.View.carId', index=14,
      number=15, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='color', full_name='adas.View.color', index=15,
      number=16, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='heading', full_name='adas.View.heading', index=16,
      number=17, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='speed', full_name='adas.View.speed', index=17,
      number=18, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='length', full_name='adas.View.length', index=18,
      number=19, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='width', full_name='adas.View.width', index=19,
      number=20, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='height', full_name='adas.View.height', index=20,
      number=21, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='drawlevel', full_name='adas.View.drawlevel', index=21,
      number=22, type=5, cpp_type=1, label=1,
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
  serialized_start=21,
  serialized_end=399,
)


_VIWESMSG = _descriptor.Descriptor(
  name='ViwesMsg',
  full_name='adas.ViwesMsg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='action', full_name='adas.ViwesMsg.action', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='models', full_name='adas.ViwesMsg.models', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=401,
  serialized_end=455,
)

_VIEW.fields_by_name['showImageLocation'].enum_type = _CARLOCATION
_VIWESMSG.fields_by_name['models'].message_type = _VIEW
DESCRIPTOR.message_types_by_name['View'] = _VIEW
DESCRIPTOR.message_types_by_name['ViwesMsg'] = _VIWESMSG
DESCRIPTOR.enum_types_by_name['CarLocation'] = _CARLOCATION
DESCRIPTOR.enum_types_by_name['ActionType'] = _ACTIONTYPE

View = _reflection.GeneratedProtocolMessageType('View', (_message.Message,), dict(
  DESCRIPTOR = _VIEW,
  __module__ = 'adas_pb2'
  # @@protoc_insertion_point(class_scope:adas.View)
  ))
_sym_db.RegisterMessage(View)

ViwesMsg = _reflection.GeneratedProtocolMessageType('ViwesMsg', (_message.Message,), dict(
  DESCRIPTOR = _VIWESMSG,
  __module__ = 'adas_pb2'
  # @@protoc_insertion_point(class_scope:adas.ViwesMsg)
  ))
_sym_db.RegisterMessage(ViwesMsg)


# @@protoc_insertion_point(module_scope)
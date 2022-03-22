# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: traffic_light.proto

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


import header_pb2 as header__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='traffic_light.proto',
  package='perception',
  syntax='proto2',
  serialized_pb=_b('\n\x13traffic_light.proto\x12\nperception\x1a\x0cheader.proto\"\x91\x01\n\x0cTrafficLight\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x31\n\x04type\x18\x02 \x01(\x0e\x32\x15.perception.LightType:\x0cTYPE_DEFAULT\x12\x30\n\x05state\x18\x03 \x01(\x0e\x32\x16.perception.LightState:\tSTATE_OFF\x12\x10\n\x08\x64uration\x18\x04 \x01(\x02\"\xd6\x01\n\rTrafficLights\x12\x1e\n\x06header\x18\x01 \x01(\x0b\x32\x0e.common.Header\x12*\n\x08straight\x18\x02 \x01(\x0b\x32\x18.perception.TrafficLight\x12&\n\x04left\x18\x03 \x01(\x0b\x32\x18.perception.TrafficLight\x12\'\n\x05right\x18\x04 \x01(\x0b\x32\x18.perception.TrafficLight\x12(\n\x06u_turn\x18\x05 \x01(\x0b\x32\x18.perception.TrafficLight*c\n\tLightType\x12\x10\n\x0cTYPE_DEFAULT\x10\x00\x12\x10\n\x0cTYPE_VEHICLE\x10\x01\x12\x0f\n\x0bTYPE_BICYLE\x10\x02\x12\x12\n\x0eTYPE_PEDSTRIAN\x10\x03\x12\r\n\tTYPE_LANE\x10\x05*^\n\nLightState\x12\r\n\tSTATE_OFF\x10\x00\x12\r\n\tSTATE_RED\x10\x01\x12\x10\n\x0cSTATE_YELLOW\x10\x02\x12\x0f\n\x0bSTATE_GREEN\x10\x03\x12\x0f\n\x0bSTATE_FLASH\x10\x04')
  ,
  dependencies=[header__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_LIGHTTYPE = _descriptor.EnumDescriptor(
  name='LightType',
  full_name='perception.LightType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TYPE_DEFAULT', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TYPE_VEHICLE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TYPE_BICYLE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TYPE_PEDSTRIAN', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TYPE_LANE', index=4, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=414,
  serialized_end=513,
)
_sym_db.RegisterEnumDescriptor(_LIGHTTYPE)

LightType = enum_type_wrapper.EnumTypeWrapper(_LIGHTTYPE)
_LIGHTSTATE = _descriptor.EnumDescriptor(
  name='LightState',
  full_name='perception.LightState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATE_OFF', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STATE_RED', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STATE_YELLOW', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STATE_GREEN', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STATE_FLASH', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=515,
  serialized_end=609,
)
_sym_db.RegisterEnumDescriptor(_LIGHTSTATE)

LightState = enum_type_wrapper.EnumTypeWrapper(_LIGHTSTATE)
TYPE_DEFAULT = 0
TYPE_VEHICLE = 1
TYPE_BICYLE = 2
TYPE_PEDSTRIAN = 3
TYPE_LANE = 5
STATE_OFF = 0
STATE_RED = 1
STATE_YELLOW = 2
STATE_GREEN = 3
STATE_FLASH = 4



_TRAFFICLIGHT = _descriptor.Descriptor(
  name='TrafficLight',
  full_name='perception.TrafficLight',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='perception.TrafficLight.id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='perception.TrafficLight.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state', full_name='perception.TrafficLight.state', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='duration', full_name='perception.TrafficLight.duration', index=3,
      number=4, type=2, cpp_type=6, label=1,
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
  serialized_start=50,
  serialized_end=195,
)


_TRAFFICLIGHTS = _descriptor.Descriptor(
  name='TrafficLights',
  full_name='perception.TrafficLights',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='perception.TrafficLights.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='straight', full_name='perception.TrafficLights.straight', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='left', full_name='perception.TrafficLights.left', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='right', full_name='perception.TrafficLights.right', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='u_turn', full_name='perception.TrafficLights.u_turn', index=4,
      number=5, type=11, cpp_type=10, label=1,
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
  serialized_start=198,
  serialized_end=412,
)

_TRAFFICLIGHT.fields_by_name['type'].enum_type = _LIGHTTYPE
_TRAFFICLIGHT.fields_by_name['state'].enum_type = _LIGHTSTATE
_TRAFFICLIGHTS.fields_by_name['header'].message_type = header__pb2._HEADER
_TRAFFICLIGHTS.fields_by_name['straight'].message_type = _TRAFFICLIGHT
_TRAFFICLIGHTS.fields_by_name['left'].message_type = _TRAFFICLIGHT
_TRAFFICLIGHTS.fields_by_name['right'].message_type = _TRAFFICLIGHT
_TRAFFICLIGHTS.fields_by_name['u_turn'].message_type = _TRAFFICLIGHT
DESCRIPTOR.message_types_by_name['TrafficLight'] = _TRAFFICLIGHT
DESCRIPTOR.message_types_by_name['TrafficLights'] = _TRAFFICLIGHTS
DESCRIPTOR.enum_types_by_name['LightType'] = _LIGHTTYPE
DESCRIPTOR.enum_types_by_name['LightState'] = _LIGHTSTATE

TrafficLight = _reflection.GeneratedProtocolMessageType('TrafficLight', (_message.Message,), dict(
  DESCRIPTOR = _TRAFFICLIGHT,
  __module__ = 'traffic_light_pb2'
  # @@protoc_insertion_point(class_scope:perception.TrafficLight)
  ))
_sym_db.RegisterMessage(TrafficLight)

TrafficLights = _reflection.GeneratedProtocolMessageType('TrafficLights', (_message.Message,), dict(
  DESCRIPTOR = _TRAFFICLIGHTS,
  __module__ = 'traffic_light_pb2'
  # @@protoc_insertion_point(class_scope:perception.TrafficLights)
  ))
_sym_db.RegisterMessage(TrafficLights)


# @@protoc_insertion_point(module_scope)

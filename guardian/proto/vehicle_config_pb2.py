# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle_config.proto

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
  name='vehicle_config.proto',
  package='chassis',
  syntax='proto2',
  serialized_pb=_b('\n\x14vehicle_config.proto\x12\x07\x63hassis\"\xf7\x03\n\rVehicleConfig\x12\x0b\n\x03vin\x18\x01 \x01(\t\x12\r\n\x05plate\x18\x02 \x01(\t\x12\r\n\x05\x62rand\x18\x03 \x01(\t\x12\x0e\n\x06length\x18\x06 \x01(\x02\x12\r\n\x05width\x18\x07 \x01(\x02\x12\x0e\n\x06height\x18\x08 \x01(\x02\x12\x0e\n\x06weight\x18\t \x01(\x02\x12\x11\n\taccel_min\x18\n \x01(\x02\x12\x11\n\taccel_max\x18\x0b \x01(\x02\x12\x14\n\x0csteering_min\x18\x0c \x01(\x02\x12\x14\n\x0csteering_max\x18\r \x01(\x02\x12\x12\n\nwheel_base\x18\x0e \x01(\x02\x12\x18\n\x10\x66ront_wheel_base\x18\x0f \x01(\x02\x12\x17\n\x0frear_wheel_base\x18\x10 \x01(\x02\x12\x13\n\x0bsteer_ratio\x18\x11 \x01(\x02\x12\"\n\x1amax_abs_speed_when_stopped\x18\x12 \x01(\x02\x12\x19\n\x11throttle_deadzone\x18\x13 \x01(\x01\x12\x16\n\x0e\x62rake_deadzone\x18\x14 \x01(\x01\x12\x17\n\x0f\x63\x65nter_to_front\x18\x16 \x01(\x02\x12\x16\n\x0e\x63\x65nter_to_back\x18\x17 \x01(\x02\x12\x16\n\x0e\x63\x65nter_to_left\x18\x18 \x01(\x02\x12\x17\n\x0f\x63\x65nter_to_right\x18\x19 \x01(\x02\x12\x15\n\rvehicle_color\x18\x1a \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_VEHICLECONFIG = _descriptor.Descriptor(
  name='VehicleConfig',
  full_name='chassis.VehicleConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='vin', full_name='chassis.VehicleConfig.vin', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='plate', full_name='chassis.VehicleConfig.plate', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='brand', full_name='chassis.VehicleConfig.brand', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='length', full_name='chassis.VehicleConfig.length', index=3,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='width', full_name='chassis.VehicleConfig.width', index=4,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='height', full_name='chassis.VehicleConfig.height', index=5,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weight', full_name='chassis.VehicleConfig.weight', index=6,
      number=9, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accel_min', full_name='chassis.VehicleConfig.accel_min', index=7,
      number=10, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accel_max', full_name='chassis.VehicleConfig.accel_max', index=8,
      number=11, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='steering_min', full_name='chassis.VehicleConfig.steering_min', index=9,
      number=12, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='steering_max', full_name='chassis.VehicleConfig.steering_max', index=10,
      number=13, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wheel_base', full_name='chassis.VehicleConfig.wheel_base', index=11,
      number=14, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='front_wheel_base', full_name='chassis.VehicleConfig.front_wheel_base', index=12,
      number=15, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rear_wheel_base', full_name='chassis.VehicleConfig.rear_wheel_base', index=13,
      number=16, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='steer_ratio', full_name='chassis.VehicleConfig.steer_ratio', index=14,
      number=17, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_abs_speed_when_stopped', full_name='chassis.VehicleConfig.max_abs_speed_when_stopped', index=15,
      number=18, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='throttle_deadzone', full_name='chassis.VehicleConfig.throttle_deadzone', index=16,
      number=19, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='brake_deadzone', full_name='chassis.VehicleConfig.brake_deadzone', index=17,
      number=20, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='center_to_front', full_name='chassis.VehicleConfig.center_to_front', index=18,
      number=22, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='center_to_back', full_name='chassis.VehicleConfig.center_to_back', index=19,
      number=23, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='center_to_left', full_name='chassis.VehicleConfig.center_to_left', index=20,
      number=24, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='center_to_right', full_name='chassis.VehicleConfig.center_to_right', index=21,
      number=25, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vehicle_color', full_name='chassis.VehicleConfig.vehicle_color', index=22,
      number=26, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=34,
  serialized_end=537,
)

DESCRIPTOR.message_types_by_name['VehicleConfig'] = _VEHICLECONFIG

VehicleConfig = _reflection.GeneratedProtocolMessageType('VehicleConfig', (_message.Message,), dict(
  DESCRIPTOR = _VEHICLECONFIG,
  __module__ = 'vehicle_config_pb2'
  # @@protoc_insertion_point(class_scope:chassis.VehicleConfig)
  ))
_sym_db.RegisterMessage(VehicleConfig)


# @@protoc_insertion_point(module_scope)

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: VehicleEventFlags_PB.proto

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


DESCRIPTOR = _descriptor.FileDescriptor(
  name='VehicleEventFlags_PB.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x1aVehicleEventFlags_PB.proto\x1a\x0fString_PB.proto\"\xfa\x04\n\x14VehicleEventFlags_PB\x12\x17\n\x03lat\x18\x01 \x02(\x0b\x32\n.String_PB\"\xc8\x04\n\x11VehicleEventFlags\x12\'\n#VehicleEventFlags_eventHazardLights\x10\x00\x12,\n(VehicleEventFlags_eventStopLineViolation\x10\x01\x12\'\n#VehicleEventFlags_eventABSactivated\x10\x02\x12.\n*VehicleEventFlags_eventTractionControlLoss\x10\x03\x12\x34\n0VehicleEventFlags_eventStabilityControlactivated\x10\x04\x12-\n)VehicleEventFlags_eventHazardousMaterials\x10\x05\x12$\n VehicleEventFlags_eventReserved1\x10\x06\x12&\n\"VehicleEventFlags_eventHardBraking\x10\x07\x12(\n$VehicleEventFlags_eventLightsChanged\x10\x08\x12(\n$VehicleEventFlags_eventWipersChanged\x10\t\x12#\n\x1fVehicleEventFlags_eventFlatTire\x10\n\x12*\n&VehicleEventFlags_eventDisabledVehicle\x10\x0b\x12+\n\'VehicleEventFlags_eventAirBagDeployment\x10\x0c')
  ,
  dependencies=[String__PB__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_VEHICLEEVENTFLAGS_PB_VEHICLEEVENTFLAGS = _descriptor.EnumDescriptor(
  name='VehicleEventFlags',
  full_name='VehicleEventFlags_PB.VehicleEventFlags',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventHazardLights', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventStopLineViolation', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventABSactivated', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventTractionControlLoss', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventStabilityControlactivated', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventHazardousMaterials', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventReserved1', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventHardBraking', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventLightsChanged', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventWipersChanged', index=9, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventFlatTire', index=10, number=10,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventDisabledVehicle', index=11, number=11,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VehicleEventFlags_eventAirBagDeployment', index=12, number=12,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=98,
  serialized_end=682,
)
_sym_db.RegisterEnumDescriptor(_VEHICLEEVENTFLAGS_PB_VEHICLEEVENTFLAGS)


_VEHICLEEVENTFLAGS_PB = _descriptor.Descriptor(
  name='VehicleEventFlags_PB',
  full_name='VehicleEventFlags_PB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='lat', full_name='VehicleEventFlags_PB.lat', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _VEHICLEEVENTFLAGS_PB_VEHICLEEVENTFLAGS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=682,
)

_VEHICLEEVENTFLAGS_PB.fields_by_name['lat'].message_type = String__PB__pb2._STRING_PB
_VEHICLEEVENTFLAGS_PB_VEHICLEEVENTFLAGS.containing_type = _VEHICLEEVENTFLAGS_PB
DESCRIPTOR.message_types_by_name['VehicleEventFlags_PB'] = _VEHICLEEVENTFLAGS_PB

VehicleEventFlags_PB = _reflection.GeneratedProtocolMessageType('VehicleEventFlags_PB', (_message.Message,), dict(
  DESCRIPTOR = _VEHICLEEVENTFLAGS_PB,
  __module__ = 'VehicleEventFlags_PB_pb2'
  # @@protoc_insertion_point(class_scope:VehicleEventFlags_PB)
  ))
_sym_db.RegisterMessage(VehicleEventFlags_PB)


# @@protoc_insertion_point(module_scope)
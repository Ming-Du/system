# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: PositionConfidenceSet_PB.proto

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
  name='PositionConfidenceSet_PB.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x1ePositionConfidenceSet_PB.proto\"\x82\n\n\x18PositionConfidenceSet_PB\x12?\n\x06poscon\x18\x01 \x02(\x0e\x32/.PositionConfidenceSet_PB.PositionConfidence_PB\x12\x46\n\x0c\x65levationCon\x18\x02 \x01(\x0e\x32\x30.PositionConfidenceSet_PB.ElevationConfidence_PB\"\xf1\x03\n\x15PositionConfidence_PB\x12\"\n\x1ePositionConfidence_unavailable\x10\x00\x12\x1c\n\x18PositionConfidence_a500m\x10\x01\x12\x1c\n\x18PositionConfidence_a200m\x10\x02\x12\x1c\n\x18PositionConfidence_a100m\x10\x03\x12\x1b\n\x17PositionConfidence_a50m\x10\x04\x12\x1b\n\x17PositionConfidence_a20m\x10\x05\x12\x1b\n\x17PositionConfidence_a10m\x10\x06\x12\x1a\n\x16PositionConfidence_a5m\x10\x07\x12\x1a\n\x16PositionConfidence_a2m\x10\x08\x12\x1a\n\x16PositionConfidence_a1m\x10\t\x12\x1c\n\x18PositionConfidence_a50cm\x10\n\x12\x1c\n\x18PositionConfidence_a20cm\x10\x0b\x12\x1c\n\x18PositionConfidence_a10cm\x10\x0c\x12\x1b\n\x17PositionConfidence_a5cm\x10\r\x12\x1b\n\x17PositionConfidence_a2cm\x10\x0e\x12\x1b\n\x17PositionConfidence_a1cm\x10\x0f\"\xe8\x04\n\x16\x45levationConfidence_PB\x12#\n\x1f\x45levationConfidence_unavailable\x10\x00\x12#\n\x1f\x45levationConfidence_elev_500_00\x10\x01\x12#\n\x1f\x45levationConfidence_elev_200_00\x10\x02\x12#\n\x1f\x45levationConfidence_elev_100_00\x10\x03\x12#\n\x1f\x45levationConfidence_elev_050_00\x10\x04\x12#\n\x1f\x45levationConfidence_elev_020_00\x10\x05\x12#\n\x1f\x45levationConfidence_elev_010_00\x10\x06\x12#\n\x1f\x45levationConfidence_elev_005_00\x10\x07\x12#\n\x1f\x45levationConfidence_elev_002_00\x10\x08\x12#\n\x1f\x45levationConfidence_elev_001_00\x10\t\x12#\n\x1f\x45levationConfidence_elev_000_50\x10\n\x12#\n\x1f\x45levationConfidence_elev_000_20\x10\x0b\x12#\n\x1f\x45levationConfidence_elev_000_10\x10\x0c\x12#\n\x1f\x45levationConfidence_elev_000_05\x10\r\x12#\n\x1f\x45levationConfidence_elev_000_02\x10\x0e\x12#\n\x1f\x45levationConfidence_elev_000_01\x10\x0f')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_POSITIONCONFIDENCESET_PB_POSITIONCONFIDENCE_PB = _descriptor.EnumDescriptor(
  name='PositionConfidence_PB',
  full_name='PositionConfidenceSet_PB.PositionConfidence_PB',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_unavailable', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a500m', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a200m', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a100m', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a50m', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a20m', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a10m', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a5m', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a2m', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a1m', index=9, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a50cm', index=10, number=10,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a20cm', index=11, number=11,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a10cm', index=12, number=12,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a5cm', index=13, number=13,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a2cm', index=14, number=14,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PositionConfidence_a1cm', index=15, number=15,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=201,
  serialized_end=698,
)
_sym_db.RegisterEnumDescriptor(_POSITIONCONFIDENCESET_PB_POSITIONCONFIDENCE_PB)

_POSITIONCONFIDENCESET_PB_ELEVATIONCONFIDENCE_PB = _descriptor.EnumDescriptor(
  name='ElevationConfidence_PB',
  full_name='PositionConfidenceSet_PB.ElevationConfidence_PB',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_unavailable', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_500_00', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_200_00', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_100_00', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_050_00', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_020_00', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_010_00', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_005_00', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_002_00', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_001_00', index=9, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_50', index=10, number=10,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_20', index=11, number=11,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_10', index=12, number=12,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_05', index=13, number=13,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_02', index=14, number=14,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ElevationConfidence_elev_000_01', index=15, number=15,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=701,
  serialized_end=1317,
)
_sym_db.RegisterEnumDescriptor(_POSITIONCONFIDENCESET_PB_ELEVATIONCONFIDENCE_PB)


_POSITIONCONFIDENCESET_PB = _descriptor.Descriptor(
  name='PositionConfidenceSet_PB',
  full_name='PositionConfidenceSet_PB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='poscon', full_name='PositionConfidenceSet_PB.poscon', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='elevationCon', full_name='PositionConfidenceSet_PB.elevationCon', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _POSITIONCONFIDENCESET_PB_POSITIONCONFIDENCE_PB,
    _POSITIONCONFIDENCESET_PB_ELEVATIONCONFIDENCE_PB,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=1317,
)

_POSITIONCONFIDENCESET_PB.fields_by_name['poscon'].enum_type = _POSITIONCONFIDENCESET_PB_POSITIONCONFIDENCE_PB
_POSITIONCONFIDENCESET_PB.fields_by_name['elevationCon'].enum_type = _POSITIONCONFIDENCESET_PB_ELEVATIONCONFIDENCE_PB
_POSITIONCONFIDENCESET_PB_POSITIONCONFIDENCE_PB.containing_type = _POSITIONCONFIDENCESET_PB
_POSITIONCONFIDENCESET_PB_ELEVATIONCONFIDENCE_PB.containing_type = _POSITIONCONFIDENCESET_PB
DESCRIPTOR.message_types_by_name['PositionConfidenceSet_PB'] = _POSITIONCONFIDENCESET_PB

PositionConfidenceSet_PB = _reflection.GeneratedProtocolMessageType('PositionConfidenceSet_PB', (_message.Message,), dict(
  DESCRIPTOR = _POSITIONCONFIDENCESET_PB,
  __module__ = 'PositionConfidenceSet_PB_pb2'
  # @@protoc_insertion_point(class_scope:PositionConfidenceSet_PB)
  ))
_sym_db.RegisterMessage(PositionConfidenceSet_PB)


# @@protoc_insertion_point(module_scope)

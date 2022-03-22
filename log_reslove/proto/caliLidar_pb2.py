# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: caliLidar.proto

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
  name='caliLidar.proto',
  package='calili.base',
  syntax='proto2',
  serialized_pb=_b('\n\x0f\x63\x61liLidar.proto\x12\x0b\x63\x61lili.base\"Y\n\x03Roi\x12\x0c\n\x04xmin\x18\x01 \x01(\x01\x12\x0c\n\x04xmax\x18\x02 \x01(\x01\x12\x0c\n\x04ymin\x18\x03 \x01(\x01\x12\x0c\n\x04ymax\x18\x04 \x01(\x01\x12\x0c\n\x04zmin\x18\x05 \x01(\x01\x12\x0c\n\x04zmax\x18\x06 \x01(\x01\"M\n\x07LidarCS\x12 \n\x06\x66rontw\x18\x01 \x01(\x0b\x32\x10.calili.base.Roi\x12 \n\x06ground\x18\x02 \x01(\x0b\x32\x10.calili.base.Roi\"o\n\x07VehleCS\x12 \n\x06\x66rontw\x18\x01 \x01(\x0b\x32\x10.calili.base.Roi\x12 \n\x06ground\x18\x02 \x01(\x0b\x32\x10.calili.base.Roi\x12 \n\x06leftwa\x18\x03 \x01(\x0b\x32\x10.calili.base.Roi\"\x85\x01\n\x0c\x43\x61liLidarSet\x12\x11\n\ttopicname\x18\x01 \x01(\t\x12\x14\n\x0csensorpbpath\x18\x02 \x01(\t\x12%\n\x07lidarcs\x18\x03 \x01(\x0b\x32\x14.calili.base.LidarCS\x12%\n\x07vehlecs\x18\x04 \x01(\x0b\x32\x14.calili.base.VehleCS\"T\n\x13RegisterCalibration\x12/\n\x0c\x63\x61lilidarset\x18\x01 \x01(\x0b\x32\x19.calili.base.CaliLidarSet\x12\x0c\n\x04\x62\x61se\x18\x02 \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_ROI = _descriptor.Descriptor(
  name='Roi',
  full_name='calili.base.Roi',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='xmin', full_name='calili.base.Roi.xmin', index=0,
      number=1, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='xmax', full_name='calili.base.Roi.xmax', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ymin', full_name='calili.base.Roi.ymin', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ymax', full_name='calili.base.Roi.ymax', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='zmin', full_name='calili.base.Roi.zmin', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='zmax', full_name='calili.base.Roi.zmax', index=5,
      number=6, type=1, cpp_type=5, label=1,
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
  serialized_start=32,
  serialized_end=121,
)


_LIDARCS = _descriptor.Descriptor(
  name='LidarCS',
  full_name='calili.base.LidarCS',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frontw', full_name='calili.base.LidarCS.frontw', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ground', full_name='calili.base.LidarCS.ground', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_start=123,
  serialized_end=200,
)


_VEHLECS = _descriptor.Descriptor(
  name='VehleCS',
  full_name='calili.base.VehleCS',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frontw', full_name='calili.base.VehleCS.frontw', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ground', full_name='calili.base.VehleCS.ground', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='leftwa', full_name='calili.base.VehleCS.leftwa', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  serialized_start=202,
  serialized_end=313,
)


_CALILIDARSET = _descriptor.Descriptor(
  name='CaliLidarSet',
  full_name='calili.base.CaliLidarSet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='topicname', full_name='calili.base.CaliLidarSet.topicname', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sensorpbpath', full_name='calili.base.CaliLidarSet.sensorpbpath', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lidarcs', full_name='calili.base.CaliLidarSet.lidarcs', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='vehlecs', full_name='calili.base.CaliLidarSet.vehlecs', index=3,
      number=4, type=11, cpp_type=10, label=1,
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
  serialized_start=316,
  serialized_end=449,
)


_REGISTERCALIBRATION = _descriptor.Descriptor(
  name='RegisterCalibration',
  full_name='calili.base.RegisterCalibration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='calilidarset', full_name='calili.base.RegisterCalibration.calilidarset', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='base', full_name='calili.base.RegisterCalibration.base', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=451,
  serialized_end=535,
)

_LIDARCS.fields_by_name['frontw'].message_type = _ROI
_LIDARCS.fields_by_name['ground'].message_type = _ROI
_VEHLECS.fields_by_name['frontw'].message_type = _ROI
_VEHLECS.fields_by_name['ground'].message_type = _ROI
_VEHLECS.fields_by_name['leftwa'].message_type = _ROI
_CALILIDARSET.fields_by_name['lidarcs'].message_type = _LIDARCS
_CALILIDARSET.fields_by_name['vehlecs'].message_type = _VEHLECS
_REGISTERCALIBRATION.fields_by_name['calilidarset'].message_type = _CALILIDARSET
DESCRIPTOR.message_types_by_name['Roi'] = _ROI
DESCRIPTOR.message_types_by_name['LidarCS'] = _LIDARCS
DESCRIPTOR.message_types_by_name['VehleCS'] = _VEHLECS
DESCRIPTOR.message_types_by_name['CaliLidarSet'] = _CALILIDARSET
DESCRIPTOR.message_types_by_name['RegisterCalibration'] = _REGISTERCALIBRATION

Roi = _reflection.GeneratedProtocolMessageType('Roi', (_message.Message,), dict(
  DESCRIPTOR = _ROI,
  __module__ = 'caliLidar_pb2'
  # @@protoc_insertion_point(class_scope:calili.base.Roi)
  ))
_sym_db.RegisterMessage(Roi)

LidarCS = _reflection.GeneratedProtocolMessageType('LidarCS', (_message.Message,), dict(
  DESCRIPTOR = _LIDARCS,
  __module__ = 'caliLidar_pb2'
  # @@protoc_insertion_point(class_scope:calili.base.LidarCS)
  ))
_sym_db.RegisterMessage(LidarCS)

VehleCS = _reflection.GeneratedProtocolMessageType('VehleCS', (_message.Message,), dict(
  DESCRIPTOR = _VEHLECS,
  __module__ = 'caliLidar_pb2'
  # @@protoc_insertion_point(class_scope:calili.base.VehleCS)
  ))
_sym_db.RegisterMessage(VehleCS)

CaliLidarSet = _reflection.GeneratedProtocolMessageType('CaliLidarSet', (_message.Message,), dict(
  DESCRIPTOR = _CALILIDARSET,
  __module__ = 'caliLidar_pb2'
  # @@protoc_insertion_point(class_scope:calili.base.CaliLidarSet)
  ))
_sym_db.RegisterMessage(CaliLidarSet)

RegisterCalibration = _reflection.GeneratedProtocolMessageType('RegisterCalibration', (_message.Message,), dict(
  DESCRIPTOR = _REGISTERCALIBRATION,
  __module__ = 'caliLidar_pb2'
  # @@protoc_insertion_point(class_scope:calili.base.RegisterCalibration)
  ))
_sym_db.RegisterMessage(RegisterCalibration)


# @@protoc_insertion_point(module_scope)

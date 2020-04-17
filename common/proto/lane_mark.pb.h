// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: lane_mark.proto

#ifndef PROTOBUF_lane_5fmark_2eproto__INCLUDED
#define PROTOBUF_lane_5fmark_2eproto__INCLUDED

#include <string>

#include <google/protobuf/stubs/common.h>

#if GOOGLE_PROTOBUF_VERSION < 2006000
#error This file was generated by a newer version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please update
#error your headers.
#endif
#if 2006001 < GOOGLE_PROTOBUF_MIN_PROTOC_VERSION
#error This file was generated by an older version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please
#error regenerate this file with a newer version of protoc.
#endif

#include <google/protobuf/generated_message_util.h>
#include <google/protobuf/message.h>
#include <google/protobuf/repeated_field.h>
#include <google/protobuf/extension_set.h>
#include <google/protobuf/generated_enum_reflection.h>
#include <google/protobuf/unknown_field_set.h>
#include "header.pb.h"
// @@protoc_insertion_point(includes)

namespace perception {

// Internal implementation detail -- do not call these.
void  protobuf_AddDesc_lane_5fmark_2eproto();
void protobuf_AssignDesc_lane_5fmark_2eproto();
void protobuf_ShutdownFile_lane_5fmark_2eproto();

class Point2D;
class LaneMark;
class LaneCenter;
class LaneMarks;

enum LaneMarkColor {
  COLOR_WHITE = 0,
  COLOR_YELLOW = 1
};
bool LaneMarkColor_IsValid(int value);
const LaneMarkColor LaneMarkColor_MIN = COLOR_WHITE;
const LaneMarkColor LaneMarkColor_MAX = COLOR_YELLOW;
const int LaneMarkColor_ARRAYSIZE = LaneMarkColor_MAX + 1;

const ::google::protobuf::EnumDescriptor* LaneMarkColor_descriptor();
inline const ::std::string& LaneMarkColor_Name(LaneMarkColor value) {
  return ::google::protobuf::internal::NameOfEnum(
    LaneMarkColor_descriptor(), value);
}
inline bool LaneMarkColor_Parse(
    const ::std::string& name, LaneMarkColor* value) {
  return ::google::protobuf::internal::ParseNamedEnum<LaneMarkColor>(
    LaneMarkColor_descriptor(), name, value);
}
enum LaneMarkType {
  LANE_MARK_NONE = 0,
  LANE_MARK_SOLID = 1,
  LANE_MARK_BROKEN = 2
};
bool LaneMarkType_IsValid(int value);
const LaneMarkType LaneMarkType_MIN = LANE_MARK_NONE;
const LaneMarkType LaneMarkType_MAX = LANE_MARK_BROKEN;
const int LaneMarkType_ARRAYSIZE = LaneMarkType_MAX + 1;

const ::google::protobuf::EnumDescriptor* LaneMarkType_descriptor();
inline const ::std::string& LaneMarkType_Name(LaneMarkType value) {
  return ::google::protobuf::internal::NameOfEnum(
    LaneMarkType_descriptor(), value);
}
inline bool LaneMarkType_Parse(
    const ::std::string& name, LaneMarkType* value) {
  return ::google::protobuf::internal::ParseNamedEnum<LaneMarkType>(
    LaneMarkType_descriptor(), name, value);
}
// ===================================================================

class Point2D : public ::google::protobuf::Message {
 public:
  Point2D();
  virtual ~Point2D();

  Point2D(const Point2D& from);

  inline Point2D& operator=(const Point2D& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const Point2D& default_instance();

  void Swap(Point2D* other);

  // implements Message ----------------------------------------------

  Point2D* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const Point2D& from);
  void MergeFrom(const Point2D& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // optional double x = 1 [default = nan];
  inline bool has_x() const;
  inline void clear_x();
  static const int kXFieldNumber = 1;
  inline double x() const;
  inline void set_x(double value);

  // optional double y = 2 [default = nan];
  inline bool has_y() const;
  inline void clear_y();
  static const int kYFieldNumber = 2;
  inline double y() const;
  inline void set_y(double value);

  // @@protoc_insertion_point(class_scope:perception.Point2D)
 private:
  inline void set_has_x();
  inline void clear_has_x();
  inline void set_has_y();
  inline void clear_has_y();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  double x_;
  double y_;
  friend void  protobuf_AddDesc_lane_5fmark_2eproto();
  friend void protobuf_AssignDesc_lane_5fmark_2eproto();
  friend void protobuf_ShutdownFile_lane_5fmark_2eproto();

  void InitAsDefaultInstance();
  static Point2D* default_instance_;
};
// -------------------------------------------------------------------

class LaneMark : public ::google::protobuf::Message {
 public:
  LaneMark();
  virtual ~LaneMark();

  LaneMark(const LaneMark& from);

  inline LaneMark& operator=(const LaneMark& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const LaneMark& default_instance();

  void Swap(LaneMark* other);

  // implements Message ----------------------------------------------

  LaneMark* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const LaneMark& from);
  void MergeFrom(const LaneMark& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // optional .perception.LaneMarkColor color = 1;
  inline bool has_color() const;
  inline void clear_color();
  static const int kColorFieldNumber = 1;
  inline ::perception::LaneMarkColor color() const;
  inline void set_color(::perception::LaneMarkColor value);

  // optional .perception.LaneMarkType type = 2;
  inline bool has_type() const;
  inline void clear_type();
  static const int kTypeFieldNumber = 2;
  inline ::perception::LaneMarkType type() const;
  inline void set_type(::perception::LaneMarkType value);

  // optional float confidence = 3;
  inline bool has_confidence() const;
  inline void clear_confidence();
  static const int kConfidenceFieldNumber = 3;
  inline float confidence() const;
  inline void set_confidence(float value);

  // repeated .perception.Point2D points = 4;
  inline int points_size() const;
  inline void clear_points();
  static const int kPointsFieldNumber = 4;
  inline const ::perception::Point2D& points(int index) const;
  inline ::perception::Point2D* mutable_points(int index);
  inline ::perception::Point2D* add_points();
  inline const ::google::protobuf::RepeatedPtrField< ::perception::Point2D >&
      points() const;
  inline ::google::protobuf::RepeatedPtrField< ::perception::Point2D >*
      mutable_points();

  // @@protoc_insertion_point(class_scope:perception.LaneMark)
 private:
  inline void set_has_color();
  inline void clear_has_color();
  inline void set_has_type();
  inline void clear_has_type();
  inline void set_has_confidence();
  inline void clear_has_confidence();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  int color_;
  int type_;
  ::google::protobuf::RepeatedPtrField< ::perception::Point2D > points_;
  float confidence_;
  friend void  protobuf_AddDesc_lane_5fmark_2eproto();
  friend void protobuf_AssignDesc_lane_5fmark_2eproto();
  friend void protobuf_ShutdownFile_lane_5fmark_2eproto();

  void InitAsDefaultInstance();
  static LaneMark* default_instance_;
};
// -------------------------------------------------------------------

class LaneCenter : public ::google::protobuf::Message {
 public:
  LaneCenter();
  virtual ~LaneCenter();

  LaneCenter(const LaneCenter& from);

  inline LaneCenter& operator=(const LaneCenter& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const LaneCenter& default_instance();

  void Swap(LaneCenter* other);

  // implements Message ----------------------------------------------

  LaneCenter* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const LaneCenter& from);
  void MergeFrom(const LaneCenter& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // repeated .perception.Point2D points = 1;
  inline int points_size() const;
  inline void clear_points();
  static const int kPointsFieldNumber = 1;
  inline const ::perception::Point2D& points(int index) const;
  inline ::perception::Point2D* mutable_points(int index);
  inline ::perception::Point2D* add_points();
  inline const ::google::protobuf::RepeatedPtrField< ::perception::Point2D >&
      points() const;
  inline ::google::protobuf::RepeatedPtrField< ::perception::Point2D >*
      mutable_points();

  // @@protoc_insertion_point(class_scope:perception.LaneCenter)
 private:

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  ::google::protobuf::RepeatedPtrField< ::perception::Point2D > points_;
  friend void  protobuf_AddDesc_lane_5fmark_2eproto();
  friend void protobuf_AssignDesc_lane_5fmark_2eproto();
  friend void protobuf_ShutdownFile_lane_5fmark_2eproto();

  void InitAsDefaultInstance();
  static LaneCenter* default_instance_;
};
// -------------------------------------------------------------------

class LaneMarks : public ::google::protobuf::Message {
 public:
  LaneMarks();
  virtual ~LaneMarks();

  LaneMarks(const LaneMarks& from);

  inline LaneMarks& operator=(const LaneMarks& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const LaneMarks& default_instance();

  void Swap(LaneMarks* other);

  // implements Message ----------------------------------------------

  LaneMarks* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const LaneMarks& from);
  void MergeFrom(const LaneMarks& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // optional .common.Header header = 1;
  inline bool has_header() const;
  inline void clear_header();
  static const int kHeaderFieldNumber = 1;
  inline const ::common::Header& header() const;
  inline ::common::Header* mutable_header();
  inline ::common::Header* release_header();
  inline void set_allocated_header(::common::Header* header);

  // optional .perception.LaneMark left = 2;
  inline bool has_left() const;
  inline void clear_left();
  static const int kLeftFieldNumber = 2;
  inline const ::perception::LaneMark& left() const;
  inline ::perception::LaneMark* mutable_left();
  inline ::perception::LaneMark* release_left();
  inline void set_allocated_left(::perception::LaneMark* left);

  // optional .perception.LaneMark right = 3;
  inline bool has_right() const;
  inline void clear_right();
  static const int kRightFieldNumber = 3;
  inline const ::perception::LaneMark& right() const;
  inline ::perception::LaneMark* mutable_right();
  inline ::perception::LaneMark* release_right();
  inline void set_allocated_right(::perception::LaneMark* right);

  // optional .perception.LaneMark left2 = 4;
  inline bool has_left2() const;
  inline void clear_left2();
  static const int kLeft2FieldNumber = 4;
  inline const ::perception::LaneMark& left2() const;
  inline ::perception::LaneMark* mutable_left2();
  inline ::perception::LaneMark* release_left2();
  inline void set_allocated_left2(::perception::LaneMark* left2);

  // optional .perception.LaneMark right2 = 5;
  inline bool has_right2() const;
  inline void clear_right2();
  static const int kRight2FieldNumber = 5;
  inline const ::perception::LaneMark& right2() const;
  inline ::perception::LaneMark* mutable_right2();
  inline ::perception::LaneMark* release_right2();
  inline void set_allocated_right2(::perception::LaneMark* right2);

  // @@protoc_insertion_point(class_scope:perception.LaneMarks)
 private:
  inline void set_has_header();
  inline void clear_has_header();
  inline void set_has_left();
  inline void clear_has_left();
  inline void set_has_right();
  inline void clear_has_right();
  inline void set_has_left2();
  inline void clear_has_left2();
  inline void set_has_right2();
  inline void clear_has_right2();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  ::common::Header* header_;
  ::perception::LaneMark* left_;
  ::perception::LaneMark* right_;
  ::perception::LaneMark* left2_;
  ::perception::LaneMark* right2_;
  friend void  protobuf_AddDesc_lane_5fmark_2eproto();
  friend void protobuf_AssignDesc_lane_5fmark_2eproto();
  friend void protobuf_ShutdownFile_lane_5fmark_2eproto();

  void InitAsDefaultInstance();
  static LaneMarks* default_instance_;
};
// ===================================================================


// ===================================================================

// Point2D

// optional double x = 1 [default = nan];
inline bool Point2D::has_x() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void Point2D::set_has_x() {
  _has_bits_[0] |= 0x00000001u;
}
inline void Point2D::clear_has_x() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void Point2D::clear_x() {
  x_ = ::google::protobuf::internal::NaN();
  clear_has_x();
}
inline double Point2D::x() const {
  // @@protoc_insertion_point(field_get:perception.Point2D.x)
  return x_;
}
inline void Point2D::set_x(double value) {
  set_has_x();
  x_ = value;
  // @@protoc_insertion_point(field_set:perception.Point2D.x)
}

// optional double y = 2 [default = nan];
inline bool Point2D::has_y() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void Point2D::set_has_y() {
  _has_bits_[0] |= 0x00000002u;
}
inline void Point2D::clear_has_y() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void Point2D::clear_y() {
  y_ = ::google::protobuf::internal::NaN();
  clear_has_y();
}
inline double Point2D::y() const {
  // @@protoc_insertion_point(field_get:perception.Point2D.y)
  return y_;
}
inline void Point2D::set_y(double value) {
  set_has_y();
  y_ = value;
  // @@protoc_insertion_point(field_set:perception.Point2D.y)
}

// -------------------------------------------------------------------

// LaneMark

// optional .perception.LaneMarkColor color = 1;
inline bool LaneMark::has_color() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void LaneMark::set_has_color() {
  _has_bits_[0] |= 0x00000001u;
}
inline void LaneMark::clear_has_color() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void LaneMark::clear_color() {
  color_ = 0;
  clear_has_color();
}
inline ::perception::LaneMarkColor LaneMark::color() const {
  // @@protoc_insertion_point(field_get:perception.LaneMark.color)
  return static_cast< ::perception::LaneMarkColor >(color_);
}
inline void LaneMark::set_color(::perception::LaneMarkColor value) {
  assert(::perception::LaneMarkColor_IsValid(value));
  set_has_color();
  color_ = value;
  // @@protoc_insertion_point(field_set:perception.LaneMark.color)
}

// optional .perception.LaneMarkType type = 2;
inline bool LaneMark::has_type() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void LaneMark::set_has_type() {
  _has_bits_[0] |= 0x00000002u;
}
inline void LaneMark::clear_has_type() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void LaneMark::clear_type() {
  type_ = 0;
  clear_has_type();
}
inline ::perception::LaneMarkType LaneMark::type() const {
  // @@protoc_insertion_point(field_get:perception.LaneMark.type)
  return static_cast< ::perception::LaneMarkType >(type_);
}
inline void LaneMark::set_type(::perception::LaneMarkType value) {
  assert(::perception::LaneMarkType_IsValid(value));
  set_has_type();
  type_ = value;
  // @@protoc_insertion_point(field_set:perception.LaneMark.type)
}

// optional float confidence = 3;
inline bool LaneMark::has_confidence() const {
  return (_has_bits_[0] & 0x00000004u) != 0;
}
inline void LaneMark::set_has_confidence() {
  _has_bits_[0] |= 0x00000004u;
}
inline void LaneMark::clear_has_confidence() {
  _has_bits_[0] &= ~0x00000004u;
}
inline void LaneMark::clear_confidence() {
  confidence_ = 0;
  clear_has_confidence();
}
inline float LaneMark::confidence() const {
  // @@protoc_insertion_point(field_get:perception.LaneMark.confidence)
  return confidence_;
}
inline void LaneMark::set_confidence(float value) {
  set_has_confidence();
  confidence_ = value;
  // @@protoc_insertion_point(field_set:perception.LaneMark.confidence)
}

// repeated .perception.Point2D points = 4;
inline int LaneMark::points_size() const {
  return points_.size();
}
inline void LaneMark::clear_points() {
  points_.Clear();
}
inline const ::perception::Point2D& LaneMark::points(int index) const {
  // @@protoc_insertion_point(field_get:perception.LaneMark.points)
  return points_.Get(index);
}
inline ::perception::Point2D* LaneMark::mutable_points(int index) {
  // @@protoc_insertion_point(field_mutable:perception.LaneMark.points)
  return points_.Mutable(index);
}
inline ::perception::Point2D* LaneMark::add_points() {
  // @@protoc_insertion_point(field_add:perception.LaneMark.points)
  return points_.Add();
}
inline const ::google::protobuf::RepeatedPtrField< ::perception::Point2D >&
LaneMark::points() const {
  // @@protoc_insertion_point(field_list:perception.LaneMark.points)
  return points_;
}
inline ::google::protobuf::RepeatedPtrField< ::perception::Point2D >*
LaneMark::mutable_points() {
  // @@protoc_insertion_point(field_mutable_list:perception.LaneMark.points)
  return &points_;
}

// -------------------------------------------------------------------

// LaneCenter

// repeated .perception.Point2D points = 1;
inline int LaneCenter::points_size() const {
  return points_.size();
}
inline void LaneCenter::clear_points() {
  points_.Clear();
}
inline const ::perception::Point2D& LaneCenter::points(int index) const {
  // @@protoc_insertion_point(field_get:perception.LaneCenter.points)
  return points_.Get(index);
}
inline ::perception::Point2D* LaneCenter::mutable_points(int index) {
  // @@protoc_insertion_point(field_mutable:perception.LaneCenter.points)
  return points_.Mutable(index);
}
inline ::perception::Point2D* LaneCenter::add_points() {
  // @@protoc_insertion_point(field_add:perception.LaneCenter.points)
  return points_.Add();
}
inline const ::google::protobuf::RepeatedPtrField< ::perception::Point2D >&
LaneCenter::points() const {
  // @@protoc_insertion_point(field_list:perception.LaneCenter.points)
  return points_;
}
inline ::google::protobuf::RepeatedPtrField< ::perception::Point2D >*
LaneCenter::mutable_points() {
  // @@protoc_insertion_point(field_mutable_list:perception.LaneCenter.points)
  return &points_;
}

// -------------------------------------------------------------------

// LaneMarks

// optional .common.Header header = 1;
inline bool LaneMarks::has_header() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void LaneMarks::set_has_header() {
  _has_bits_[0] |= 0x00000001u;
}
inline void LaneMarks::clear_has_header() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void LaneMarks::clear_header() {
  if (header_ != NULL) header_->::common::Header::Clear();
  clear_has_header();
}
inline const ::common::Header& LaneMarks::header() const {
  // @@protoc_insertion_point(field_get:perception.LaneMarks.header)
  return header_ != NULL ? *header_ : *default_instance_->header_;
}
inline ::common::Header* LaneMarks::mutable_header() {
  set_has_header();
  if (header_ == NULL) header_ = new ::common::Header;
  // @@protoc_insertion_point(field_mutable:perception.LaneMarks.header)
  return header_;
}
inline ::common::Header* LaneMarks::release_header() {
  clear_has_header();
  ::common::Header* temp = header_;
  header_ = NULL;
  return temp;
}
inline void LaneMarks::set_allocated_header(::common::Header* header) {
  delete header_;
  header_ = header;
  if (header) {
    set_has_header();
  } else {
    clear_has_header();
  }
  // @@protoc_insertion_point(field_set_allocated:perception.LaneMarks.header)
}

// optional .perception.LaneMark left = 2;
inline bool LaneMarks::has_left() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void LaneMarks::set_has_left() {
  _has_bits_[0] |= 0x00000002u;
}
inline void LaneMarks::clear_has_left() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void LaneMarks::clear_left() {
  if (left_ != NULL) left_->::perception::LaneMark::Clear();
  clear_has_left();
}
inline const ::perception::LaneMark& LaneMarks::left() const {
  // @@protoc_insertion_point(field_get:perception.LaneMarks.left)
  return left_ != NULL ? *left_ : *default_instance_->left_;
}
inline ::perception::LaneMark* LaneMarks::mutable_left() {
  set_has_left();
  if (left_ == NULL) left_ = new ::perception::LaneMark;
  // @@protoc_insertion_point(field_mutable:perception.LaneMarks.left)
  return left_;
}
inline ::perception::LaneMark* LaneMarks::release_left() {
  clear_has_left();
  ::perception::LaneMark* temp = left_;
  left_ = NULL;
  return temp;
}
inline void LaneMarks::set_allocated_left(::perception::LaneMark* left) {
  delete left_;
  left_ = left;
  if (left) {
    set_has_left();
  } else {
    clear_has_left();
  }
  // @@protoc_insertion_point(field_set_allocated:perception.LaneMarks.left)
}

// optional .perception.LaneMark right = 3;
inline bool LaneMarks::has_right() const {
  return (_has_bits_[0] & 0x00000004u) != 0;
}
inline void LaneMarks::set_has_right() {
  _has_bits_[0] |= 0x00000004u;
}
inline void LaneMarks::clear_has_right() {
  _has_bits_[0] &= ~0x00000004u;
}
inline void LaneMarks::clear_right() {
  if (right_ != NULL) right_->::perception::LaneMark::Clear();
  clear_has_right();
}
inline const ::perception::LaneMark& LaneMarks::right() const {
  // @@protoc_insertion_point(field_get:perception.LaneMarks.right)
  return right_ != NULL ? *right_ : *default_instance_->right_;
}
inline ::perception::LaneMark* LaneMarks::mutable_right() {
  set_has_right();
  if (right_ == NULL) right_ = new ::perception::LaneMark;
  // @@protoc_insertion_point(field_mutable:perception.LaneMarks.right)
  return right_;
}
inline ::perception::LaneMark* LaneMarks::release_right() {
  clear_has_right();
  ::perception::LaneMark* temp = right_;
  right_ = NULL;
  return temp;
}
inline void LaneMarks::set_allocated_right(::perception::LaneMark* right) {
  delete right_;
  right_ = right;
  if (right) {
    set_has_right();
  } else {
    clear_has_right();
  }
  // @@protoc_insertion_point(field_set_allocated:perception.LaneMarks.right)
}

// optional .perception.LaneMark left2 = 4;
inline bool LaneMarks::has_left2() const {
  return (_has_bits_[0] & 0x00000008u) != 0;
}
inline void LaneMarks::set_has_left2() {
  _has_bits_[0] |= 0x00000008u;
}
inline void LaneMarks::clear_has_left2() {
  _has_bits_[0] &= ~0x00000008u;
}
inline void LaneMarks::clear_left2() {
  if (left2_ != NULL) left2_->::perception::LaneMark::Clear();
  clear_has_left2();
}
inline const ::perception::LaneMark& LaneMarks::left2() const {
  // @@protoc_insertion_point(field_get:perception.LaneMarks.left2)
  return left2_ != NULL ? *left2_ : *default_instance_->left2_;
}
inline ::perception::LaneMark* LaneMarks::mutable_left2() {
  set_has_left2();
  if (left2_ == NULL) left2_ = new ::perception::LaneMark;
  // @@protoc_insertion_point(field_mutable:perception.LaneMarks.left2)
  return left2_;
}
inline ::perception::LaneMark* LaneMarks::release_left2() {
  clear_has_left2();
  ::perception::LaneMark* temp = left2_;
  left2_ = NULL;
  return temp;
}
inline void LaneMarks::set_allocated_left2(::perception::LaneMark* left2) {
  delete left2_;
  left2_ = left2;
  if (left2) {
    set_has_left2();
  } else {
    clear_has_left2();
  }
  // @@protoc_insertion_point(field_set_allocated:perception.LaneMarks.left2)
}

// optional .perception.LaneMark right2 = 5;
inline bool LaneMarks::has_right2() const {
  return (_has_bits_[0] & 0x00000010u) != 0;
}
inline void LaneMarks::set_has_right2() {
  _has_bits_[0] |= 0x00000010u;
}
inline void LaneMarks::clear_has_right2() {
  _has_bits_[0] &= ~0x00000010u;
}
inline void LaneMarks::clear_right2() {
  if (right2_ != NULL) right2_->::perception::LaneMark::Clear();
  clear_has_right2();
}
inline const ::perception::LaneMark& LaneMarks::right2() const {
  // @@protoc_insertion_point(field_get:perception.LaneMarks.right2)
  return right2_ != NULL ? *right2_ : *default_instance_->right2_;
}
inline ::perception::LaneMark* LaneMarks::mutable_right2() {
  set_has_right2();
  if (right2_ == NULL) right2_ = new ::perception::LaneMark;
  // @@protoc_insertion_point(field_mutable:perception.LaneMarks.right2)
  return right2_;
}
inline ::perception::LaneMark* LaneMarks::release_right2() {
  clear_has_right2();
  ::perception::LaneMark* temp = right2_;
  right2_ = NULL;
  return temp;
}
inline void LaneMarks::set_allocated_right2(::perception::LaneMark* right2) {
  delete right2_;
  right2_ = right2;
  if (right2) {
    set_has_right2();
  } else {
    clear_has_right2();
  }
  // @@protoc_insertion_point(field_set_allocated:perception.LaneMarks.right2)
}


// @@protoc_insertion_point(namespace_scope)

}  // namespace perception

#ifndef SWIG
namespace google {
namespace protobuf {

template <> struct is_proto_enum< ::perception::LaneMarkColor> : ::google::protobuf::internal::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor< ::perception::LaneMarkColor>() {
  return ::perception::LaneMarkColor_descriptor();
}
template <> struct is_proto_enum< ::perception::LaneMarkType> : ::google::protobuf::internal::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor< ::perception::LaneMarkType>() {
  return ::perception::LaneMarkType_descriptor();
}

}  // namespace google
}  // namespace protobuf
#endif  // SWIG

// @@protoc_insertion_point(global_scope)

#endif  // PROTOBUF_lane_5fmark_2eproto__INCLUDED

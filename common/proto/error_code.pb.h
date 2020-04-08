// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: error_code.proto

#ifndef PROTOBUF_error_5fcode_2eproto__INCLUDED
#define PROTOBUF_error_5fcode_2eproto__INCLUDED

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
// @@protoc_insertion_point(includes)

namespace common {

// Internal implementation detail -- do not call these.
void  protobuf_AddDesc_error_5fcode_2eproto();
void protobuf_AssignDesc_error_5fcode_2eproto();
void protobuf_ShutdownFile_error_5fcode_2eproto();

class StatusPb;

enum ErrorCode {
  OK = 0,
  CONTROL_ERROR = 1000,
  CONTROL_INIT_ERROR = 1001,
  CONTROL_COMPUTE_ERROR = 1002,
  CONTROL_ESTOP_ERROR = 1003,
  CANBUS_ERROR = 2000,
  CAN_CLIENT_ERROR_BASE = 2100,
  CAN_CLIENT_ERROR_OPEN_DEVICE_FAILED = 2101,
  CAN_CLIENT_ERROR_FRAME_NUM = 2102,
  CAN_CLIENT_ERROR_SEND_FAILED = 2103,
  CAN_CLIENT_ERROR_RECV_FAILED = 2104,
  LOCALIZATION_ERROR = 3000,
  LOCALIZATION_ERROR_MSG = 3100,
  LOCALIZATION_ERROR_LIDAR = 3200,
  LOCALIZATION_ERROR_INTEG = 3300,
  LOCALIZATION_ERROR_GNSS = 3400,
  PERCEPTION_ERROR = 4000,
  PERCEPTION_ERROR_TF = 4001,
  PERCEPTION_ERROR_PROCESS = 4002,
  PERCEPTION_FATAL = 4003,
  PERCEPTION_ERROR_NONE = 4004,
  PERCEPTION_ERROR_UNKNOWN = 4005,
  PREDICTION_ERROR = 5000,
  PLANNING_ERROR = 6000,
  PLANNING_ERROR_NOT_READY = 6001,
  HDMAP_DATA_ERROR = 7000,
  ROUTING_ERROR = 8000,
  ROUTING_ERROR_REQUEST = 8001,
  ROUTING_ERROR_RESPONSE = 8002,
  ROUTING_ERROR_NOT_READY = 8003,
  END_OF_INPUT = 9000,
  HTTP_LOGIC_ERROR = 10000,
  HTTP_RUNTIME_ERROR = 10001,
  RELATIVE_MAP_ERROR = 11000,
  RELATIVE_MAP_NOT_READY = 11001,
  DRIVER_ERROR_GNSS = 12000,
  DRIVER_ERROR_VELODYNE = 13000,
  STORYTELLING_ERROR = 14000
};
bool ErrorCode_IsValid(int value);
const ErrorCode ErrorCode_MIN = OK;
const ErrorCode ErrorCode_MAX = STORYTELLING_ERROR;
const int ErrorCode_ARRAYSIZE = ErrorCode_MAX + 1;

const ::google::protobuf::EnumDescriptor* ErrorCode_descriptor();
inline const ::std::string& ErrorCode_Name(ErrorCode value) {
  return ::google::protobuf::internal::NameOfEnum(
    ErrorCode_descriptor(), value);
}
inline bool ErrorCode_Parse(
    const ::std::string& name, ErrorCode* value) {
  return ::google::protobuf::internal::ParseNamedEnum<ErrorCode>(
    ErrorCode_descriptor(), name, value);
}
// ===================================================================

class StatusPb : public ::google::protobuf::Message {
 public:
  StatusPb();
  virtual ~StatusPb();

  StatusPb(const StatusPb& from);

  inline StatusPb& operator=(const StatusPb& from) {
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
  static const StatusPb& default_instance();

  void Swap(StatusPb* other);

  // implements Message ----------------------------------------------

  StatusPb* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const StatusPb& from);
  void MergeFrom(const StatusPb& from);
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

  // optional .common.ErrorCode error_code = 1 [default = OK];
  inline bool has_error_code() const;
  inline void clear_error_code();
  static const int kErrorCodeFieldNumber = 1;
  inline ::common::ErrorCode error_code() const;
  inline void set_error_code(::common::ErrorCode value);

  // optional string msg = 2;
  inline bool has_msg() const;
  inline void clear_msg();
  static const int kMsgFieldNumber = 2;
  inline const ::std::string& msg() const;
  inline void set_msg(const ::std::string& value);
  inline void set_msg(const char* value);
  inline void set_msg(const char* value, size_t size);
  inline ::std::string* mutable_msg();
  inline ::std::string* release_msg();
  inline void set_allocated_msg(::std::string* msg);

  // @@protoc_insertion_point(class_scope:common.StatusPb)
 private:
  inline void set_has_error_code();
  inline void clear_has_error_code();
  inline void set_has_msg();
  inline void clear_has_msg();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  ::std::string* msg_;
  int error_code_;
  friend void  protobuf_AddDesc_error_5fcode_2eproto();
  friend void protobuf_AssignDesc_error_5fcode_2eproto();
  friend void protobuf_ShutdownFile_error_5fcode_2eproto();

  void InitAsDefaultInstance();
  static StatusPb* default_instance_;
};
// ===================================================================


// ===================================================================

// StatusPb

// optional .common.ErrorCode error_code = 1 [default = OK];
inline bool StatusPb::has_error_code() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void StatusPb::set_has_error_code() {
  _has_bits_[0] |= 0x00000001u;
}
inline void StatusPb::clear_has_error_code() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void StatusPb::clear_error_code() {
  error_code_ = 0;
  clear_has_error_code();
}
inline ::common::ErrorCode StatusPb::error_code() const {
  // @@protoc_insertion_point(field_get:common.StatusPb.error_code)
  return static_cast< ::common::ErrorCode >(error_code_);
}
inline void StatusPb::set_error_code(::common::ErrorCode value) {
  assert(::common::ErrorCode_IsValid(value));
  set_has_error_code();
  error_code_ = value;
  // @@protoc_insertion_point(field_set:common.StatusPb.error_code)
}

// optional string msg = 2;
inline bool StatusPb::has_msg() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void StatusPb::set_has_msg() {
  _has_bits_[0] |= 0x00000002u;
}
inline void StatusPb::clear_has_msg() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void StatusPb::clear_msg() {
  if (msg_ != &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    msg_->clear();
  }
  clear_has_msg();
}
inline const ::std::string& StatusPb::msg() const {
  // @@protoc_insertion_point(field_get:common.StatusPb.msg)
  return *msg_;
}
inline void StatusPb::set_msg(const ::std::string& value) {
  set_has_msg();
  if (msg_ == &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    msg_ = new ::std::string;
  }
  msg_->assign(value);
  // @@protoc_insertion_point(field_set:common.StatusPb.msg)
}
inline void StatusPb::set_msg(const char* value) {
  set_has_msg();
  if (msg_ == &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    msg_ = new ::std::string;
  }
  msg_->assign(value);
  // @@protoc_insertion_point(field_set_char:common.StatusPb.msg)
}
inline void StatusPb::set_msg(const char* value, size_t size) {
  set_has_msg();
  if (msg_ == &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    msg_ = new ::std::string;
  }
  msg_->assign(reinterpret_cast<const char*>(value), size);
  // @@protoc_insertion_point(field_set_pointer:common.StatusPb.msg)
}
inline ::std::string* StatusPb::mutable_msg() {
  set_has_msg();
  if (msg_ == &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    msg_ = new ::std::string;
  }
  // @@protoc_insertion_point(field_mutable:common.StatusPb.msg)
  return msg_;
}
inline ::std::string* StatusPb::release_msg() {
  clear_has_msg();
  if (msg_ == &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    return NULL;
  } else {
    ::std::string* temp = msg_;
    msg_ = const_cast< ::std::string*>(&::google::protobuf::internal::GetEmptyStringAlreadyInited());
    return temp;
  }
}
inline void StatusPb::set_allocated_msg(::std::string* msg) {
  if (msg_ != &::google::protobuf::internal::GetEmptyStringAlreadyInited()) {
    delete msg_;
  }
  if (msg) {
    set_has_msg();
    msg_ = msg;
  } else {
    clear_has_msg();
    msg_ = const_cast< ::std::string*>(&::google::protobuf::internal::GetEmptyStringAlreadyInited());
  }
  // @@protoc_insertion_point(field_set_allocated:common.StatusPb.msg)
}


// @@protoc_insertion_point(namespace_scope)

}  // namespace common

#ifndef SWIG
namespace google {
namespace protobuf {

template <> struct is_proto_enum< ::common::ErrorCode> : ::google::protobuf::internal::true_type {};
template <>
inline const EnumDescriptor* GetEnumDescriptor< ::common::ErrorCode>() {
  return ::common::ErrorCode_descriptor();
}

}  // namespace google
}  // namespace protobuf
#endif  // SWIG

// @@protoc_insertion_point(global_scope)

#endif  // PROTOBUF_error_5fcode_2eproto__INCLUDED

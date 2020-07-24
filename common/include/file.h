#pragma once
#include <dirent.h>
#include <fcntl.h>
#include <glob.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <cerrno>
#include <climits>
#include <cstddef>
#include <fstream>
#include <string>

#include "common/util/log.h"
#include "google/protobuf/io/zero_copy_stream_impl.h"
#include "google/protobuf/text_format.h"

namespace common {

// file type: file or directory
enum FileType { TYPE_FILE, TYPE_DIR };

bool GetProtoFromASCIIFile(const std::string &file_name,        
    google::protobuf::Message *message) {
  using google::protobuf::TextFormat;
  using google::protobuf::io::FileInputStream;
  using google::protobuf::io::ZeroCopyInputStream;
  int file_descriptor = open(file_name.c_str(), O_RDONLY);

  if (file_descriptor < 0) {
    AERROR << "Failed to open file " << file_name << " in text mode.";
    // Failed to open;
    return false;
  }

  ZeroCopyInputStream *input = new FileInputStream(file_descriptor);
  bool success = TextFormat::Parse(input, message);
  if (!success) {
    AERROR << "Failed to parse file " << file_name << " as text proto.";
  }
  delete input;
  close(file_descriptor);
  return success;
}

bool GetProtoFromBinaryFile(const std::string &file_name,
    google::protobuf::Message *message) {
  std::fstream input(file_name, std::ios::in | std::ios::binary);
  if (!input.good()) {
    AERROR << "Failed to open file " << file_name << " in binary mode.";
    return false;
  }
  if (!message->ParseFromIstream(&input)) {
    AERROR << "Failed to parse file " << file_name << " as binary proto.";
    return false;
  }
  return true;
}

bool GetProtoFromFile(const std::string &file_name,
    google::protobuf::Message *message) {
  static const std::string kBinExt = ".bin";
  if (std::equal(kBinExt.rbegin(), kBinExt.rend(), file_name.rbegin())) {
    return GetProtoFromBinaryFile(file_name, message) ||
      GetProtoFromASCIIFile(file_name, message);
  }

  return GetProtoFromASCIIFile(file_name, message) ||
    GetProtoFromBinaryFile(file_name, message);
}


}

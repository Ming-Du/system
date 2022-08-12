#include <fstream>
#include <string>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

#include "log.h"
#include "pb_utils.h"

#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/text_format.h>

namespace common {

bool PathExists(const std::string &path) {
  struct stat info;
  return stat(path.c_str(), &info) == 0;
}

static bool SetProtoToASCIIFile(const google::protobuf::Message &message,
                         int file_descriptor) {
  using google::protobuf::TextFormat;
  using google::protobuf::io::FileOutputStream;
  using google::protobuf::io::ZeroCopyOutputStream;
  if (file_descriptor < 0) {
    AERROR << "Invalid file descriptor.";
    return false;
  }
  ZeroCopyOutputStream *output = new FileOutputStream(file_descriptor);
  bool success = TextFormat::Print(message, output);
  delete output;
  close(file_descriptor);
  return success;
}

bool SetProtoToASCIIFile(const google::protobuf::Message &message,
                         const std::string &file_name) {
  int fd = open(file_name.c_str(), O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU);
  if (fd < 0) {
    AERROR << "Unable to open file " << file_name << " to write.";
    return false;
  }
  return SetProtoToASCIIFile(message, fd);
}

bool GetProtoFromASCIIFile(const std::string &file_name,
                           google::protobuf::Message &message) {
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
  bool success = TextFormat::Parse(input, &message, true, true);
  if (!success) {
    AERROR << "Failed to parse file " << file_name << " as text proto.";
  }
  delete input;
  close(file_descriptor);
  return success;
}

bool SetProtoToBinaryFile(const google::protobuf::Message &message,
                          const std::string &file_name) {
  std::fstream output(file_name.c_str(),
                      std::ios::out | std::ios::trunc | std::ios::binary);
  return message.SerializeToOstream(&output);
}

bool GetProtoFromBinaryFile(const std::string &file_name,
                            google::protobuf::Message &message) {
  std::fstream input(file_name.c_str(), std::ios::in | std::ios::binary);
  if (!input.good()) {
    AERROR << "Failed to open file " << file_name << " in binary mode.";
    return false;
  }
  if (!message.ParseFromIstream(&input)) {
    AERROR << "Failed to parse file " << file_name << " as binary proto.";
    return false;
  }
  return true;
}

bool GetProtoFromFile(const std::string &file_name,
                      google::protobuf::Message &message) {
  // Try the binary parser first if it's much likely a binary proto.
  static const std::string kBinExt = ".bin";
  if (std::equal(kBinExt.rbegin(), kBinExt.rend(), file_name.rbegin())) {
    return GetProtoFromBinaryFile(file_name, message) ||
           GetProtoFromASCIIFile(file_name, message);
  }

  return GetProtoFromASCIIFile(file_name, message) ||
         GetProtoFromBinaryFile(file_name, message);
}

// output memory stream
class omstreambuf : public std::streambuf
{
private:
  std::vector<char> buf;
  #define BUFFER_SIZE 1024
public:
  omstreambuf() : buf(BUFFER_SIZE)
  {
    setp(buf.data(), buf.data() + buf.size());
  }
  template <class bufT>
  void copy_to(std::vector<bufT>& v) const
  {
    int len = pptr() - pbase();
    v.resize(len);
    memcpy((void*)v.data(), buf.data(), len);
  }
private:
  virtual int overflow(int c)
  {
    if (c == EOF)
    {
      return !EOF;
    }
    else
    {
      size_t old_size = buf.size();
      buf.resize(old_size * 2);
      setp(buf.data(), buf.data() + buf.size());
      pbump(static_cast<int>(old_size));
      return sputc(c);
    }
  }
};
// input memory stream
class imstreambuf : public std::streambuf
{
public:
  imstreambuf(char* gbeg, char* gend)
  {
    setg(gbeg, gbeg, gend);
  }
};


bool SerializeProto(const google::protobuf::Message &message, std::vector<uint8_t>& buffer)
{
  omstreambuf mb;
  std::ostream output(&mb);
  if (message.SerializeToOstream(&output))
  {
    mb.copy_to<uint8_t>(buffer);
    return true;
  }
  return false;
}

bool DeserializeProto(google::protobuf::Message &message, const std::vector<uint8_t>& buffer)
{
  imstreambuf mb((char*)buffer.data(), (char*)(buffer.data() + buffer.size()));
  std::istream input(&mb);
  return message.ParseFromIstream(&input);
}

}  // namespace common


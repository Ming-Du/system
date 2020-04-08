#ifndef _PB_UTILS_H_
#define _PB_UTILS_H_

#include <string>

#include <google/protobuf/message.h>

namespace common {

/**
 * @brief Sets the content of the file specified by the file_name to be the
 *        ascii representation of the input protobuf.
 * @param message The proto to output to the specified file.
 * @param file_name The name of the target file to set the content.
 * @return If the action is successful.
 */
bool SetProtoToASCIIFile(const google::protobuf::Message &message,
                         const std::string &file_name);

/**
 * @brief Parses the content of the file specified by the file_name as ascii
 *        representation of protobufs, and merges the parsed content to the
 *        proto.
 * @param file_name The name of the file to parse whose content.
 * @param message The proto to carry the parsed content in the specified file.
 * @return If the action is successful.
 */
bool GetProtoFromASCIIFile(const std::string &file_name,
                           google::protobuf::Message &message);

/**
 * @brief Sets the content of the file specified by the file_name to be the
 *        binary representation of the input protobuf.
 * @param message The proto to output to the specified file.
 * @param file_name The name of the target file to set the content.
 * @return If the action is successful.
 */
bool SetProtoToBinaryFile(const google::protobuf::Message &message,
                          const std::string &file_name);

/**
 * @brief Parses the content of the file specified by the file_name as binary
 *        representation of protobufs, and merges the parsed content to the
 *        proto.
 * @param file_name The name of the file to parse whose content.
 * @param message The proto to carry the parsed content in the specified file.
 * @return If the action is successful.
 */
bool GetProtoFromBinaryFile(const std::string &file_name,
                            google::protobuf::Message &message);

/**
 * @brief Parses the content of the file specified by the file_name as a
 *        representation of protobufs, and merges the parsed content to the
 *        proto.
 * @param file_name The name of the file to parse whose content.
 * @param message The proto to carry the parsed content in the specified file.
 * @return If the action is successful.
 */
bool GetProtoFromFile(const std::string &file_name,
                      google::protobuf::Message &message);


bool SerializeProto(const google::protobuf::Message &message, std::vector<uint8_t>& buffer);

bool DeserializeProto(google::protobuf::Message &message, const std::vector<uint8_t>& buffer);


}  // namespace common

#endif  // _PB_UTILS_H_

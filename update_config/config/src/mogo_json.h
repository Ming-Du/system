#ifndef JSON_H_
#define JSON_H_

#include <string>
#include "jsoncpp/json/json.h"
#include "const.h"


class MyJson
{
public:
	MyJson();
	MyJson(uint16 taskCode, uint16 mode, const char* funName);
	MyJson( const Json::Value& other);
	virtual ~MyJson();

	bool parse(std::istream& is);
	bool parse(const std::string& s);
	bool parse(char* start, char* end);
	bool StrToObject(const std::string& str, Json::Value& obj);
	bool getString(const char* name, std::string& ret);
	bool getInt(const char* name, int& ret);
	bool getLong(const char* name, long long int& ret);
	//bool getInt(const char* name, unsigned int& ret);
	bool getBool(const char* name, bool& ret);
	bool getDouble(const char* name, double& ret);
	bool getFloat(const char* name, float& ret);
	size_t getSize(const char* name);
	size_t getSize();
	void  getArrayStr(int index, std::string& ret);
	void  getArrayStr(const char* name, int index, std::string& ret);
	void  getArrayInt(const char* name, int index, int& ret);
	bool  getArrayObj(const char* name, int index, Json::Value& ret);
	bool  getArrayObj(int index, Json::Value& ret);
	void  getArrayDouble(int index, double& ret);
	bool  getRootArrayInt(int index, int& ret);
	Json::Value& getObjectIndex( const char* name, int index );
	bool getObject( const char* name, Json::Value &obj );
	bool  getArray(const char* name, Json::Value& obj);
	Json::Value& getObjectIndex(int index);
	Json::Value::Members getKeyNames();
	Json::Value* getRoot()
	{
		return &m_jRoot;
	}

	bool empty()
	{
		return m_jRoot.empty();
	}
private:
	const char*     m_funName;
	Json::Value     m_jRoot;
	Json::Reader    m_jReader;
	bool		m_isCopying;
};

#endif

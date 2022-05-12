#include "mogo_json.h"


using namespace Json;

MyJson::MyJson()
{
	m_jRoot.clear();
	m_jReader = Json::Features::strictMode();
	m_isCopying = false;
	m_funName		= "";
}

MyJson::MyJson(uint16 taskCode, uint16 mode, const char* funName)
{
	m_funName = funName;
	m_isCopying = false;
}

MyJson::~MyJson()
{
	if ( ! m_jRoot.empty() && !m_isCopying )
	{
		m_jRoot.clear();
	}
}


MyJson::MyJson( const Json::Value& other )
{
	m_jRoot = other;
	m_isCopying = true;
}


bool MyJson::StrToObject(const std::string& str, Json::Value& obj)
{
	obj.clear();
	Json::Reader pReader;
	if (!pReader.parse(str, obj))
	{
		return false;
	}
	return true;
}

bool MyJson::parse(std::istream& is)
{
	m_jRoot.clear();
	if ( !m_jReader.parse(is, m_jRoot) )
	{
		return false;
	}
	return true;
}



bool MyJson::parse(const std::string& s)
{
	m_jRoot.clear();
	if ( !m_jReader.parse(s, m_jRoot) )
	{
		return false;
	}
	return true;
}


bool MyJson::parse(char* start, char* end)
{
	m_jRoot.clear();
	if ( !m_jReader.parse(start, end, m_jRoot) )
	{
		return false;
	}
	return true;
}


bool MyJson::getString( const char* name, std::string& ret)
{
	if(name != NULL)
	{
		if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isString() )
		{
			ret = m_jRoot[name].asString();
			return true;
		}
		return false;
	}
	else
	{
		if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot.isString() )
		{
			ret = m_jRoot.asString();
			return true;
		}
		return false;

	}
}

bool MyJson::getInt( const char* name, int& ret)
{
	if(name != NULL)
	{
		if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isInt() )
		{
			ret = m_jRoot[name].asInt();
			return true;
		}
		return false;
	}
	else
	{
		if ( !m_jRoot.empty()  && !m_jRoot.isNull() && m_jRoot.isInt() )
		{
			ret = m_jRoot.asInt();
			return true;
		}
		return false;
	}
}


/*
   bool MyJson::getInt(int &ret)
   {
   if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot.isInt() )
   {
   ret = m_jRoot.asInt();
   return true;
   }
   return false;
   }
   */

bool MyJson::getLong(const char* name, long long int& ret)//asInt64
{
	if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isInt64() )
	{
		ret = m_jRoot[name].asInt64();
		return true;
	}
	return false;
}

bool MyJson::getFloat(const char* name, float& ret)
{
	if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isDouble() )
	{
		ret = m_jRoot[name].asFloat();
		return true;
	}
	return false;
}

bool MyJson::getDouble(const char* name, double& ret)
{
	if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isDouble() )
	{
		ret = m_jRoot[name].asDouble();
		return true;
	}
	return false;
}

bool MyJson::getBool( const char* name, bool& ret)
{
	if ( !m_jRoot.empty() && !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name].isBool() )
	{
		ret = m_jRoot[name].asBool();
		return true;
	}
	return false;
}

size_t MyJson::getSize(const char* name)
{
	if ( !m_jRoot.empty() && (m_jRoot[name].isArray() || m_jRoot[name].isObject()))
	{
		return m_jRoot[name].size();
	}
	return 0;
}


size_t MyJson::getSize()
{
	if ( !m_jRoot.empty() && (m_jRoot.isArray() || m_jRoot.isObject()))
	{
		return m_jRoot.size();
	}
	return 0;
}

//void MyJson::getArrayStr(int index, std::string& ret)
//{
//}

void MyJson::getArrayStr(const char* name, int index, std::string& ret)
{
	if ( ! m_jRoot[name].isValidIndex(index) )
	{
		return;
	}
	if ( !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name][index].isString() )
	{
		ret = m_jRoot[name][index].asString();
	}
}

void MyJson::getArrayStr(int index, std::string& ret)
{
	if ( ! m_jRoot.isValidIndex(index) )
	{
		return;
	}
	if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot[index].isString() )
	{
		ret = m_jRoot[index].asString();
	}
}



void MyJson::getArrayInt(const char* name, int index, int& ret)
{
	if(name!=NULL)
	{
		if ( ! m_jRoot[name].isValidIndex(index) )
		{
			return;
		}
		if ( !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name][index].isInt() )
		{
			ret = m_jRoot[name][index].asInt();
		}
	}
	else
	{
		if ( ! m_jRoot.isValidIndex(index) )
		{
			return;
		}
		if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot[index].isInt() )
		{
			ret = m_jRoot[index].asInt();
		}
	}
}

bool MyJson::getArrayObj(const char* name, int index, Json::Value& ret)
{
	if ( ! m_jRoot[name].isValidIndex(index) )
	{
		return false;
	}
	if ( !m_jRoot[name].empty() && !m_jRoot[name].isNull() && m_jRoot[name][index].isObject() )
	{
		ret = m_jRoot[name][index];
	}
	return true;
}

bool MyJson::getArrayObj(int index, Json::Value& ret)
{
	if ( ! m_jRoot.isValidIndex(index) )
	{
		return false;
	}
	if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot[index].isObject() )
	{
		ret = m_jRoot[index];
	}
	return true;
}



void MyJson::getArrayDouble(int index, double& ret)
{
	if ( ! m_jRoot.isValidIndex(index) )
	{
		return;
	}
	if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot[index].isDouble() )
	{
		ret = m_jRoot[index].asDouble();
	}
}

/*
   bool MyJson::getRootArrayInt(int index, int& ret)
   {
   if ( !m_jRoot.isValidIndex(index) )
   {
   return false;
   }
   if ( !m_jRoot.empty() && !m_jRoot.isNull() && m_jRoot[index].isInt() )
   {
   ret = m_jRoot[index].asInt();
   }
   return true;
   }
   */

Json::Value& MyJson::getObjectIndex( const char* name, int index )
{
	if ( m_jRoot[name].empty() && !m_jRoot[name].isValidIndex(index) )
	{
		return m_jRoot;
	}
	return m_jRoot[name][index];
}

Json::Value& MyJson::getObjectIndex(int index)
{
	if ( m_jRoot.empty() && !m_jRoot.isValidIndex(index) )
	{
		return m_jRoot;
	}
	return m_jRoot[index];
}

bool MyJson::getObject( const char* name, Json::Value& obj )
{
	if ( !m_jRoot[name].isObject() )
	{
		return false;
	}
	obj = m_jRoot[name];
	return true;
}

bool  MyJson::getArray(const char* name, Json::Value& obj)
{
	if ( !m_jRoot[name].isArray() )
	{
		return false;
	}
	obj = m_jRoot[name];
	return true;
}

Json::Value::Members MyJson::getKeyNames()
{
	return m_jRoot.getMemberNames();
}

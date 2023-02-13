import os
import sys
import logging
import traceback
import json
from threading import RLock

def configure_logging():
    """
    Setup filesystem logging for the master
    """
    filename = 'master.log'
    # #988 __log command-line remapping argument
    import rosgraph.names
    import rosgraph.roslogging
    mappings = rosgraph.names.load_mappings(sys.argv)
    if '__log' in mappings:
        logfilename_remap = mappings['__log']
        filename = os.path.abspath(logfilename_remap)
    _log_filename = rosgraph.roslogging.configure_logging('rosmaster', logging.DEBUG, filename=filename)

def logerror(msg, *args):
    configure_logging()
    _logger = logging.getLogger("rosmaster.master")
    _logger.error(msg, *args)
    if args:
        print("ERROR: " + msg % args)
    else:
        print("ERROR: " + str(msg))

def logwarn(msg, *args):
    configure_logging()
    _logger = logging.getLogger("rosmaster.master")
    _logger.warn(msg, *args)
    if args:
        print("WARN: " + msg % args)
    else:
        print("WARN: " + str(msg))

try:
    import redis
    from redis import ConnectionPool,StrictRedis
    AuthenticationError = redis.AuthenticationError
    AuthenticationWrongNumberOfArgsError = redis.AuthenticationWrongNumberOfArgsError
    BusyLoadingError = redis.BusyLoadingError
    ChildDeadlockedError = redis.ChildDeadlockedError
    ConnectionError = redis.ConnectionError
    DataError = redis.DataError
    InvalidResponse = redis.InvalidResponse
    PubSubError = redis.PubSubError
    ReadOnlyError = redis.ReadOnlyError
    RedisError = redis.RedisError
    ResponseError = redis.ResponseError
    TimeoutError = redis.TimeoutError
    WatchError = redis.WatchError
except:
    pass

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class RedisManager(object):
    def __init__(self):
        self.lock = RLock()
        self.ready = False
        self.pool = None
        self.rhost = 'localhost'
        self.rport = 6379
        self.ruser = None
        self.rpassword = None
        self.max_reconnect_times = 10
        self.connect_timeout = 1
        self.socket_timeout = 0.05

    def _read_config(self):
        config = None
        config_file = os.path.join(os.environ.get('ROS_ETC_DIR'),'rosmaster.json')
        try:
            with open(config_file,'r') as f:
                config = json.loads(f.read())
        except IOError as e:
            logerror('open config file failed:%s'%e)
            return False
        except ValueError: 
            logerror('parse config failed:%s'%e)
            return False

        try:
            self.rhost = config['redis']['host']
        except:
            self.rhost = 'localhost'
        try:
            self.rport = config['redis']['port']
        except:
            self.rport = 6379
        try:
            self.ruser = config['redis']['user']
        except:
            self.ruser = None
        try:
            self.rpassword = config['redis']['password']
        except:
            self.rpassword = None
        return True

    def connect(self,retry_times=10):
        self.lock.acquire()
        try:
            self.pool = ConnectionPool(host=self.rhost,port=self.rport, db=0, username=self.ruser,password=self.rpassword, max_connections=10,decode_responses=True)
            self.redis_handler = StrictRedis(connection_pool=self.pool,socket_connect_timeout=self.connect_timeout,socket_keepalive=True,socket_timeout=self.socket_timeout,health_check_interval=5)
        except Exception as e:
            logwarn("functions of redis are invalid:%s"%e)
            self.lock.release()
            return False
        for i in range(retry_times):
            try:
                self.redis_handler.ping()
                self.ready = True
                self.lock.release()
                return True
            except ConnectionError as e:
                logerror('Connet redis server[%s:%s] failed:%s'%(self.rhost,self.rport,e))
                self.lock.release()
                return False
            except TimeoutError as e:
                logerror('Connet redis server[%s:%s] timeout:%s'%(self.rhost,self.rport,e))
                continue
            except Exception as e:
                logerror(e)
                self.lock.release()
                return False

    def init(self):
        self.lock.acquire()
        try:
            if self.ready:
                return True
            if not self._read_config():
                return False
            return self.connect()
        finally:
            self.lock.release()

    def set(self,key,value):
        json_dict = {}
        json_dict["Data"] = value
        if isinstance(value,int):
            json_dict["Type"] = 'int'
        elif isinstance(value,float) and len(str(value)) > 7:
            json_dict["Type"] = 'double'
        elif isinstance(value,float) and len(str(value)) <= 7:
            json_dict["Type"] = 'float'
        elif isinstance(value,str):
            json_dict["Type"] = 'str'
        elif isinstance(value,bool):
            json_dict["Type"] = 'bool'
        elif isinstance(value,list):
            json_dict["Type"] = 'list'
            if len(value) > 0:
                if isinstance(value[0],int):
                    json_dict["SubType"] = 'int'
                if isinstance(value[0],float) and len(str(value[0])) > 7:
                    json_dict["SubType"] = 'double'
                elif isinstance(value[0],float) and len(str(value[0])) <= 7:
                    json_dict["SubType"] = 'float'
                elif isinstance(value[0],str):
                    json_dict["SubType"] = 'str'
                elif isinstance(value[0],bool):
                    json_dict["SubType"] = 'bool'
        elif isinstance(value,dict):
            json_dict["Type"] = 'dict'
            if len(value) > 0:
                if isinstance(value.values()[0],int):
                    json_dict["SubType"] = 'int'
                if isinstance(value.values()[0],float) and len(str(value.values()[0])) > 7:
                    json_dict["SubType"] = 'double'
                elif isinstance(value.values()[0],float) and len(str(value.values()[0])) <= 7:
                    json_dict["SubType"] = 'float'
                elif isinstance(value.values()[0],str):
                    json_dict["SubType"] = 'str'
                elif isinstance(value.values()[0],bool):
                    json_dict["SubType"] = 'bool'

        try:
            return self.redis_handler.set(key,json.dumps(json_dict))
        except (ConnectionError, TimeoutError) as e:
            raise Exception('set key failed:%s'%e)
        except Exception as e:
            raise e

    def get(self,key):
        json_str = self.redis_handler.get(key)
        if not json_str:
            raise KeyError
        try:
            return json.loads(json_str)['Data']
        except Exception as e:
            raise

    def delete(self,key):
        try:
            if self.redis_handler.delete(key) > 0:
                return True
            else:
                raise KeyError('%s is not set'%key)
        except (ConnectionError, TimeoutError) as e:
            raise Exception('delete key failed:%s'%e)
        except Exception as e:
            raise e

    def keys(self,key):
        try:
            return self.redis_handler.keys(key)
        except Exception as e:
            raise e
    
    def has_key(self,key):
        try:
            if self.redis_handler.exists(key):
                return True 
            else:
                return False
        except Exception as e:
            raise e

    def clear(self):
        try:
            return self.redis_handler.flushall()
        except:
            return False

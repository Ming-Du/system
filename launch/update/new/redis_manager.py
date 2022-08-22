import os
import logging
import redis
from redis import ConnectionPool,StrictRedis
import yaml
import traceback
import json
from threading import RLock
# from roslaunch.core import printlog,printerrlog
_loginfo = logging.getLogger("rosmaster.master").info
_logerror = logging.getLogger("rosmaster.master").error


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
        config_file = os.path.join(os.environ.get('ROS_ETC_DIR'),'rosmaster.yaml')
        try:
            with open(config_file,'r') as f:
                config = yaml.load(f.read())
        except IOError as e:
            _logerror('open config file failed:%s'%e)
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
        try:
            self.lock.acquire()
            self.pool = ConnectionPool(host=self.rhost,port=self.rport, db=0, username=self.ruser,password=self.rpassword, max_connections=3,decode_responses=True)
            self.redis_handler = StrictRedis(connection_pool=self.pool,socket_connect_timeout=self.connect_timeout,socket_keepalive=True,socket_timeout=self.socket_timeout,health_check_interval=5)
            for i in range(retry_times):
                try:
                    self.redis_handler.ping()
                    self.ready = True
                    return True
                except (ConnectionError, TimeoutError) as e:
                    _logerror('ConnectionError or TimeoutError:Cannot conneted with redis server[%s:%s]:%s'%(self.rhost,self.rport,e))
                except AuthenticationError as e:
                    _logerror('Cannot conneted with redis server[%s:%s]:%s'%(self.rhost,self.rport,e))
                    break
                except ResponseError as e:
                    _logerror('ResponseError:Server[%s:%s] response error:%s'%(self.rhost,self.rport,e))
                    return False
                except:
                    _logerror('Cannot conneted with redis server[%s:%s]'%(self.rhost,self.rport))
            return False
        finally:
            self.lock.release()

    def init(self):
        _logerror("test err log")
        _loginfo("test info log")
        try:
            self.lock.acquire()
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
        try:
            return self.redis_handler.set(key,json.dumps(json_dict))
        except (ConnectionError, TimeoutError) as e:
            raise 'set key failed:%s'%e
        except Exception as e:
            raise e

    def get(self,key):
        try:
            return json.loads(self.redis_handler.get(key))['Data']
        except Exception as e:
            raise e

    def delete(self,key):
        try:
            if self.redis_handler.delete(key) > 0:
                return True
            else:
                raise KeyError('%s is not set'%key)
        except (ConnectionError, TimeoutError) as e:
            raise 'delete key failed:%s'%e
        except Exception as e:
            raise e

    def keys(self,key):
        try:
            return self.redis_handler.keys(key)
        except Exception as e:
            raise e
    
    def has_key(self,key):
        try:
            if len(self.redis_handler.exists(key)) > 0:
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

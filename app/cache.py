from flask_redis import FlaskRedis
import json

redis_client = FlaskRedis()

def init_redis(app):
    redis_client.init_app(app)

def cache_key(prefix, *args):
    """Generate a cache key from prefix and arguments"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"

def set_cache(key, data, expire=3600):
    """Set data in cache with expiration"""
    redis_client.setex(key, expire, json.dumps(data))

def get_cache(key):
    """Get data from cache"""
    data = redis_client.get(key)
    return json.loads(data) if data else None

def invalidate_cache(pattern):
    """Invalidate all cache entries matching pattern"""
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)

REDISPASSWORD = 'plokiqikj##mlad,..ad'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/0", # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS':{"max_connections":100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "helper": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/4",  # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "orders": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/5",  # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    }
}
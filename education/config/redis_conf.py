
REDISPASSWORD = 'plokiqikj##mlad,..ad'
REDISURL = '172.31.137.187'
REDISPORT = '6379'

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
    "token": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",  # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/2",  # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "orders": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/3",  # 如果redis设置密码的话，需要以这种格式host前面是密码
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    }
}

REDISPASSWORD = 'plokiqikj##mlad,..ad'
REDISURL = '172.31.137.187'
REDISPORT = '6379'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/0".format(REDISURL, REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "token": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/1".format(REDISURL, REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/2".format(REDISURL, REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "orders": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/3".format(REDISURL, REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    }
}
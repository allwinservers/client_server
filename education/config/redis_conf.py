
REDISPASSWORD = 'plokiqikj##mlad,..ad'
REDISURL = '172.31.137.187'
REDISPORT = '6379'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/0".format(REDISURL,REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS':{"max_connections":100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "helper": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/4".format(REDISURL,REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    },
    "orders": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/5".format(REDISURL,REDISPORT),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {"max_connections": 100},
            "PASSWORD": REDISPASSWORD
        }
    }
}
import os

# ==============================================================================
# 中间件和应用
# ==============================================================================
# 自定义中间件
MIDDLEWARE_CLASSES_CUSTOM = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ServerUrl = os.environ.get('SERVERURL', 'localhost:8000')

# 自定义APP
INSTALLED_APPS_CUSTOM = [
    'apps.user',
    'apps.order',
    'apps.cache',
    'apps.public',
    'apps.pay',
    'apps.datacount',
    'apps.business',
    'apps.business_new',
    'apps.paycall',
    'apps.lastpass',
    'django_crontab'
]


# ===============================================================================
# 日志级别
# ===============================================================================
# 本地开发环境日志级别
LOG_LEVEL_DEVELOP = 'DEBUG'
# 正式环境日志级别
LOG_LEVEL_PRODUCT = os.environ.get('LOG_LEVEL', 'DEBUG')

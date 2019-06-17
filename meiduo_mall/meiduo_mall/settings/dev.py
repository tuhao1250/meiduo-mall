"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 2.1.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 也就是meiduo-mall/meiduo_mall/meiduo_mall这个目录了

# sys.path保存python解释器导包的路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x)ahr(kn8dp@ngu=a=&7iw&iwzlium2mr+d@s2_g^#d7-!l*fa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'www.meiduo.site', 'localhost', 'api.meiduo.site']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # cors跨域
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',  # 定时任务
    'haystack',  # 搜索引擎框架
    'xadmin',
    'crispy_forms',
    'reversion',
    'users.apps.UsersConfig',  # 用户模块
    'verifications.apps.VerificationsConfig',  # 图片验证码模块
    'oauth.apps.OauthConfig',  # 第三方认证模块
    'areas.apps.AreasConfig',  # 行政区划
    'goods.apps.GoodsConfig',  # 商品模块
    'contents.apps.ContentsConfig',  # 广告模块
    'carts.apps.CartsConfig',  # 购物车模块
    'orders.apps.OrdersConfig',  # 订单模块
    'payment.apps.PaymentConfig',  # 支付模块
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'meiduo',
        'HOST': '192.168.1.110',
        'PORT': 3306,
        'USER': 'meiduo',
        'PASSWORD': 'meiduo',
        'OPTIONS': {'charset': 'utf8mb4'}
    }
}

# Redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.110:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.110:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.110:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # 存储用户浏览历史记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.110:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cart": {  # 存储用户购物车数据
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.1.110:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # 配置session存储在缓存中
SESSION_CACHE_ALIAS = "session"


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# 日志的配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}


# REST framework配置
REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'meiduo_mall.utils.exceptions.exception_handler',
    # 认证机制后端
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 全局分页器配置
    'DEFAULT_PAGINATION_CLASS': 'meiduo_mall.utils.pagination.StandardResultsSetPagination',
}

# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),  # 指定token的有效期为一天
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',  # 配置注册时返回值包含用户名和用户id
}

# 配置django认证系统使用的模型类
AUTH_USER_MODEL = 'users.User'  # 格式:以点划分,点前面代表应用名,点后面表示模型类名
# 配置django认证后端采用的认证类
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://www.meiduo.site:8080",
    "http://api.meiduo.site:8000",
)

# 用于QQ登录的配置信息
QQ_APP_ID = '101474184'
QQ_APP_KEY = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
QQ_STATE = "/"

# django发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'suptest005@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'th19940713'
# 收件人看到的发件人
EMAIL_FROM = '美多商城<suptest005@163.com>'

# 配置django使用fastdfs文件存储系统
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSSTORAGE'

# FASTDFS配置
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')
FDFS_BASE_URL = 'http://192.168.1.110:8888/'

# CKEDITOR设置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 配置生成首页静态文件的目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务
CRONJOBS = [
    ('*/5 * * * *', 'contents.crons.generate_static_index_file', '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.logs') )
]

# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.1.110:9200/',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo',  # 指定elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 支付宝支付配置
ALIPAY_APPID = "2016092800619303"
ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do"
ALIPAY_DEBUG = True
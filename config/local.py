from .base import *

# 通常の console だと日本語メールのタイトルが文字化けしてしまうので回避
# ref: https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=44
#      https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=45
#      https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=46
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'config.email_backends.ReadableSubjectEmailBackend'

MEDIA_ROOT = BASE_DIR / 'media'

DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOGGING = {
    'version': 1,  # バージョンは「1」固定
    'disable_existing_loggers': False,  # 既存のログ設定を無効化しない

    # ログフォーマット
    'formatters': {
        'develop': {  # 開発用
            'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d '
                      '%(message)s'
        },
    },

    # ハンドラ
    'handlers': {
        'console': {  # コンソール出力用ハンドラ
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'develop',
        },
    },

    # ロガー
    'loggers': {
        '': {  # 自作アプリケーション全般のログを拾うロガー
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {  # Django本体が出すログ全般を拾うロガー
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # 'django.db.backends': {  # 発行されるSQL文を出力するための設定
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
    },
}

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ["127.0.0.1", ]  # debug toolbar

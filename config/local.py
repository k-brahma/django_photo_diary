from .base import *

# 通常
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# console での出力時に日本語の件名を読めるようにする
# ref: https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=44
#      https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=45
#      https://speakerdeck.com/thinkami/djangocongress-jp-2019-talk?slide=46
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

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ["127.0.0.1", ]  # debug toolbar

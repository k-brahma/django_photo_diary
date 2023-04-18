# photo_diary

写真日記アプリのデモです。

写真日記を投稿できます。  
投稿にタグをつけられます。タグで絞りこんだ一覧表示も可能です。  
投稿に対してコメントを追加できます。

## インストール

config/local.py または config/prod.py をコピーして、 config/settings.py を作成します。
.env_sample をコピーして、 .env を作成します。

SECRET_KEY を生成して .env に記載します。

SECRET_KEY は、以下のコマンドで生成できます。

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

`python manage.py check` でエラーがでていないことを確認します。

```bash
$ python manage.py check
```

`python manage.py migrate` でデータベースを作成します。

```bash
$ python manage.py migrate
```

`python manage.py createsuperuser` で管理者ユーザーを作成します。

```bash
$ python manage.py createsuperuser
```

本番環境での利用時は、 `python manage.py collectstatic` で静的ファイルを配置します。

```bash
$ python manage.py collectstatic
```

ローカル環境での動作確認には、 `python manage.py runserver` でサーバーを起動します。

```bash
$ python manage.py runserver
```

管理者としてログインしたら、以下のページに移動してください。

/admin/sites/site/1/change/

ドメイン名、表示名を example から変更してください。  
(本番環境で利用する予定のドメイン名が良いでしょう)

***

## 見どころ

### config

ローカル環境用の settings.py のサンプルとして local.py を用意しています。  
本番環境用の settings.py のサンプルとして production.py を用意しています。

これらに共通する部分については、 base.py にまとめています。

それぞれの環境では、 settings.py を local.py または production.py をコピーして配置します。

config/local.py

```python
from .base import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MEDIA_ROOT = BASE_DIR / 'media'

DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
    }
}

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ["127.0.0.1", ]  # debug toolbar
```

.gitignore では、 config.settings.py は git での管理対象外としています。

```gitignore
config/settings.py
```

***

### ライブラリの読み込み

ローカル環境用のライブラリ読み込みリストとして、 requirements/dev.txt を用意しています。  
本番環境用のライブラリ読み込みリストとして、 requirements/prod.txt を用意しています。

これらに共通する部分については、 base.txt にまとめています。

requirements/dev.txt

```requirements.txt
-r base.txt

django-debug-toolbar==4.0.0
```

***

### ユーザ:

accounts アプリに、 AbstractUser を継承した CustomUser モデルを定義しています。

accounts/models.py

```python
class CustomUser(AbstractUser):
    """
    Custom User model
    """

    def __str__(self):
        return self.email
```

config/base.py

```python
INSTALLED_APPS = [
    # ...
    'accounts.apps.AccountsConfig',
    # ...
]

# ...

AUTH_USER_MODEL = 'accounts.CustomUser'
```

ほか、 django-allauth にかかる設定を追加しています。  
AUTH_USER_MODEL も含めて以下に紹介します。

config/base.py

```python
# allauth
AUTH_USER_MODEL = 'accounts.CustomUser'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

ACCOUNT_ADAPTER = 'accounts.adapter.NoNewUsersAccountAdapter'

SITE_ID = 1
```

***

### ログアプリ

Article モデルが日記のモデルです。  
Tag モデルが日記に付けるタグのモデルです。  
Comment モデルが日記に付けるコメントのモデルです。

Article モデルには、 thumbnail というフィールドがあります。  
これは、 photo フィールドにアップロードされた画像をリサイズして利用するためのフィールドです。  
django-imagekit というライブラリの機能を使って実装しています。

log/models.py

```python
from django.db import models
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill


class Article(models.Model):
    # ...
    photo = models.ImageField(upload_to='log/photos/', blank=True, null=True, verbose_name='写真', )
    thumbnail = ImageSpecField(source='photo', processors=[ResizeToFill(100, 100)], format='JPEG',
                               options={'quality': 60}, )
```

photo フィールドが更新されるとき、通常では、 photo フィールドにアップロードされた画像をそのままサーバの残ってしまいます。  
これでは photo フィールドを更新する都度、不要な画像が残ってしまいます。

この不便を避けるため、 django-cleanup というアプリを導入しています。

config/base.py

```python
INSTALLED_APPS = [
    # ...
    'django_cleanup',
]
```

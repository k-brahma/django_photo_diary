# photo_diary

写真日記アプリのデモです。

- 写真日記を投稿できます。
- 投稿にタグをつけられます。タグで絞りこんだ一覧表示も可能です。
- 投稿に対してコメントを追加できます。

***

## インストール

### 1. requrements に記載されているパッケージをインストールする

ローカル環境の場合は以下

```bash
$ pip install -r requirements/dev.txt
```

本番環境の場合は以下

```bash
$ pip install -r requirements/prod.txt
```

### 2. settings.py を作る

config/local.py または config/production.py をコピーして、 config/settings.py を作成します。    
ローカル環境では local.py, 本番環境では production.py を使ってください。

### 3. .env ファイルを作る

.env_sample をコピーして、 .env を作成します。

### 4. .env ファイルに SECRET_KEY を書き込む

SECRET_KEY を生成して .env に記載します。  
SECRET_KEY は、以下のコマンドで生成できます。

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 5. Django の設定に問題がないことを確認する

`python manage.py check` でエラーがでていないことを確認します。

```bash
$ python manage.py check
```

### 6. データベースの設定をする

`python manage.py migrate` でデータベースを作成します。

```bash
$ python manage.py migrate
```

### 7. 管理者ユーザを作成する

`python manage.py createsuperuser` で管理者ユーザーを作成します。

```bash
$ python manage.py createsuperuser
```

### 8. 静的ファイルを配信する(本番環境のみ)

本番環境での利用時は、 `python manage.py collectstatic` で静的ファイルを配信します。

```bash
$ python manage.py collectstatic
```

### 9. サーバを起動する(ローカル環境のみ)

ローカル環境での動作確認には、 `python manage.py runserver` でサーバーを起動します。

```bash
$ python manage.py runserver
```

### 10. site の値を変更する

管理者としてログインしたら、以下のページに移動してください。  
(以下のページでの設定値は、このデモアプリが利用している django-allauth というのパッケージが利用しています)

/admin/sites/site/1/change/

ドメイン名、表示名を example から変更してください。  
(本番環境で利用する予定のドメイン名が良いでしょう)

***

## 見どころ

### 本番環境での利用を想定した記述

本番環境での利用を想定した記述が随所に見られます。  
参考にしてください。

#### config/settings.py

ローカル環境用の settings.py のサンプルとして local.py を用意しています。  
本番環境用の settings.py のサンプルとして production.py を用意しています。

これらに共通する部分については、 base.py にまとめています。

それぞれの環境では、local.py または production.py をコピーして settings.py を配置します。

config/local.py

```python
from .base import *

# 通常の console だと日本語メールのタイトルが文字化けしてしまうので回避
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

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ["127.0.0.1", ]  # debug toolbar
```

#### .gitignore

.gitignore では、 config/settings.py は git での管理対象外としています。

```gitignore
config/settings.py
```

***

### アプリの見どころ

#### ライブラリの読み込み

ローカル環境用のライブラリ読み込みリストとして、 requirements/dev.txt を用意しています。  
本番環境用のライブラリ読み込みリストとして、 requirements/prod.txt を用意しています。

これらに共通する部分については、 base.txt にまとめています。

requirements/dev.txt

```requirements.txt
-r base.txt

django-debug-toolbar==4.0.0
```

***

#### django-allauth を使った実装

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

#### django-imagekit を使った実装

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

#### django-cleanup を使った実装

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

#### django-bootstrap5 を使った実装

django-bootstrap5 を利用しています。

Tempalte で、 bootstrap5 という、 css/js ライブラリを利用しています。  
bootstrap5 は、少量のコードで見栄えの良いサイトを作るのに便利です。

```python
INSTALLED_APPS = [
    # ...
    'django_bootstrap5',
    # ...
]
```

Template に、以下のコードを追加しています。

```html
{% load django_bootstrap5 %}
{% bootstrap_css %}
{% bootstrap_javascript %}
```

実際には、 bootstrap5 は、 base.html に追加しています。

```html
<!doctype html>
{% load static %}
{% load django_bootstrap5 %}
{% bootstrap_css %}
{% bootstrap_javascript %}

<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- script src="https://kit.fontawesome.com/e795095651.js" crossorigin="anonymous"></script -->
    <script src="{% static 'fontawesome-free-6.4.0-web/js/all.js' %}"></script>
    {% block extra_js %}{% endblock %}
    <link rel="stylesheet" type="text/css" href="{% static 'css/style.css' %}">
    {% block extra_css %}{% endblock %}
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
<main class="container">
    {% block breadcrumb %}{% endblock %}
    {% bootstrap_messages %}
    <h1 class="h1_header">{% block header_h1 %}{% endblock %}</h1>
    <div class="justify-content-center">
        {% block main_content %}{% endblock %}
    </div>
</main>
{% block extra_footer_js %}{% endblock %}
</body>
</html>
```

base.html で読み込まれているタグ 3 つのうち以下の 2 つは、 css/js の読み込みリンクを生成するためのものです。  
なので、サイト全体で有効です。

```html
{% bootstrap_css %}
{% bootstrap_javascript %}
```

ただし、 base.html を extend している Template でも、 django-bootstrap5 を都度読み込む必要があります。

```html
{% extends "base.html" %}
{% load django_bootstrap5 %}
```

***

## Django の UnitTest クラスについて

Django の UnitTest クラスは、 Python 標準の UnitTest クラスを継承したものです。

テストは、以下のコマンドで実行できます。

```bash
$ python manage.py test
```

## 実行されるテスト

実行されるテストは、以下の条件を満たすものです。

- モジュールの置き場所は、以下のいずれかを満たす
    - トップディレクトリ直下にある
    - python package である (`__init__.py` が必要)
- モジュール名が test_ で始まる
- django.test.TestCase クラスを継承したインスタンスである
- メソッド名が test_ で始まる

以上を踏まえて、 UnitTest は、以下の条件を満たすようにしましょう。  
(可読性のための命名規則を含む)

| 要件 | 命名規則                          | 所見                         |
| --- |-------------------------------|----------------------------|
| モジュールの配置場所 | `tests`で始まる名前のパッケージ内に置く | トップディレクトリ直下は管理上好ましくないので避ける |
| モジュール名 | `test_`で始まる名前にする              | 必須                         |
| クラス名 | `Test`で始まる名前にする               | 可読性のために推奨                  |
| テストメソッド名 | `test_`で始まる名前にする              | 必須                         |

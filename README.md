# photo_diary

写真日記アプリです。  
特別なことはしていません。

Ubuntu 22.04 LTS 環境へのデプロイの解説資料となるよう、以下を意図して作りました。

- django-environ を使う
- `python manage.py collectstatic` コマンドを実行する意味がある
- 開発環境と本番環境で settings.py の内容が異なる

## 使い方

開発環境用のライブラリは requirements/dev.txt に記載しています。

本番環境用のライブラリは requirements/prod.txt に記載しています。
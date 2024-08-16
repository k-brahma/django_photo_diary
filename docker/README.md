# Docker でのこのサイトの起動からSSL設定まで

## 前提

### 要求するスキルレベル等

- `vim` 等でのファイル編集を自力でできる
- `sudo` 権限を有するユーザで作業する
- サーバに `docker`, `docker-compse` がインストールされている (方法は省略)

### .env で編集するキーとその意図

| キー | 意図 |
| ---- | ---- |
| `ALLOWED_HOSTS` | `DEBUG=False` のときはサーバのIP/ドメイン名を記入する必要があります。(でないと400エラー) | 
| `NGINX_HTTPS_ENABLED` | `HTTPS` でサービス運用する段階で `true` にします。サーバ証明書取得までは `false` のままで。 | 
| `NGINX_ENABLE_CERTBOT_CHALLENGE` | サーバ署名書初回発行時は `true` にします。あとは `false` のままで。 |
| `CERTBOT_EMAIL` |  | サーバ署名書初回発行時にメールアドレスが必要です。 |
| `CERTBOT_DOMAIN` | `ALLOWED_HOSTS` で指定したのと同じドメイン名にしてください。 |

### 事例

以下の手順書では、 `webapp` という名前のユーザが `/home/webapp/mysite/` にアプリをインストールしたという前提で話を進めます。  
(以下の場合という前提です)

| 値 | 具体例 |
| ---- | ---- |
| アプリインストール先 | `/home/webapp/mysite` | 
| `docker` ディレクトリ | `/home/webapp/mysite/docker/` | 
| IPアドレス | `157.245.147.103` | 
| ドメイン名 | `d4.pc5bai.com` | 
| メールアドレス | `foo@bar.com` | 

## 全体の流れ

1. アプリの導入
2. IP, ドメイン名での接続確認(HTTP)
3. サーバ署名書を取得
4. HTTPSでの接続確認
5. サーバ証明書を更新
6. サーバ証明書定期更新の設定

### 1. アプリの導入

```shell
mkdir mysite
cd mysite
git clone https://github.com/k-brahma/django_photo_diary.git

# docker ディレクトリへ移動
cd docker
```


### 2. IP, ドメイン名での接続確認(HTTP)

IPアドレス, ドメイン(HTTP)での接続を確認します。

```shell
cp .env_sample .env
vim .env
```

ALLOWED_HOST 内の IP アドレスをサーバのものに変更してください。  
また、 domain 名も変更してください。

```
# ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_HOSTS=d4.pc5bai.com,157.245.147.103
```

.env を保存したら、以下を実行。

```
sudo docker-compose up -d
```

しばらく待って、様子が落ち着いてきたら、ブラウザで以下の2つについて動作確認。サイトが表示できればOK。

```
http://157.245.147.103/
http://d4.pc5bai.com/
```

動作確認したら docker を終了。

```
sudo docker-compose down
```

### 3. サーバ署名書を取得

certbot コンテナを起動してサーバ証明書を取得する。

```shell
vim .env
```

以下は例。  
`NGINX_ENABLE_CERTBOT_CHALLENGE=true` にする。また、メールアドレス、ドメインを指定する。

```env
NGINX_HTTPS_ENABLED=false
NGINX_ENABLE_CERTBOT_CHALLENGE=true
CERTBOT_EMAIL=foo@bar.com
CERTBOT_DOMAIN=d4.pc5bai.com
```

再び `docker-compose` コマンドを実行。  
今回は、 certbot のコンテナも含めて起動。

```
# もしまだ終了してない場合は以下(終了していた場合に以下を実行しても問題ない)
sudo docker-compose down

# nginx コンテナを作り直す必要があるので --force-recreate
sudo docker-compose --profile certbot up --force-recreate -d
```

念のため、ブラウザで以下のそれぞれに接続できることを確認する。  
(キャッシュに騙されないように。別ブラウザを使う、シークレットモードでテストする等)

```
http://157.245.147.103/
http://d4.pc5bai.com/
```

上記動作確認が済んだら、以下を実行する。

```shell
sudo docker-compose exec -it certbot /bin/sh /update-cert.sh
```

おそらくうまくいくでしょう。

以下のディレクトリに証明書が置かれます。

```shell
ls -al volumes/certbot/conf/live/d4.pc5bai.com/
total 12
drwxr-xr-x 2 root root 4096 Aug 16 13:01 .
drwxr-xr-x 3 root root 4096 Aug 16 13:01 ..
-rw-r--r-- 1 root root  692 Aug 16 13:01 README
lrwxrwxrwx 1 root root   37 Aug 16 13:01 cert.pem -> ../../archive/d4.pc5bai.com/cert1.pem
lrwxrwxrwx 1 root root   38 Aug 16 13:01 chain.pem -> ../../archive/d4.pc5bai.com/chain1.pem
lrwxrwxrwx 1 root root   42 Aug 16 13:01 fullchain.pem -> ../../archive/d4.pc5bai.com/fullchain1.pem
lrwxrwxrwx 1 root root   40 Aug 16 13:01 privkey.pem -> ../../archive/d4.pc5bai.com/privkey1.pem
```

失敗した場合は以下で nginx の設定を覗けますので、状態を確認してみてください。

```shell
sudo docker-compose exec -it nginx /bin/cat /etc/nginx/conf.d/default.conf
```

証明書発行できたぽいようであれば docker を終了。

```
sudo docker-compose down
```

### 4. HTTPSでの接続確認

HTTPS での接続を確認してみます。

```shell
vim .env
```

以下は例。  
`NGINX_HTTPS_ENABLED=true` にする

```env
NGINX_HTTPS_ENABLED=true
NGINX_ENABLE_CERTBOT_CHALLENGE=false
CERTBOT_EMAIL=foo@bar.com
CERTBOT_DOMAIN=d4.pc5bai.com
```

今回もまた、 certbot のコンテナも含めて起動。

```
# もしまだ終了してない場合は以下(終了していた場合に以下を実行しても問題ない)
sudo docker-compose down

# nginx コンテナを作り直す必要があるので --force-recreate
sudo docker-compose --profile certbot up --force-recreate -d
```

HTTPS で接続してみる。

```shell
https://d4.pc5bai.com/
```

おめでとう！ v(^^*

### 5. サーバ証明書を更新

サーバ証明書の更新方法は以下のとおり。(docker コンテナが健全に起動しているという前提。 docker コンテナの様子は `sudo docker ps` で確認できる)

```shell
# 以下のコマンドは、サーバ証明書取得だけでなく更新でも使える
sudo docker-compose exec -it certbot /bin/sh /update-cert.sh

# nginx に証明書を再読み込みさせる
sudo docker-compose exec -T nginx nginx -s reload
```

ただし、サーバ証明書更新を頻繁に試みると letsencrypt 側から一定期間接続を拒絶されるので要注意。


### 6. サーバ証明書定期更新の設定

letsencrypt で取得できるサーバ署名書の有効期限は90日。  
毎月1回更新を試みれば、まあ十分かと。

こういう定期作業には `cron` を使う。

```shell
sudo crontab -e
```

ここでもしも以下のような表示が出たならば迷わず `1` を選択。

```shell
no crontab for root - using an empty one

Select an editor.  To change later, run 'select-editor'.
  1. /bin/nano        <---- easiest
  2. /usr/bin/vim.basic
  3. /usr/bin/vim.tiny
  4. /bin/ed
```

最後尾に以下を追記する。  
すると、毎月1日の午前0時にSSL証明書の更新が実行され、`nginx` が再読み込みされる。

(以下の `/webapp/mysite/` のところは各自の環境にあわせて必要に応じて書き換える)

```cron
0 0 1 * * cd /home/webapp/mysite/docker/ && /usr/bin/docker-compose exec -T certbot /bin/sh /update-cert.sh && /usr/bin/docker-compose exec -T nginx nginx -s reload
```

最初の何ヶ月かくらいは、サーバ証明書が更新されていることを月初に確認すると良い。  
ブラウザからアクセスしても普通に確認できる。

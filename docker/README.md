# Docker でのこのサイトの起動からSSL設定まで

# 前提

## 要求するスキルレベル等

- `vim` 等でのファイル編集を自力でできる
- `sudo` 権限を有するユーザで作業する
- サーバに `docker`, `docker-compse` がインストールされている (方法は省略)

## .env で編集するキーとその意図

| キー                             | 意図                                                                                        |
| -------------------------------- | ------------------------------------------------------------------------------------------- |
| `ALLOWED_HOSTS`                  | `DEBUG=False` のときはサーバのIP/ドメイン名を記入する必要がある。(でないと400エラー)        |
| `NGINX_HTTPS_ENABLED`            | `HTTPS` でサービス運用する段階で `true` にします。サーバ証明書取得までは `false` のままで。 |
| `NGINX_ENABLE_CERTBOT_CHALLENGE` | サーバ署名書初回発行時は `true` にします。あとは `false` のままで。                         |
| `CERTBOT_EMAIL`                  | サーバ署名書初回発行時にメールアドレスが必要。                                              |
| `CERTBOT_DOMAIN`                 | `ALLOWED_HOSTS` で指定したのと同じドメイン名にすること。                                    |

## 事例

以下の手順書では、 `webapp` という名前のユーザが `/home/webapp/mysite/` にアプリをインストールしたという前提で話を進める。  

| 値                    | 具体例                        |
| --------------------- | ----------------------------- |
| アプリインストール先  | `/home/webapp/mysite`         |
| `docker` ディレクトリ | `/home/webapp/mysite/docker/` |
| IPアドレス            | `157.245.147.103`             |
| ドメイン名            | `ogawa-photo.com`             |
| メールアドレス        | `foo@bar.com`                 |

# 全体の流れ

1. アプリの導入
2. IP, ドメイン名での接続確認(HTTP)
3. サーバ署名書を取得
4. HTTPSでの接続確認
5. サーバ証明書を更新
6. サーバ証明書定期更新の設定

## 1. アプリの導入

```shell
mkdir mysite
cd mysite
git clone https://github.com/k-brahma/django_photo_diary.git .

# docker ディレクトリへ移動
cd docker
```


## 2. IP, ドメイン名での接続確認(HTTP)

IPアドレス, ドメイン(HTTP)での接続を確認する。  

1. 環境変数の `ALLOWED_HOSTS` を書き換える
2. `docker-compose up -d` で起動する
3. 動作確認
4. 終了

### 2-1. 環境変数の `ALLOWED_HOSTS` を書き換える

```shell
cp .env_sample .env
vim .env
```

ALLOWED_HOST 内の IP アドレスをサーバのものに変更する。  
また、 domain 名も変更する。
両者の値はカンマで区切る。

```env
# ALLOWED_HOSTS=localhost,127.0.0.1
ALLOWED_HOSTS=ogawa-photo.com,157.245.147.103
```

### 2-2. `docker-compose up -d` で起動する

.env を保存したら、以下を実行する。

```shell
sudo docker-compose up -d
```

初回は時間がかかるが、これは仕方がない。  

### 2-3. 動作確認

しばらく待って、様子が落ち着いてきたら、ブラウザで以下の2つについて動作確認。サイトが表示できればOK。

```
http://157.245.147.103/
http://ogawa-photo.com/
```

よくある問題:

| エラー             | 解決方法                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| 400エラーが出たら: | ALLOWED_HOSTS の設定を確認すること。                                                                                |
| 502エラーが出たら: | 「ngixの準備はできたが、裏で web app の準備ができていない」という状況はないかと。もう少し待ってから再度試してみる。 |

うまくいかなかった場合は、まずは docker のログを確認してみるのもよい。  

```shell
sudo docker-compose logs -f
```
(ログの出力を終了するには Ctrl+C を押す)

### 2-4. 終了

動作確認したら以下のコマンドで docker を終了。

```shell
sudo docker-compose down
```

## 3. サーバ署名書を取得

サーバ証明書を取得する。

1. 環境変数を編集する
2. `certbot` コンテナを含めて docker containers を起動する
3. 動作確認
4. サーバ証明書を更新
5. 終了

### 3-1. 環境変数を編集する

certbot コンテナを起動してサーバ証明書を取得する。

```shell
vim .env
```

`NGINX_ENABLE_CERTBOT_CHALLENGE` を `true` にする。  
`CERTBOT_EMAIL` を利用可能なメールアドレスにする。  
`CERTBOT_DOMAIN` をこのサーバに割り当てたドメイン名にする。

以下は例。  

```env
NGINX_HTTPS_ENABLED=false
NGINX_ENABLE_CERTBOT_CHALLENGE=true
CERTBOT_EMAIL=foo@bar.com
CERTBOT_DOMAIN=ogawa-photo.com
```

### 3-2. `certbot` コンテナを含めて docker containers を起動する

再び `docker-compose` コマンドを実行。  
今回は、 certbot のコンテナも含めて起動。

```shell
# もしまだ終了してない場合は以下(終了していた場合に以下を実行しても問題ない)
sudo docker-compose down

# nginx コンテナを作り直す必要があるので --force-recreate
sudo docker-compose --profile certbot up --force-recreate -d
```

### 3-3. 動作確認

念のため、ブラウザで以下のそれぞれに接続できることを確認する。  
(キャッシュに騙されないように、先の検証時とは別ブラウザを使う。あるいは、シークレットモードでテストする等)

```
http://157.245.147.103/
http://ogawa-photo.com/
```

問題があった場合の対処についてはすでに書いたとおり。

### 3-4. サーバ証明書を更新

上記動作確認が済んだら、以下を実行する。

```shell
sudo docker-compose exec -it certbot /bin/sh /update-cert.sh
```

おそらくうまくいくであろう。  
以下は、証明書取得に成功した場合の出力の例:

```shell
Certificate does not exist. Obtaining a new certificate...
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Account registered.
Requesting a certificate for df.pc5bai.com

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/df.pc5bai.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/df.pc5bai.com/privkey.pem
This certificate expires on 2024-11-15.
These files will be updated when the certificate renews.

NEXT STEPS:
- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Certificate operation successful
Please ensure to reload Nginx to apply any certificate changes.
```

成功した場合、以下のディレクトリに証明書が置かれる。

```shell
ls -al volumes/certbot/conf/live/ogawa-photo.com/
total 12
drwxr-xr-x 2 root root 4096 Aug 16 13:01 .
drwxr-xr-x 3 root root 4096 Aug 16 13:01 ..
-rw-r--r-- 1 root root  692 Aug 16 13:01 README
lrwxrwxrwx 1 root root   37 Aug 16 13:01 cert.pem -> ../../archive/ogawa-photo.com/cert1.pem
lrwxrwxrwx 1 root root   38 Aug 16 13:01 chain.pem -> ../../archive/ogawa-photo.com/chain1.pem
lrwxrwxrwx 1 root root   42 Aug 16 13:01 fullchain.pem -> ../../archive/ogawa-photo.com/fullchain1.pem
lrwxrwxrwx 1 root root   40 Aug 16 13:01 privkey.pem -> ../../archive/ogawa-photo.com/privkey1.pem
```

失敗した場合は、以下の順序で確認をしたい。

1. `nginx` 内で `.conf` がどうなっているかを確認する
2. `certbot` のログを確認する

#### 失敗した場合の確認事項 1. `nginx` 内で `.conf` がどうなっているかを確認する

`nginx` 内で `.conf` がどうなっているかを確認する。

```shell
sudo docker-compose exec -it nginx /bin/cat /etc/nginx/conf.d/default.conf
```

以下は出力例。  
環境変数 `NGINX_ENABLE_CERTBOT_CHALLENGE` の値を `true` にしてから `docker-compose --profile certbot up --force-recreate -d` したのであれば、以下の記述があるはず。  
`location /.well-known/acme-challenge/ { root /var/www/html; }`

```nginx.conf
WARN[0000] /home/webapp/mysite/docker/docker-compose.yaml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
# Please do not directly edit this file. Instead, modify the .env variables related to NGINX configuration.

server {
    listen 80;
    server_name _;


    location /static/ {
        alias /var/html/www/static/;
    }

    location /media/ {
        alias /app/mediafiles/;
    }

    location / {
      proxy_pass http://web:8000;
      include proxy.conf;
    }

    # placeholder for acme challenge location
    location /.well-known/acme-challenge/ { root /var/www/html; } #これがあるはず！

    # placeholder for https config defined in https.conf.template

}
```

##### 失敗した場合の確認事項 2. `certbot` のログを確認する

 `ls volumes/certbot/logs/` で `certbot` のログを確認する。

```shell
ls volumes/certbot/logs/

# 以下は出力例
# letsencrypt.log  letsencrypt.log.1

# ひきつづき、 letsencrypt.log の中身を調べてみる
cat volumes/certbot/logs/letsencrypt.log
```

### 3-5. 終了

証明書発行できたぽいようであれば docker を終了。

```
sudo docker-compose down
```

## 4. HTTPSでの接続確認

HTTPS での接続を確認する。

1. 環境変数を編集する
2. `certbot` コンテナを含めて docker containers を起動する
3. 動作確認

### 4-1. 環境変数を編集する

環境変数を編集する。

```shell
vim .env
```

`NGINX_HTTPS_ENABLED=true` にする。  
以下は設定例。  

```env
NGINX_HTTPS_ENABLED=true
NGINX_ENABLE_CERTBOT_CHALLENGE=false
CERTBOT_EMAIL=foo@bar.com
CERTBOT_DOMAIN=ogawa-photo.com
```

### 4-2. `certbot` コンテナを含めて docker containers を起動する

今回もまた、 certbot のコンテナも含めて起動。

```
# もしまだ終了してない場合は以下(終了していた場合に以下を実行しても問題ない)
sudo docker-compose down

# nginx コンテナを作り直す必要があるので --force-recreate
sudo docker-compose --profile certbot up --force-recreate -d
```

### 4-3. 動作確認

HTTPS で接続してみる。

```shell
https://ogawa-photo.com/
```

おめでとう！ v(^^*

## 5. サーバ証明書を更新

サーバ証明書の更新方法は以下のとおり。(docker コンテナが健全に起動しているという前提。 docker コンテナの様子は `sudo docker ps` で確認できる)

```shell
# 以下のコマンドは、サーバ証明書取得だけでなく更新でも使える
sudo docker-compose exec -it certbot /bin/sh /update-cert.sh

# nginx に証明書を再読み込みさせる
sudo docker-compose exec -T nginx nginx -s reload
```

ただし、サーバ証明書更新を頻繁に試みると letsencrypt 側から一定期間接続を拒絶されるので要注意。  
(サーバマシン単位なので、別サーバからの証明書更新リクエストは、たとえ同じドメインに対するものであっても問題ない)

短時間でくりかえし試したい場合は、`CERTBOT_OPTIONS` キーの値として `--dry-run` 等を追加する。  
これにより、サーバ証明書の更新はされないが、ログに記録される。この方法はテストに役立つ。

```env
CERTBOT_OPTIONS=--dry-run --debug
```

## 6. サーバ証明書定期更新の設定

letsencrypt で取得できるサーバ署名書の有効期限は90日。  
毎月1回更新を試みれば、まあ十分かと。

こういう定期作業には `cron` を使う。

```shell
sudo crontab -e
```

ここでもしも以下のような表示が出たならば迷わず `1` を選択。  
(`cron`編集画面の初回起動では、おそらく以下の選択を求められる)

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
Google Chrome 等の標準的なブラウザでもサーバ証明書の期限は容易に確認できる。

証明書更新のログについては、記述の「`certbot` のログを確認する」に基づいて行う。

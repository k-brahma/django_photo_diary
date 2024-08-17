# Docker, Docker-Compose のインストール

以下のガイドは、2024年8月17日バージョンです。  
docker, docker-compose がインストールされていないことを前提としています。

## 全体の流れ:

1. パッケージの更新とアップグレード
2. Docker のインストールと動作確認
3. Docker-Compose **のインストールと動作確認**

## 1. パッケージの更新とアップグレード

お約束。

```bash
sudo apt update
sudo apt -y upgrade
sudo apt-get update
```

## 2. Docker のインストール

Ubuntu 24.04 LTS に Docker をインストールする場合、公式 Docker リポジトリを使用することをお勧めします。  
これにより、最新の Docker バージョンを確実に入手できます。

以下の手順に従って Docker をインストールしてください。

1. 必要なパッケージをインストールします。

```bash
sudo apt install ca-certificates curl gnupg
```

2. Docker の公式 GPG キーを追加します。

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

3. Docker リポジトリを APT ソースに追加します。

```bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

4. パッケージリストを更新し、Docker をインストールします。

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

これで、Ubuntu 24.04 LTS に Docker が正しくインストールされます。

5. インストールと動作の確認

インストール後、以下のコマンドを実行して Docker が正常に動作していることを確認してください。

```bash
# バージョン確認
docker --version

# イメージをプルし、コンテナを実行
sudo docker run hello-world
```

このコマンドにより、Docker がイメージをプルし、コンテナを実行できることが確認できます。

## 3. Docker-Compose のインストール

1. 最新バージョンの docker-compose をインストールします。

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

2. インストールを確認

```bash
docker-compose --version
```

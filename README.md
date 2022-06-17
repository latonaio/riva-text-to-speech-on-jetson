# riva-text-to-speech-on-jetson
riva-text-to-speech-on-jetson は、NVIDIA Rivaのテキスト音声合成（TTS）をJetson上で実行する手順概要です。

## 動作環境
- NVIDIA
    - JetPack 4.6.1
    - Riva
- Docker
- Docker Compose v2
- GNU Make
- Python3

## NVIDIA Rivaについて
NVIDIA Rivaは音声AIアプリケーションの構築、ユースケースに合わせたカスタマイズ、リアルタイムパフォーマンスの提供を実現するためのGPU-accelerated SDKです。

## インストール
以下のコマンドでRivaをインストールし、Riva Speech Serverを立ち上げることができます。  
詳細は[Quick Start Guide](https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html)を参照してください。
```
start-riva-server: ## Quick Start Scripts のダウンロード、Riva Speech Server の立ち上げ
        ngc registry resource download-version nvidia/riva/riva_quickstart_arm64:2.1.0
        cd riva_quickstart_arm64_v2.1.0 && bash riva_init.sh && bash riva_start.sh
```
Dockerコンテナが起動するので「Ctrl+P」+「Ctrl+Q」でコンテナから抜けます。


## 動作手順
### Riva Speech Serverの立ち上げ
以下のコマンドでRiva Speech Serverを立ち上げます。  
ただし、すでに立ち上げている場合、この操作は不要です。
```
start-riva-server: ## Riva Speech Serverの立ち上げ（2回目以降）
	bash riva_quickstart_arm64_v2.1.0/riva_start.sh
```

### Docker イメージの作成
以下のコマンドでRiva Speech TTSを動作させるためのDocker イメージを作成します。
```
docker-build: ## docker image の作成
        docker-compose build
```

### Docker コンテナの起動
以下のコマンドでDocker コンテナを起動します。
```
docker-run: ## docker container の立ち上げ
        docker-compose up -d
```

### パラメータ設定
`text-to-speech/config/config.json5`に出力するデバイスのidとjetsonのサーバーのアドレスを設定します。  
`text-to-speech/config/config-sample.json5`に記述し、ファイル名を`config.json5`に書き換えてください。
```
{
    // ID of device
    device_id: xx,

    // Server Address ([IP address]:[Port number])
    // Port number must be a free port on Riva Speech Server
    server_address: '192.xxx.xxx.xxx:50051'
}
```

接続されているデバイスの一覧は以下のコマンドで確認できます。
```
device-list: ## 接続されているdeviceの一覧を表示
	docker exec -it riva-tts python3 text-to-speech/device-list.py
```

### TTSの開始
以下のコマンドでDocker内でTTSを開始します。
```
start-tts: ## ttsの開始
	docker exec -it riva-tts python3 text-to-speech/tts-realtime.py
```
テキストを入力すると合成された音声が再生されます。
ただし、テキストは英語である必要があります。  
終了するときは「Ctrl+C」を押してください。

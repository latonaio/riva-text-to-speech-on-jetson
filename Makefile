# Self-Documented Makefile
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

initialize-riva-server: ## Quick Start Scripts のダウンロード、Riva Speech Server の立ち上げ
	ngc registry resource download-version nvidia/riva/riva_quickstart_arm64:2.1.0
	cd riva_quickstart_arm64_v2.1.0 && bash riva_init.sh && bash riva_start.sh

start-riva-server: ## Riva Speech Serverの立ち上げ（2回目以降）
	bash riva_quickstart_arm64_v2.1.0/riva_start.sh

docker-build: ## docker image の作成
	docker-compose build

docker-run: ## docker container の立ち上げ
	docker-compose up -d

docker-login: ## docker container にログイン
	docker exec -it riva-tts bash

device-list: ## 接続されているdeviceの一覧を表示
	docker exec -it riva-tts python3 text-to-speech/device-list.py

start-tts: ## ttsの開始
	docker exec -it riva-tts python3 text-to-speech/tts-realtime.py

## 概要
LINEで顔写真を送ると感情分析結果を返してくれます。

## ライブラリを追加したときに反映させる
```
pip3 install -r src/requirements.txt
```

## ビルドとデプロイ
```
sam build -t template.json
sam deploy
```
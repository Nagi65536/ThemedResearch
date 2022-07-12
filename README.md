# ThemedResearch
課題研究用のレポジトリだよ

## ドキュメント
[研究内容の説明](/document/explanation.md)  
[プログラムの説明](/document/program_desc.md)  
[調査結果の記録](/document/record.md)  
[重要単語の説明](/document/words_desc.md)  
[参考文献](/document/references.md)  

## スタートアップ
```bash
git clone https://github.com/SatooRu65536/ThemedResearch
cd ThemedResearch
mkdir db

python3 setting.py
(python setting.py)
```

## 試す
```bash
[ターミナル 1]
python3 control.py
```
```bash
[ターミナル 2,3...]
python3 tmp_client.py [タグID] [進む方向]
```
[タグID] setting.py 実行後、/db/main.db を見てください
[進む方向] 1:左折, 2:直進, 3:右折
（指定しなかった場合はデフォルトの値がはいります）


> OSError: [Errno 48] Address already in use  

と出る場合は `control.py line:12`, `tmp_client.py line:9` のポート番号を変更してください

## プロトコル
[DB構造の取り決め](/document/protocol/db_protocol.txt)  
[通信内容(json)の取り決め](/document/protocol/json_protocol.txt)  

## 主なプログラム
### [control.py](/control.py)
* 各交差点における全自動車を制御する

### [tmp_client.py](/tmp_client.py)
* 各車から通信を行う仮のプログラム
* 実際はesp32よりArduino言語で実行する

### [settgng.py](/setting.py)
* DB(テーブル)を生成する
* 仮のデータを追加する

## メモ
[socket通信メモ](/memo/socket)
* socket通信のメモプログラム

[テキストメモ](/memo/text)
* 話し合った内容等のテキストメモ

[その他メモ](/memo/misc)
* その他色々な雑プログラムメモ

## ライセンス
[MIT ライセンス](/LICENSE)


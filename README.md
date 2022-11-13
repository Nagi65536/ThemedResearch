# ThemedResearch
課題研究用のレポジトリだよ

## ドキュメント
- [研究内容の説明](/document/explanation.md)  
- [プログラムの説明](/document/program_desc.md)  
- [調査結果の記録](/document/record.md)  
- [重要単語の説明](/document/words_desc.md)  
- [参考文献](/document/references.md)  


## プロトコル
[DB構造の取り決め](/document/protocol/db_protocol.txt)


## 主なプログラム

###  シミュレーター ver1.0
#### [control.py](/control.py)
* 各交差点における全自動車を制御する

#### [tmp_client.py](/tmp_client.py)
* 各車から通信を行う仮のプログラム
* 実際はesp32よりArduino言語で実行する

#### [settgng.py](/setting.py)
* DB(テーブル)を生成する
* 仮のデータを追加する


### シュミレーター ver2.0(simulator-1/)
* ver1.0 の改善版
* 一つの交差点内での効率化
* 引数に「tl」をつけると信号機制御になる

#### [main.py](/simulator-1/main.py)
* 一括実行するプログラム

#### [config.py](/simulator-1/config.py)
* シミュレーターの設定とプログラムの共通の変数などを保持するファイル

#### [setting.py](/simulator-1/setting.py)
* DB(テーブル)を生成する


### シュミレーター ver3.0(simulator-1/)
* ver2.0 の改良版
* マップ全体での効率化
* 引数に「tl」をつけると信号機制御になる

#### [main.py](/simulator-2/main.py)
* 一括実行するプログラム

#### [config.py](/simulator-2/config.py)
* シミュレーターの設定とプログラムの共通の変数などを保持するファイル

#### [setting.py](/simulator-2/setting.py)
* DB(テーブル)を生成する
* 仮のデータを追加する


## ライセンス
[MIT ライセンス](/LICENSE)


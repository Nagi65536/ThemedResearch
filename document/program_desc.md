# プログラム説明

## 目次
* [contrl.py](#controlpy)  
* [tmp_client.py](#tmp_clientpy)  
* [setting.py](#settingpy)  

## 注目ポイント
* [control.py - add_db_control()](#adddbcontrol-関数)  
* [control.py - control()](#control-関数)  

<br>

## コーディング規約
* Python 3.8 以上を使用する。
* match-case文は使用しない。
* 基本的に **PEP8** に従う。
* 変数名・関数名はわかりやすさを第一とし、ある程度の長さは許容する。
* 型アノテーションを表記する。
* 文字列フォーマットは `f文字列` を使用する。
* `"` と `'` に関しては定めない。
* 分かりやすさを大切にする。

## Python のバージョンによる影響
**Python 3.6**
* 型アノテーション追加
* f文字列の追加
* `global` と `nonlocal` の厳格化
* jsonモジュールがバイナリを入力として受け取れるようになる

**Python 3.8**
* f文字列の拡張
* 標準のコレクション型による型付けが可能に
* 共用体型オペレータの追加

<br>

## 目標
* 交差点において、自動運転車を効率よく走行させる


## **control.py**
* 交差点の一元管理

### **main()** 関数
* メイン関数です

[説明]　　
**control()** 関数と **socket()** 関数の並列処理を開始する

<br>

### **control()** 関数
* 各交差点の車の制御をする

[説明]
車が接続されている交差点を集合型に入れて **check_can_entry()** 関数 を回す

<br>

### **check_can_entry()** 関数
* 指定された交差点において各車が進入できるか判断する

[引数]  
**cross_name** : 確認する交差点を指定  

[詳細設定]  
北:0, 東:1, 南:2, 西:3 とする  
左折:1, 直進:2, 右折:3 とする

[説明]  
進入済時間順にデータを取得し、進入可能な車IDを **can_entry_list** に追加する

[判断手順]  
**共通**
* 同じレーンで既に待機して*ない*
* 同じ方向へ進む車が*ない*

**Uターン**
* (未実装)

**左折**
* (なし)

**直進**
* 左方向から来る車が*ない*
* 左方向へ進む車が*ない*

**右折**
* 左方向から左折は*おけ*
* 前方向から右折は*おけ*
* 右方向からの左折は*おけ*

<br>

### **communication()** 関数
* 各車と通信をする
* サーバーと通信中の車の数だけ並列で実行される

[手順] socket通信接続後
1. 接続報告を受信
2. **add_db_control()** 関数 を呼び、データ登録
3. 停止指示を送信
4. **check_can_entry()** 関数によって **can_entry_list** に車IDが追加されるまで待機
5. 進入指示
6. 通過済報告を受信
7. socket通信切断

<br>

### **add_db_control()** 関数
* 各車の接続交差点名, 来し方, 行き先を登録する

[引数]  
data : 
```Python
{
    car_id : 'CAR_ID',  # 車ID
    status : 'connect',  # 車の状態
    tag_id : 'TAG_ID',  # 接続したタグID
    destination : 'TURN_DIRECTION'  # 行き先
}
```

[詳細設定]  
* 北:0, 東:1, 南:2, 西:3 とする
* 左折:1, 直進:2, 右折:3 とする

```Python
car_idstr = data['car_id']    # 車ID
tag_idstr = data['tag_id']    # 接続地点タグID
destinationint = data['destination']  # 行き先
time_float = time.time()  # 時間（秒）
```
**destination** は車から見た相対位置である（右折, 直進, 左折...）  
**tag_id** より **origin**（来し方）などを割り出す  

```Python
# DBよりデータ取得
cur.execute(f'SELECT cross_name, direction FROM cross_tag_info WHERE tag_id = "{tag_id}"')
get_db_datadict: tuple = cur.fetchone()
cross_name: str = get_db_data[0]    # 交差点名取得
origin: int = get_db_data[1]    # 来し方取得
```
**origin** は絶対位置である（北, 東, 南, 西）  
**dest_direction**（行き先）の絶対位置を割出す
```Python
dest_directionint = origin + destination
```
**est_direction** は絶対位置である（北, 東, 南, 西）  
データをDBに登録する
```Python
cur.execute(f'''
    REPLACE INTO control VALUES (
    "{car_id}", "{cross_name}", "{tag_id}", "{origin}", "{destination}", "{status}", {time_}
)''')
```

<br>

### **remove_db_control()** 関数
* socket通信切断後、DBから保存データを削除する

<br>

### **get_decode_data()** 関数
* 受信したbytes型をjsonにした後、辞書型にする

<br>

### **get_encode_to_send()** 関数
* 指示を辞書型->jsonにした後、bytes型にする

<br>

## **tmp_client.py**
* 仮のクライアント（車側）としてデータの送受信をする

### **main()** 関数
* メイン関数です
* control関数とsocket通信関数を並列処理する

### **communication()** 関数

### **get_decode_data()** 関数
* 受信したbytes型をjsonにした後、辞書型にする

<br>

### **get_encode_to_send()** 関数
* 指示を辞書型->jsonにした後、bytes型にする

<br>

## **setting.py**
* データベースに仮のデータを設定する

### **create_table()** 関数
* テーブルを作成する

### **register()** 関数
* 仮のデータを登録する

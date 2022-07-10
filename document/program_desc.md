# プログラム説明

## 目次
[contrl.py](#controlpy)  
[tmp_client.py](#tmp_clientpy)  
[setting.py](#settingpy)  

## 注目ポイント
[control.py add_db_control()](#adddbcontrol-関数)  
[control.py control()](#control-関数)  

## 目標
* 交差点において、自動運転車を効率よく走行させる


## **control.py**
* 交差点の一元管理

### **main()** 関数
* メイン関数です
* control関数とsocket通信関数を並列処理する

<br>

### **control()** 関数
* 各交差点の車の制御をする

[詳細設定]  
* 北:0, 東:1, 南:2, 西:3 とする
* 左折:1, 直進:2, 右折:3 とする

時間順にデータを取得し、進入可能な車IDを **can_entry_list** に追加する
TODO後ほど

<br>

### **communication()** 関数
* 各車と通信をする
* 並列処理によって車一台に対し、一つ実行される

[手順] socket通信接続後
1. 接続報告を受信
2. **add_db_control()** 関数 を呼び、接続データ保存
3. 直接進入できない場合、停止指示を送信
4. **control()** 関数によって **can_entry_list** に車IDが追加されるまで待機
5. 進入指示
6. 通過済報告を受信
7. socket通信切断

<br>

### **add_db_control()** 関数
* 来し方, 行き先を絶対位置（方角）で保存します

[詳細設定]  
* 北:0, 東:1, 南:2, 西:3 とする
* 左折:1, 直進:2, 右折:3 とする

引数として車からの **tag_id**や **destination**（行き先）などをもらう  
```python
car_idstr = data['car_id']    # 車ID
tag_idstr = data['tag_id']    # 接続地点タグID
destinationint = data['destination']  # 行き先
time_float = time.time()  # 時間（秒）
```

**destination** は車から見た相対位置である（右, 直進, 左...）  
**tag_id** より **origin**（来し方）などを割り出す  
```python
# DBよりデータ取得
cur.execute(f'SELECT cross_name, direction FROM tag_info WHERE tag_id = "{tag_id}"')
get_db_datadict: tuple = cur.fetchone()
cross_name: str = get_db_data[0]    # 交差点名取得
origin: int = get_db_data[1]    # 来し方取得
```
**origin** は絶対位置である（北, 東, 南, 西）  
**dest_direction**（行き先）の絶対位置を割出す
```python
dest_directionint = origin + destination
```
**est_direction** は絶対位置である（北, 東, 南, 西）  
データをDBに登録する
```python
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

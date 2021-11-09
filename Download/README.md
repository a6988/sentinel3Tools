# AWSからSentinel-3データのダウンロード


# 使い方
---
## STEP1 : 諸々準備(場合によっては1-1, 1-3はいらないかも．．)
### STEP1-1 : AWSのアカウント登録([参考](#https://docs.aws.amazon.com/ja_jp/redshift/latest/dg/tutorial-loading-data-launch-cluster.html))
参考より，アカウント登録ページに飛ぶことができます．  
基本的に無料で利用できる．ただし，クレジットカードを登録する必要あり

---
### STEP1-2 : AWS CLIのダウンロード([参考](https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/install-cliv2.html))
1. 参考ページよりマシンにあったインストール手順を選択し，その説明に従う
2. awsコマンドが使えるようになったらSTEP2に進む

---
### STEP1-3 : AWS CLIの初期設定
1. STEP1-1で作成したアカウントのマイアカウントページを開く
2. 右上のユーザー名のタブ⇒マイセキュリティ資格情報
3. 見開きのアクセスキータブを展開⇒新しいアクセスキーの取得(csvで出力されるアクセスキーは保存しておく)
4. terminalを開いて以下のように打つ
   ```
   aws configure
   すると，ユーザーネーム，パスワード，場所[，出力フォーマット]の順番で求められるので打ち込む
   username
   pass word
   region [Sentinel-3はeu=central-1]
   output format (任意：Noneのままでいい)
   ```

---
### STEP2 : ダウンロード
---
#### STEP2-1 : params.shを編集
[カタログ](https://meeo-s3.s3.amazonaws.com/index.html#/?t=catalogs)を見ながら設定してください  
カタログ内ではページの見出しがタイトル(ショートタイトル)となっています。  
それぞれの変数にショートタイトルを定義してください
```
Dtime    : 時間の設定
            NRT : Non-Real Time
            NTC : Non-Time Critical
Sentinel : 衛星バージョン
            S3A : Sentinel 3A 
            S3B : Sentinel 3B 
Var      : データ種別
            例えば．．．"SL_2_LST___" : Land surface temperature
start    : データ取得開始時間
end      : データ取得終了時間
```

---
#### STEP2-2 : Download.shの実行
ターミナル上で以下のように打つと，OUTPUTフォルダが作成されその中にAWSからデータがコピーされる
```
./Download.sh
```

---
#### 補足（簡単なダウンロード.shの説明）
1. params.shから設定を読み込む
2. フォルダパス(AWS_path)を作成し，そのフォルダの一覧(tmp.txt)を取得する
3. EditTmpを使ってフォルダのみを抽出し，tmpフォルダに展開する
4. ダウンロード
5. 2.-5.の操作を日付分繰り返す

もし，特定のフォルダ(場所の定義)を追加したい場合は，EditTmp_source内にあるEditTmp.pyを編集，実行ファイルに変換してください  
L7. (# pick up only folder)のfolder抽出部分にif文等を追加すれば行けると思います.  
編集後以下のように打ち，distフォルダにあるEditTmpをDownload.shと同じフォルダに移動
```
pyinstaller EditTmp.py --onefile
```
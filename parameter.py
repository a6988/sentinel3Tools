'''
Sentinel-3可視化のパラメータファイル
フォルダ構成 : 
    shp : shapeファイルを入れる。
'''

# shpディレクトリ(このpyがあるディレクトリからの相対パス)
shpDir = './shp'
# 結果dir
resDir = './res'
# png格納
pngDir = f'{resDir}/png'
# pickup結果の格納フォルダ
pickupDir = f'{resDir}/pickup'
# データ格納フォルダ
dataDir = './data'

# 対象項目(クロロフィルa:CHLA, 懸濁物質:TSM)
targetItems = ['CHLA']

# 画像作成を行うか
pngExec = True
# 表示させたい緯度経度の範囲
lons = [123.7, 123.9]    # [min, max]
lats = [9.6, 9.8]    # [min, max]    

# ピックアップを行うか
pickupExec = True
# ピックアップファイルの名前(csv)
pickupResFilename = 'timeseries.csv'
# ピックアップしたいポイントの座標
# 投影法の定義
coordinate = 'EPSG:4326'
# ピックアップしたい地域のshpファイル(リスト)
pickupShps = ['./shp/pickArea/compareSat/compareSat.shp',
        './shp/pickArea/pickupSatTentative/pickupSatTentative.shp']

pickupLon = 123.83538
pickupLat = 9.65851

# 表示させるshapeFile(shpディレクトリ以下を指定)
visSHPs = ['/adminAroundTagbilaran/adminAroundTagbilaran.shp']

# 描画時の範囲
vrange = [0,20]



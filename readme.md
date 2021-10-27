# Sentinel-3 OCLI 海色センター 作図ツール

Sentinel-3 OCLIの海色センサープロダクトを読み込み作図するツールです。
現在は以下のプロダクトの読み込みに対応しています。

* CHL_NN

	* クロロフィルa濃度(ニューラルネットワーク処理)

* TSM_NN

	* 懸濁物質濃度(ニューラルネットワーク処理)

## 依存関係

* cartopy
* netCDF4
* numpy
* matplotlib
* pandas
* geopandas
* shapely

## データ

* Sentinel-3のデータをダウンロードし解凍すると、以下のような形式のフォルダが出力されるので、これを指定フォルダに置く

	* `S3B_OL_2_WFR____20190707T012847_20190707T013147_20190708T102150_0179_027_188_2700_MAR_O_NT_002.SEN3`

* 複数のnetCDFファイルから構成されるが、緯度経度情報が入った`geo_coordinates.nc`は必須。
* 可視化対象に応じて、プロダクトDN値が格納されたnetCDFファイルを同ファイルに格納する

|項目名|netCDFファイル名|
|------|----------------|
|CHL_NN|chl_nn.nc|
|TSM_NN|tsm_nn.nc|

## 使い方

* `parameter.py`に必要事項記載する
* `python visSentinel3.py`を実行する

## parameter.pyの記載事項

* `parameter.py`に項目の内容は記載

	* 仕様がもう少し固まればこちらに詳細を記載する

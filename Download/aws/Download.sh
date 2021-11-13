#!/bin/bash

if [ ! -e ./OUTPUT ]; then
	mkdir ./OUTPUT
fi

#read params
source ./params.sh
AWS="s3://meeo-s3/$Dtime/$Sentinel/$Var/"
echo "---------------"
echo AWS = $AWS
echo Start date = $start
echo End date = $end
echo "---------------"


Cdate=$start
Sdate=`date -d ${start} "+%s"`
Edate=`date -d ${end} "+%s"`

# print number of download files
NFILES=$(((Edate-$Sdate)/86400))
echo Download $((NFILES+1)) days
for d in `seq $((NFILES+1))`
do
	if [ -e ./tmp ]; then
		rm -rf ./tmp
	fi
	mkdir ./tmp
	## 日付の取得
	dt=$((d-1))
	yyyy=`date --date "$Cdate $dt days" +%Y`
	mm=`date --date "$Cdate $dt days" +%m`
	dd=`date --date "$Cdate $dt days" +%d`
	echo ["$yyyy/$mm/$dd"]  / [`date -d ${end} +%Y/%m/%d`]
	## その日付のデータを開く
	AWS_path="$AWS$yyyy/$mm/$dd/"
	## フォルダ名をtmp.txtに出力する
	touch ./tmp/tmp.txt
	files=`sudo aws s3 ls $AWS_path --no-sign-request`
	echo $files > ./tmp/tmp.txt
	## tmpの編集
	./EditTmp
	## ダウンロード
	source ./tmp/number.sh
	for i in `seq $((Nfolder))`
	do
		printf "\r$((i))/$((Nfolder)) folders"
		source ./tmp/tmp$i.sh
		AWS_path2="$AWS$yyyy/$mm/$dd/$folder"
		out=`sudo aws s3 cp $AWS_path2 ./OUTPUT/$folder --no-sign-request --recursive`
	done
	echo 
done

rm -rf ./tmp














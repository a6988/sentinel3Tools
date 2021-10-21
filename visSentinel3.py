import numpy as np
import netCDF4 
import matplotlib.pyplot as plt
from cartopy.io import shapereader 
from cartopy.feature import ShapelyFeature
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import glob
from parameter import *
import subprocess
import os

def writeTimeseries():
    '''
    時系列データの書き込みを行う
    '''
    pass

def getLatLonArray(geoCoordNCFile:str, thisLat:list,thisLon:list):
    '''
    指定範囲内の配列を得る
    '''

    # 指定範囲の最小最大からstart, endを算出
    startLat = min(thisLat)
    endLat = max(thisLat)
    startLon = min(thisLon)
    endLon = max(thisLon)

    # netCDF4の読み込み
    with netCDF4.Dataset(geoCoordNCFile,'r') as geoNC:

        # 緯度・経度で範囲にあるかのフラグ配列
        inLatFlag = ( geoNC['latitude'][:] > startLat ) & \
            ( geoNC['latitude'][:] < endLat )

        inLonFlag = ( geoNC['longitude'][:] > startLon ) & \
            ( geoNC['longitude'][:] < endLon )

        # 緯度経度として範囲に入っているかどうかの判定
        inAreaFlag = inLatFlag * inLonFlag
        thisRes = np.where(inAreaFlag == True)
        
        # 範囲内にはいっているかどうか緯度経度の結果を格納
        latRes = thisRes[0]
        lonRes = thisRes[1]
        startLat = latRes.min()
        endLat = latRes.max()
        startLon = lonRes.min()
        endLon = lonRes.max()
        

        return {'startLatIndex':startLat, 'endLatIndex':endLat,
                'startLonIndex':startLon, 'endLonIndex':endLon}

def getArrays(geoNC,itemNC,itemLabel,regionIndex):
    '''
    緯度経度が格納されたgeoNCと項目が格納されたitemNCから
    対象になる範囲のindexを取得する
    '''

    startLat = regionIndex['startLatIndex']
    endLat = regionIndex['endLatIndex']
    startLon = regionIndex['startLonIndex']
    endLon = regionIndex['endLonIndex']

    itemArray = itemNC[itemLabel][startLat:endLat,startLon:endLon]
    
    latArray = geoNC['latitude'][startLat:endLat, startLon:endLon]
    lonArray = geoNC['longitude'][startLat:endLat, startLon:endLon]
    return itemArray,latArray,lonArray

def pickupNearestData(pickupLon, pickupLat,
        itemArray,latArray,lonArray):
    '''
    任意の座標に最も近いポイントを取得する
    distArray[i,j]に各地点からの距離を算出する
    '''
    
    distArray = np.zeros([itemArray.shape[0],itemArray.shape[1]])

    for i in range(0,itemArray.shape[0]):
        for j in range(0,itemArray.shape[1]):
            distArray[i,j] = ( latArray[i,j]-pickupLat)**2 + (lonArray[i,j]-pickupLon)**2

    return distArray

def makeTimeseries(thisDataFolder,itemArray,latArray,lonArray,f):
    '''
    時系列のデータを日付とともに入力する
    valueがないときはnp.nan
    valueはlog10の値らしいので取り敢えず変換する
    '''
    
    distArray = pickupNearestData(pickupLon,pickupLat,
            itemArray,latArray,lonArray)
    nearestArrayIndexes = np.where(distArray==distArray.min())

    res = 0
    #for thisNearestArrayIndex in nearestArrayIndexes:
    #    res += itemArray[thisNearestArrayIndex[0],thisNearestArrayIndex[1]]
    #res = res / len(nearestArrayIndexes)
    # 一つ目を使うことにする
    res = itemArray[nearestArrayIndexes[0],nearestArrayIndexes[0]]

    # log10の値ということなので変換、もしおかしなあたいのときは-9999
    try:
        thisValue = 10**res[0]
    except:
        thisValue = -9999

    thisDate = thisDataFolder.split('_')[7]

    f.write(f"{thisDate},{thisValue}\n")
    



class visSentinel():

    def __init__(self):

        self.dataDir = dataDir
        self.pngExec = pngExec
        self.pickupExec = pickupExec
        # 画像出力を行う場合
        if self.pngExec == True:
            self.pngDir = pngDir
            ## フォルダ作成
            if not os.path.isdir(pngDir):
                subprocess.run(['mkdir','-p',pngDir])

        ## 連続値結果を取得する場合
        if self.pickupExec == True:
            self.pickupDir = pickupDir
            # フォルダ作成
            if not os.path.isdir(pickupDir):
                subprocess.run(['mkdir','-p',pickupDir])

            with open(f'{self.pickupDir}/{pickupResFilename}','w') as f:
                f.write('date,value\n')

        # sentinelデータはS3から始まるディレクトリに格納されている
        dataFolders = glob.glob(dataDir +'/S3*')

        for i,thisDataFolder in enumerate(dataFolders):
         
            print(f'{i+1}番目/{len(dataFolders)}中')
            try:
                self.makeFigure(thisDataFolder)
            except Exception as e:
                print(e)

            writeTimeseries()
        
    def makeFigure(self,thisDataFolder):
        '''
        このdataFolderの図を作成する
        '''
        ## 緯度経度のファイル
        geoCoordNCFile = thisDataFolder + '/geo_coordinates.nc'
        geoNC = netCDF4.Dataset(geoCoordNCFile,'r')
        ## 対象項目(クロロフィル)
        chlNCFile = thisDataFolder + '/chl_nn.nc'
        chlNC = netCDF4.Dataset(chlNCFile,'r')
        chlLabel = 'CHL_NN'

        itemNC=chlNC
        itemLabel = chlLabel


        regionIndex = getLatLonArray(geoCoordNCFile,thisLat,thisLon)


        # 緯度・経度・項目の配列を取得
        startLatIndex = regionIndex
        itemArray, latArray, lonArray = getArrays(
                geoNC,itemNC,itemLabel,regionIndex)

        #makeTimeseries(thisDataFolder,itemArray,latArray,lonArray,f)

        fig = plt.figure()

        ax = fig.add_subplot(111,projection=ccrs.PlateCarree())

        cont = ax.contourf(lonArray, latArray, 10**itemArray, 
                levels=range(0,50,10),cmap='jet',
                     transform=ccrs.PlateCarree())
        cbar =fig.colorbar(cont)

        #coast = ax.coastlines(resolution="10m")

        # 行政界の描画
        for thisShp in visSHPs:
            src = shapereader.Reader(shpDir + thisShp)

            shp_ftr = ShapelyFeature(src.geometries(),
                    ccrs.PlateCarree(),
                    edgecolor='brown',
                    facecolor=cfeature.COLORS['land'])

            ax.add_feature(shp_ftr)

        ax.set_xlim(thisLon[0],thisLon[1])
        ax.set_ylim(thisLat[0],thisLat[1])

        
        thisDate = thisDataFolder.split('_')[7]
        plt.savefig(f'{self.pngDir}/{thisDate}.png')


if __name__ == '__main__':

    thisVis = visSentinel()




    





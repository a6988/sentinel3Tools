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
import pandas as pd
import geopandas as gpd
from shapely.ops import cascaded_union




class visSentinel():

    def __init__(self):

        self.dataDir = dataDir
        self.pngExec = pngExec
        self.pickupExec = pickupExec
        self.lons = lons
        self.lats = lats
        self.targetItems = targetItems
        self.coordinate = coordinate 
        # 画像出力を行う場合
        if self.pngExec == True:
            self.visSHPs = visSHPs
            self.pngDir = pngDir
            self.shpDir = shpDir
            self.vrange = vrange
            ## フォルダ作成
            if not os.path.isdir(pngDir):
                subprocess.run(['mkdir','-p',pngDir])

        ## 連続値結果を取得する場合
        if self.pickupExec == True:
            self.pickupDir = pickupDir
            self.pickupLon = pickupLon
            self.pickupLat = pickupLat
            self.pickupShps = pickupShps
            # フォルダ作成
            if not os.path.isdir(pickupDir):
                subprocess.run(['mkdir','-p',pickupDir])

            with open(f'{self.pickupDir}/{pickupResFilename}','w') as f:
                f.write('date,value\n')

        # sentinelデータはS3から始まるディレクトリに格納されている
        dataFolders = glob.glob(dataDir +'/S3*')

        for i,thisDataFolder in enumerate(dataFolders):
         
            self.thisDataFolder = thisDataFolder
            print(f'{i+1}番目/{len(dataFolders)}中')
            #try:
            for thisTargetItem in self.targetItems:
                self.thisTargetItem = thisTargetItem
                self.makeData()
                if self.pngExec == True:
                    self.makeFigure()
                if self.pickupExec == True:
                    self.pickupFromShp()
                    #self.makeTimeseries()
            #except Exception as e:
            #    print(e)
        
    def makeData(self):
        '''
        生データを読み込み作図や時系列データの作成の元を作成する
        '''
        ## 緯度経度のファイル
        geoCoordNCFile = self.thisDataFolder + '/geo_coordinates.nc'
        geoNC = netCDF4.Dataset(geoCoordNCFile,'r')
        ## 対象項目
        if self.thisTargetItem == 'CHLA':
            # クロロフィルはニューラルネットワークのプロダクトを想定
            itemNCFile = self.thisDataFolder + '/chl_nn.nc'
            itemLabel = 'CHL_NN'
        elif self.thisTargetItem == 'TSM':
            # クロロフィルはニューラルネットワークのプロダクトを想定
            itemNCFile = self.thisDataFolder + '/tsm_nn.nc'
            itemLabel = 'TSM_NN'

        itemNC = netCDF4.Dataset(itemNCFile,'r')

        regionIndex = self.getLatLonArray(geoCoordNCFile,lats,lons)

        # 緯度・経度・項目の配列を取得
        startLatIndex = regionIndex
        self.itemArray, self.latArray, self.lonArray = self.getArrays(
                geoNC,itemNC,itemLabel,regionIndex)

        return

    def makeFigure(self):
        '''
        このdataFolderの図を作成する
        '''
        ### COLORBAR TICKS
        self.CbarTicks = np.linspace(self.vrange[0], self.vrange[1], 5)
        fig = plt.figure()

        ax = fig.add_subplot(111,projection=ccrs.PlateCarree())

        # log10の値が入っているのであれば、10**self.itemArrayとすべき
        contour = ax.pcolormesh(
                self.lonArray, self.latArray, self.itemArray*10, 
                edgecolor="none", cmap="rainbow", 
                vmin=self.vrange[0], vmax=self.vrange[1], 
                shading="auto", zorder=1)
        
        bar     = fig.colorbar(contour, ax=ax, 
                ticks=self.CbarTicks)

        #cont = ax.contourf(self.lonArray, self.latArray, 10**self.itemArray, 
        #        levels=range(0,50,10),cmap='jet',
        #             transform=ccrs.PlateCarree())
        #cbar =fig.colorbar(cont)

        #coast = ax.coastlines(resolution="10m")

        # 行政界の描画
        for thisShp in self.visSHPs:
            src = shapereader.Reader(self.shpDir + thisShp)

            shp_ftr = ShapelyFeature(src.geometries(),
                    ccrs.PlateCarree(),
                    edgecolor='brown',
                    facecolor=cfeature.COLORS['land'])

            ax.add_feature(shp_ftr)

        ax.set_xlim(lons[0],lons[1])
        ax.set_ylim(lats[0],lats[1])

        
        thisDate = self.thisDataFolder.split('_')[7]
        plt.savefig(f'{self.pngDir}/{self.thisTargetItem}_{thisDate}.png')

    def makeTimeseries(self):
        '''
        時系列のデータを日付とともに入力する
        valueがないときはnp.nan
        valueはlog10の値らしいので取り敢えず変換する
        '''
        
        distArray = self.pickupNearestData(self.pickupLon,self.pickupLat,
                self.itemArray,self.latArray,self.lonArray)
        nearestArrayIndexes = np.where(distArray==distArray.min())

        res = 0
        res = self.itemArray[nearestArrayIndexes[0],nearestArrayIndexes[0]]

        # log10の値ということなので変換、もしおかしなあたいのときは-9999
        try:
            thisValue = 10**res[0]
        except:
            thisValue = -9999

        thisDate = self.thisDataFolder.split('_')[7]

        with open(f'{self.pickupDir}/{pickupResFilename}','a') as f:
            f.write(f"{thisDate},{thisValue}\n")

        return

    def pickupFromShp(self):
        '''
        shapeファイルと一致する地点からデータを出力する
        '''
        ### PREPARE DATA
        # 縦ベクトル化
        LAT   = np.reshape(self.latArray,  
                ((self.latArray.shape[0]  *  self.latArray.shape[1], 1)))
        LON   = np.reshape(self.lonArray,  
                ((self.lonArray.shape[0]  *  self.lonArray.shape[1], 1)))
        DATA  = np.reshape(self.itemArray, 
                ((self.itemArray.shape[0] *  self.itemArray.shape[1], 1)))
        #
        if LAT.shape[0] != LON.shape[0] or LAT.shape[0] != DATA.shape[0]:
            raise valueError('緯度・経度・データの配列の大きさが異なります')
        PDATA = pd.DataFrame(np.zeros((LAT.shape[0], 3)))
        PDATA.columns = [self.thisTargetItem, "LAT", "LON"]
        PDATA.loc[:, self.thisTargetItem] = DATA[:,0]
        PDATA.loc[:, "LAT"] = LAT[:,0]
        PDATA.loc[:, "LON"] = LON[:,0]
        PDATA = PDATA.dropna(how="any", axis=0)
        PDATA = gpd.GeoDataFrame(PDATA, geometry=gpd.points_from_xy(PDATA.LON, PDATA.LAT)).set_crs(self.coordinate)
        ### PICK DATA
        for thisPickupShp in self.pickupShps:
            shp = gpd.read_file(thisPickupShp)
            shp = cascaded_union(shp.geometry)
            res = PDATA[PDATA.geometry.within(shp)]
            # ここにファイルにアペンドしていくようにする必要あり
            res.to_csv(f"{self.pickupDir}/{pickupResFilename}", 
                    index=None)


    def getLatLonArray(self,geoCoordNCFile:str, lats:list,lons:list):
        '''
        指定範囲内の配列を得る
        '''

        # 指定範囲の最小最大からstart, endを算出
        startLat = min(lats)
        endLat = max(lats)
        startLon = min(lons)
        endLon = max(lons)

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

    def getArrays(self,geoNC,itemNC,itemLabel,regionIndex):
        '''
        緯度経度が格納されたgeoNCと項目が格納されたitemNCから
        対象になる範囲のindexを取得する
        '''

        startLat = regionIndex['startLatIndex']
        endLat = regionIndex['endLatIndex']
        startLon = regionIndex['startLonIndex']
        endLon = regionIndex['endLonIndex']

        # Sentinel3のデータは(少なくともCHLAは)log10の値として入っている
        if self.thisTargetItem in ['CHLA','TSM']:
            itemArray = 10 ** (itemNC[itemLabel][startLat:endLat,startLon:endLon])
        
        latArray = geoNC['latitude'][startLat:endLat, startLon:endLon]
        lonArray = geoNC['longitude'][startLat:endLat, startLon:endLon]
        return itemArray,latArray,lonArray

    def pickupNearestData(self,pickupLon, pickupLat,
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
            

if __name__ == '__main__':

    thisVis = visSentinel()




    





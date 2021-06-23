# -*- coding: utf-8 -*-
import threading
import os,time,sys
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime,pyautogui,subprocess
import pandas as pd
from datetime import datetime,timedelta
import numpy as np
import talib as ta
import csv
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import hmac
import talib as ta
import hashlib
import base64
import urllib.parse
import requests as  r
import json
import numpy
import time
import shutil
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
import sys,io
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
import multiprocessing
import okex.Account_api as Account
import okex.Funding_api as Funding
import okex.Market_api as Market
import okex.Public_api as Public
import okex.Trade_api as Trade
import okex.subAccount_api as SubAccount
import okex.status_api as Status
import statsmodels.api as sm
import statsmodels.formula.api as smf



class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


class Datainfo:



    def isbuy(minute):

        
        Datainfo.saveinfo('开始获取是否可以买入ismarket。。。')

        api_key,secret_key,passphrase,flag = Datainfo.get_userinfo()

        #判断订单是否大于5单，大于则不买入
        #trade api
        tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        list_string_buy = ['buy']
        list_string_sell = ['sell']
        list_text = list(pd.DataFrame(eval(str(tradeAPI.get_fills()))['data'])['side'].head(100).values)
        all_words_buy = list(filter(lambda text: all([word in text for word in list_string_buy]), list_text ))
        all_words_sell = list(filter(lambda text: all([word in text for word in list_string_sell]), list_text ))
        Datainfo.saveinfo('总计：--->>>'+str(len(all_words_buy) - len(all_words_sell))+' 单 。。。>>>')
        print('总计：--->>>',len(all_words_buy) - len(all_words_sell),' 单 。。。>>>')
        if(len(all_words_buy) - len(all_words_sell)>30):
            Datainfo.saveinfo('买单大于30单返回。。。>>>')
            
            return '30单'

        if(len(all_words_buy) < len(all_words_sell) - 5):
            Datainfo.saveinfo('买单小于卖单返回。。。>>>')
            return '买单小于卖单'

        t = time.time()

        #print (t)                       #原始时间数据
        #print (int(t))                  #秒级时间戳
        #print (int(round(t * 1000)))    #毫秒级时间戳
        #print (int(round(t * 1000000))) #微秒级时间戳
        tt = str((int(t * 1000)))
        ttt = str(int(round(t * 1000)))

        #=====获取vol数据
        headers = {
            'authority': 'www.okex.com',
            'sec-ch-ua': '^\\^',
            'timeout': '10000',
            'x-cdn': 'https://static.okex.com',
            'devid': '7f1dea77-90cd-4746-a13f-a98bac4a333b',
            'accept-language': 'zh-CN',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'accept': 'application/json',
            'x-utc': '8',
            'app-type': 'web',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.okex.com/markets/swap-data/eth-usd',
            'cookie': '_gcl_au=1.1.1849415495.'+str(tt)+'; _ga=GA1.2.1506507962.'+str(tt)+'; first_ref=https^%^3A^%^2F^%^2Fwww.okex.com^%^2Fcaptcha^%^3Fto^%^3DaHR0cHM6Ly93d3cub2tleC5jb20vbWFya2V0cy9zd2FwLWRhdGEvZXRoLXVzZA^%^3D^%^3D; locale=zh_CN; _gid=GA1.2.802198982.'+str(tt)+'; amp_56bf9d=gqC_GMDGl4q5Tk-BJhT-oP...1f8fiso4n.1f8fiu841.1.2.3',
        }

        params = (
            ('t', str(ttt)),
            ('unitType', '0'),
        )

        response = r.get('https://www.okex.com/v3/futures/pc/market/takerTradeVolume/ETH', headers=headers, params=params)

        if response.cookies.get_dict(): #保持cookie有效 
                s=r.session()
                c = r.cookies.RequestsCookieJar()#定义一个cookie对象
                c.set('cookie-name', 'cookie-value')#增加cookie的值
                s.cookies.update(c)#更新s的cookie
                s.get(url = 'https://www.okex.com/v3/futures/pc/market/takerTradeVolume/ETH?t='+str(ttt)+'&unitType=0')
        df = pd.DataFrame(response.json()['data'])
        df.to_csv(f'./datas/okex/eth.csv',index=False)
        df = pd.read_csv(f'./datas/okex/eth.csv')
        df['timestamps'] = pd.to_datetime(df['timestamps'],unit='ms')+pd.to_timedelta('8 hours')
        buyVolumes = df['buyVolumes'].tail(30).values
        sellVolumes = df['sellVolumes'].tail(30).values

        buyVolumes10 = df['buyVolumes'].tail(10).values
        sellVolumes10 = df['sellVolumes'].tail(10).values

        print(df)
        print(str(datetime.now())+'--->>>计算结果--->>>',(sum(buyVolumes)/len(buyVolumes)) / (sum(sellVolumes)/len(sellVolumes)))

        #===获取close数据
        headers = {
        'authority': 'www.okex.com',
        'sec-ch-ua': '^\\^',
        'timeout': '10000',
        'x-cdn': 'https://static.okex.com',
        'devid': '7f1dea77-90cd-4746-a13f-a98bac4a333b',
        'accept-language': 'zh-CN',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'accept': 'application/json',
        'x-utc': '8',
        'app-type': 'web',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.okex.com/markets/swap-info/eth-usd',
        'cookie': 'locale=zh_CN; _gcl_au=1.1.1849415495.'+str(tt)+'; _ga=GA1.2.1506507962.'+str(tt)+'; _gid=GA1.2.256681666.'+str(tt)+'; first_ref=https^%^3A^%^2F^%^2Fwww.okex.com^%^2Fcaptcha^%^3Fto^%^3DaHR0cHM6Ly93d3cub2tleC5jb20vbWFya2V0cy9zd2FwLWRhdGEvZXRoLXVzZA^%^3D^%^3D; _gat_UA-35324627-3=1; amp_56bf9d=gqC_GMDGl4q5Tk-BJhT-oP...1f711b989.1f711fv58.0.2.2',
        }

        params = (
        ('granularity', str(int(minute)*60)),
        ('size', '1000'),
        ('t', str(ttt)),
        )
        response = r.get('https://www.okex.com/v2/perpetual/pc/public/instruments/ETH-USD-SWAP/candles', headers=headers, params=params)

        if response.cookies.get_dict(): #保持cookie有效 
                s=r.session()
                c = r.cookies.RequestsCookieJar()#定义一个cookie对象
                c.set('cookie-name', 'cookie-value')#增加cookie的值
                s.cookies.update(c)#更新s的cookie
                s.get(url = 'https://www.okex.com/v2/perpetual/pc/public/instruments/ETH-USD-SWAP/candles?granularity=900&size=1000&t='+str(ttt))
        dw = pd.DataFrame(eval(json.dumps(response.json()))['data'])
        #print(df)
        dw.columns = ['timestamps','open','high','low','close','vol','p']
        datelist = []
        for timestamp in dw['timestamps']:
            datelist.append(timestamp.split('.000Z')[0].replace('T',' '))
        dw['timestamps'] = datelist
        dw['timestamps'] = pd.to_datetime(dw['timestamps'])+pd.to_timedelta('8 hours')
        #df['timestamps'] = df['timestamps'].apply(lambda x:time.mktime(time.strptime(str(x),'%Y-%m-%d %H:%M:%S')))
        #print(dw)
        dw['vol'] = list(map(float, dw['vol'].values))
        dw.to_csv(f'./datas/okex/eth/close.csv',index = False)
        dw = pd.read_csv(f'./datas/okex/eth/close.csv')
        Datainfo.getfulldata(dw)
        dw = pd.read_csv(f'./datas/okex/eth/close.csv')
        #===判断是否买入或者卖出
        print('(sum(buyVolumes10)/len(buyVolumes10)) /(sum(sellVolumes10)/len(sellVolumes10))  -->>',(sum(buyVolumes10)/len(buyVolumes10)) /(sum(sellVolumes10)/len(sellVolumes10))  )
        print('obv-->>',dw['obv'].tail(1).values ,'MA_obv-->>', dw['maobv'].tail(1).values)

        #人工智能计算结果
        learning = Datainfo.getnextdata(dw,'ETH-USD-SWAP')
        print('learning--->>>',learning)

        if((sum(buyVolumes)/len(buyVolumes)) /(sum(sellVolumes)/len(sellVolumes)) > 1.01 and (sum(buyVolumes10)/len(buyVolumes10)) /(sum(sellVolumes10)/len(sellVolumes10)) > 1.02 and dw['obv'].tail(1).values > dw['maobv'].tail(1).values and learning):
            print('买入')
            sendtext = '获取数据完毕。。。   判断为： -->>True-->>>  '+str(minute)+'分钟--->>>buyVolumes-->>'+str(df['buyVolumes'].values[-1])+'--->>>sellVolumes-->>'+str(df['sellVolumes'].values[-1])+'  ,预测结果-->>正确   -->>我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^'
            Datainfo.saveinfo(sendtext)
            return '买入'
        elif((sum(buyVolumes)/len(buyVolumes)) /(sum(sellVolumes)/len(sellVolumes)) < 0.99 and (sum(buyVolumes10)/len(buyVolumes10)) /(sum(sellVolumes10)/len(sellVolumes10)) < 0.97 and dw['obv'].tail(1).values < dw['maobv'].tail(1).values and (not learning)):
            print('卖出')
            sendtext = '获取数据完毕。。。   判断为： -->>True-->>>  '+str(minute)+'分钟--->>>buyVolumes-->>'+str(df['buyVolumes'].values[-1])+'--->>>sellVolumes-->>'+str(df['sellVolumes'].values[-1])+'  ,预测结果-->>正确   -->>我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^'
            Datainfo.saveinfo(sendtext)
            return '卖出'
        else:
            print('不买卖')
            return '不买卖'


    def getfulldata(df):


        #获取参数历史数据
        df['will'] = ta.WILLR(df['high'].values,df['low'].values,df['close'].values,timeperiod=14)
        df['upper'], df['middle'], df['lower'] = ta.BBANDS(
                        df.close.values,
                        timeperiod=20,
                        # number of non-biased standard deviations from the mean
                        nbdevup=2,
                        nbdevdn=2,
                        # Moving average type: simple moving average here
                        matype=0)
        df["rsi"] = ta.RSI(df['close'], timeperiod=14)
        df['slowk'], df['slowd'] = ta.STOCH(df['high'].values,
                                df['low'].values,
                                df['close'].values,
                                fastk_period=9,
                                slowk_period=3,
                                slowk_matype=0,
                                slowd_period=3,
                                slowd_matype=0)
        df["DEMA"] = ta.DEMA(df['close'].values, timeperiod=30)
        # MA - Moving average 移动平均线
        # 函数名：MA
        # 名称： 移动平均线
        # 简介：移动平均线，Moving Average，简称MA，原本的意思是移动平均，由于我们将其制作成线形，所以一般称之为移动平均线，简称均线。它是将某一段时间的收盘价之和除以该周期。 比如日线MA5指5天内的收盘价除以5 。
        # real = MA(close, timeperiod=30, matype=0)
        df["MA"] = ta.MA(df['close'].values, timeperiod=30, matype=0)
        # EMA和MACD
        df['obv'] = ta.OBV(df['close'].values,df['vol'].values)
        df['maobv'] = ta.MA(df['obv'].values, timeperiod=30, matype=0)
        df["MACD_macd"],df["MACD_macdsignal"],df["MACD_macdhist"] = ta.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=60)
        df['macd'] = 2*(df["MACD_macd"]-df["MACD_macdsignal"])
        df['upper'], df['middle'], df['lower'] = ta.BBANDS(
                    df.close.values,
                    timeperiod=26,
                    # number of non-biased standard deviations from the mean
                    nbdevup=2,
                    nbdevdn=2,
                    # Moving average type: simple moving average here
                    matype=0)
        df.to_csv(f'./datas/okex/eth/close.csv',index = False)

     #数据清洗
    def clean_data_df(df):
        # 计算当前、未来1-day涨跌幅
        df.loc[:,'1d_close_future_pct'] = df['close'].shift(-1).pct_change(1)
        df.loc[:,'now_1d_direction'] = df['close'].pct_change(1)
        df.dropna(inplace=True)
        # ====1代表上涨，0代表下跌
        df.loc[df['1d_close_future_pct'] > 0, 'future_1d_direction'] = 1
        df.loc[df['1d_close_future_pct'] <= 0, 'future_1d_direction'] = 0
        df = df[['now_1d_direction', 'future_1d_direction']]
        return df

    #增加数据标签
    def split_train_and_test(df):
        # 创建特征 X 和标签 y
        y = df['future_1d_direction'].values
        X = df.drop('future_1d_direction', axis=1).values
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test =  train_test_split(X, y, test_size=0.8, random_state=42)
        return X_train, X_test, y_train, y_test

    #svm_svc模型
    def svm_svc(X_train, X_test, y_train, y_test):
        clf = svm.SVC(gamma='auto')
        clf.fit(X_train, y_train)
        new_prediction = clf.predict(X_test)
    #   print("Prediction: {}".format(new_prediction))
        return (clf.score(X_test, y_test))

    #主函数 SVM
    def main(df):
        #数据清洗
        df = Datainfo.clean_data_df(df)
        X_train, X_test, y_train, y_test =  Datainfo.split_train_and_test(df)
        svm_score = Datainfo.svm_svc(X_train, X_test, y_train, y_test)

    #获取下个预期数值的方法
    def getnextdata(df,symbol):

        
        f_info = "\n开始获取是否"+symbol+"买入信号 SVM人工智能运算"
        print(f_info)
        Datainfo.saveinfo(f_info)
        #运行主函数
        Datainfo.main(df)
        #获取close值
        for i in range(1, 21, 1):
            df['close - ' + str(i) + 'd'] = df['close'].shift(i)

        df_20d = df[[x for x in df.columns if 'close' in x]].iloc[20:]
        df_20d = df_20d.iloc[:,::-1]   # 转换特征的顺序；

        #训练模型
        clf = svm.SVR(kernel='linear')
        features_train = df_20d[:200]
        labels_train = df_20d['close'].shift(-1)[:200]     # 回归问题的标签就是预测的就是股价，下一天的收盘价就是前一天的标签；
        features_test = df_20d[200:]
        labels_test = df_20d['close'].shift(-1)[200:]
        clf.fit(features_train, labels_train)     # 模型的训练过程；

        predict = clf.predict(features_test)      # 给你测试集的特征，返回的是测试集的标签，回归问题的标签就是股价；

        dft = pd.DataFrame(labels_test)
        dft['predict'] = predict     # 把前面预测的测试集的股价给添加到DataFrame中；
        dft = dft.rename(columns = {'close': 'Next Close', 'predict':'Predict Next Close'})

        current_close = df_20d[['close']].iloc[200:]
        next_open = df[['open']].iloc[220:].shift(-1)

        #获取df1 df2的值
        df1 = pd.merge(dft, current_close, left_index=True, right_index=True)

        df2 = pd.merge(df1, next_open, left_index=True, right_index=True)
        df2.columns = ['Next Close', 'Predicted Next Close', 'Current Close', 'Next Open']
        #画图
        df2['Signal'] = np.where(df2['Predicted Next Close'] > df2['Next Open'] ,1,0)

        df2['PL'] =  np.where(df2['Signal'] == 1,(df2['Next Close'] - df2['Next Open'])/df2['Next Open'],0)

        #df2['Strategy'] = (df2['PL'].shift(1)+1).cumprod()
        #df2['return'] = (df2['Next Close'].pct_change()+1).cumprod()

        #df2[['Strategy','return']].dropna().plot(figsize=(10, 6))

        #获取预期下个整点的值
        print(df2['PL'][-2:-1].values[0])
        Datainfo.saveinfo(df2['PL'][-2:-1].values[0])
        print(df2.tail(20))
        return df2['PL'][-2:-1].values[0]>0

    #获取用户API信息
    def get_userinfo():

        with open('api.json', 'r', encoding='utf-8') as f:
            obj = json.loads(f.read())


        api_key = obj['api_key']
        secret_key = obj['secret_key']
        passphrase = obj['passphrase']

        # flag是实盘与模拟盘的切换参数 flag is the key parameter which can help you to change between demo and real trading.
        # flag = '1'  # 模拟盘 demo trading
        flag = '0'  # 实盘 real trading

        return api_key,secret_key,passphrase,flag

    #保存信息
    def saveinfo(info):

        f_info = f'./datas/log/infodata.txt'
 

        with open(f_info,"a+",encoding='utf-8') as file:   #a :   写入文件，若文件不存在则会先创建再写入，但不会覆盖原文件，而是追加在文件末尾 
            file.write('\n'+str(info)+str(datetime.now()))

    
    #保存最终信息
    def save_finalinfo(info):

        f_day = f'./datas/log/day_buy.txt'

        with open(f_day,"a+",encoding='utf-8') as file:   #a :   写入文件，若文件不存在则会先创建再写入，但不会覆盖原文件，而是追加在文件末尾 
            file.write('\n'+str(info)+'--->>>'+str(datetime.now()))


    
    #设置自动下单
    def orderbuy(api_key, secret_key, passphrase, flag):

        # account api
        accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        
        # 设置持仓模式  Set Position mode
        result = accountAPI.get_position_mode('long_short_mode')
        # 设置杠杆倍数  Set Leverage
        result = accountAPI.set_leverage(instId='ETH-USD-SWAP', lever='100', mgnMode='cross')
        #Datainfo.saveinfo('设置100倍保证金杠杆完毕。。。')
        # trade api
        tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        # 批量下单  Place Multiple Orders
        # 批量下单  Place Multiple Orders
        result = tradeAPI.place_multiple_orders([
             {'instId': 'ETH-USD-SWAP', 'tdMode': 'cross', 'side': 'buy', 'ordType': 'market', 'sz': '3',
              'posSide': 'long',
              'clOrdId': 'a12344', 'tag': 'test1210'},
    

         ])
        print(result)

        #Datainfo.saveinfo('下单完毕。。。')

        lastprice = Datainfo.getlastprice(api_key, secret_key, passphrase, flag)

        #Datainfo.saveinfo('获取最新价格。。。'+str(lastprice))
        
        # 调整保证金  Increase/Decrease margint
        result = accountAPI.Adjustment_margin('ETH-USD-SWAP', 'short', 'add', '5')
        #Datainfo.saveinfo('调整保证金完毕。。。')

        # 策略委托下单  Place Algo Order
        result = tradeAPI.place_algo_order('ETH-USD-SWAP', 'cross', 'sell', ordType='conditional',
                                            sz='3',posSide='long', tpTriggerPx=str(float(lastprice)+50), tpOrdPx=str(float(lastprice)+50))
        #Datainfo.saveinfo(str(datetime.now())+'设置止盈完毕。。。'+str(float(lastprice)+50))


        sendtext = str(datetime.now())+'--->>>100倍杠杆，全仓委托：买入ETH-USD-SWAP -->> 3笔，价格是'+str(lastprice)+'，设置止盈完毕。。。'+str(float(lastprice)+50)
        Datainfo.save_finalinfo(str(datetime.now())+'--->>>我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^     -->>'+sendtext)
        SendDingding.sender(sendtext)

    #设置自动下单
    def ordersell(api_key, secret_key, passphrase, flag):

        # account api
        accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
        
        # 设置持仓模式  Set Position mode
        result = accountAPI.get_position_mode('long_short_mode')
        # 设置杠杆倍数  Set Leverage
        result = accountAPI.set_leverage(instId='ETH-USD-SWAP', lever='100', mgnMode='cross')
        #Datainfo.saveinfo('设置100倍保证金杠杆完毕。。。')
        # trade api
        tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        # 批量下单  Place Multiple Orders
        result = tradeAPI.place_order(instId='ETH-USD-SWAP', tdMode='cross', side='sell', posSide='short',
                              ordType='market', sz='3')
        print(result)

        #Datainfo.saveinfo('下单完毕。。。')

        lastprice = Datainfo.getlastprice(api_key, secret_key, passphrase, flag)

        #Datainfo.saveinfo('获取最新价格。。。'+str(lastprice))
        
        # 调整保证金  Increase/Decrease margint
        result = accountAPI.Adjustment_margin('ETH-USD-SWAP', 'short', 'add', '5')
        #Datainfo.saveinfo('调整保证金完毕。。。')

        # 策略委托下单  Place Algo Order
        result = tradeAPI.place_algo_order('ETH-USD-SWAP', 'cross', 'buy', ordType='conditional',
                                            sz='3',posSide='short', tpTriggerPx=str(float(lastprice)-50), tpOrdPx=str(float(lastprice)-50))
        #Datainfo.saveinfo(str(datetime.now)+'设置止盈完毕。。。'+str(float(lastprice)-50))


        sendtext = str(datetime.now())+'--->>>卖出100倍杠杆，全仓委托：ETH-USD-SWAP -->> 3笔，价格是'+str(lastprice)+'，设置止盈完毕。。。'+str(float(lastprice)-50)
        Datainfo.save_finalinfo(str(datetime.now())+'--->>>我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^     -->>'+sendtext)
        SendDingding.sender(sendtext)

    #查询最新价格
    def getlastprice(api_key, secret_key, passphrase, flag):

        # market api
        marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, False, flag)

        # 获取单个产品行情信息  Get Ticker
        result = marketAPI.get_ticker('ETH-USDT-SWAP')
        
        return eval(json.dumps(result['data'][0]))['last']
   
  
    class mywindows_multiprocessing ():

    
        #运行函数 必须写
        def run():
            sch = Datainfo.windowsshow()

            #声明2线程保存数据
            p1 = multiprocessing.Process(target = sch.showwindows)
            p2 = multiprocessing.Process(target = sch.okex5M_buy)


            #6个进程开始运行
            p2.start()
            p1.start()

            p2.join()
            p1.join()
            
            

    class Ui_MainWindow(object):


        def setupUi(self, MainWindow):
            MainWindow.setObjectName("MainWindow")
            MainWindow.resize(800, 600)
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
            self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 801, 551))
            self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
            self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
            self.verticalLayout.setContentsMargins(0, 0, 0, 0)
            self.verticalLayout.setObjectName("verticalLayout")
            self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.verticalLayoutWidget)
            self.dateTimeEdit.setObjectName("dateTimeEdit")
            self.dateTimeEdit.setAlignment(Qt.AlignRight)
            #设置日期最大值与最小值，在当前日期的基础上，后一年与前一年
            self.dateTimeEdit.setMinimumDate(QDate.currentDate().addDays(-365))
            self.dateTimeEdit.setMaximumDate(QDate.currentDate().addDays(365))
            self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss ddd a")
            #设置日历控件允许弹出
            self.dateTimeEdit.setCalendarPopup(True)
            self.verticalLayout.addWidget(self.dateTimeEdit)

            self.textBrowserone = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
            self.textBrowserone.setObjectName("textBrowser")
            self.textBrowserone.setStyleSheet("background-color:#4e72b8;font-size:20px; font-family:'行楷';font-weight:bold;")
            self.textBrowserone.setAlignment(Qt.AlignCenter)
            self.textBrowserone.verticalScrollBar().setValue(self.textBrowserone.maximumHeight())
            self.verticalLayout.addWidget(self.textBrowserone)

            self.textBrowsertwo = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
            self.textBrowsertwo.setObjectName("textBrowser")
            self.textBrowsertwo.setStyleSheet("background-color:#9b95c9;font-size:20px; font-family:'行楷';font-weight:bold;")
            self.textBrowsertwo.setAlignment(Qt.AlignCenter)
            self.textBrowsertwo.verticalScrollBar().setValue(self.textBrowsertwo.maximumHeight())
            self.verticalLayout.addWidget(self.textBrowsertwo)
            

            MainWindow.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(MainWindow)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
            self.menubar.setObjectName("menubar")
            self.menu = QtWidgets.QMenu(self.menubar)
            self.menu.setObjectName("menu")
            self.menu_2 = QtWidgets.QMenu(self.menubar)
            self.menu_2.setObjectName("menu_2")
            self.menu_3 = QtWidgets.QMenu(self.menubar)
            self.menu_3.setObjectName("menu_3")
   
            MainWindow.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(MainWindow)
            self.statusbar.setObjectName("statusbar")
            MainWindow.setStatusBar(self.statusbar)
            self.action = QtWidgets.QAction(MainWindow)
            self.action.setObjectName("action")
            self.menu.addAction(self.action)
            self.menubar.addAction(self.menu_3.menuAction())
            self.menubar.addAction(self.menu.menuAction())
            self.menubar.addAction(self.menu_2.menuAction())
       

            #oneAction = self.menu_3.addAction("运行")
            #oneAction.triggered.connect(mywindows.run())

            self.menubar.setStyleSheet("font-size:20px; font-family:'LiSu'; margin:0;padding:0;text-align:center;")
            #创建定时器
            self.Timer=QTimer()
            #定时器每1s工作一次
            self.Timer.start(60)
            #建立定时器连接通道  注意这里调用TimeUpdate方法，不是方法返回的的结果，所以不能带括号，写成self.TimeUpdate()是不对的
            self.Timer.timeout.connect(self.TimeUpdate)


            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)

        



        def TimeUpdate(self):
        
            #'yyyy-MM-dd hh:mm:ss dddd' 这是个时间的格式，其中yyyy代表年，MM是月，dd是天，hh是小时，mm是分钟，ss是秒，dddd是星期
            self.dateTimeEdit.setDateTime(QDateTime.currentDateTime()) 
          

            f_day = open(f'./datas/log/day_buy.txt',"r",encoding='utf-8')   #设置文件对象
            day_buy = f_day.read()     #将txt文件的所有内容读入到字符串str中
            f_day.close()   #将文件关闭
            if(day_buy):
                self.textBrowsertwo.clear()
                self.textBrowsertwo.append(day_buy)

            f_info = open(f'./datas/log/infodata.txt',"r",encoding='utf-8')   #设置文件对象
            infodata = f_info.read()     #将txt文件的所有内容读入到字符串str中
            f_info.close()   #将文件关闭
            if(infodata):
                self.textBrowserone.clear()
                self.textBrowserone.append(infodata)

            


        def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
            self.menu.setTitle(_translate("MainWindow", "关于"))
            self.menu_2.setTitle(_translate("MainWindow", "帮助"))
            self.menu_3.setTitle(_translate("MainWindow", "开始"))
            self.action.setText(_translate("MainWindow", "什么是深度学习"))

    class windowsshow():



        def showwindows(self):
            app = QtWidgets.QApplication(sys.argv) # 创建一个QApplication，也就是你要开发的软件app
            MainWindow = QtWidgets.QMainWindow() # 创建一个QMainWindow，用来装载你需要的各种组件、控件
            ui = Datainfo.Ui_MainWindow() # ui是Ui_MainWindow()类的实例化对象，Ui_MainWindow需要根据你的实例化对象的objectname，默认是MainWindow。
            ui.setupUi(MainWindow) # 执行类中的setupUi方法，方法的参数是第二步中创建的QMainWindow
            MainWindow.setWindowTitle("人工智能程序———okex自动交易v3.0")
            # 加载操作
            dark_stylesheet=qdarkstyle.load_stylesheet_from_environment()# PyQtGraphdark_stylesheet=qdarkstyle.load_stylesheet_from_environment(is_pyqtgraph)
            app.setStyleSheet(dark_stylesheet)
            MainWindow.show() # 执行QMainWindow的show()方法，显示这个QMainWindow
            Datainfo.textBrowserone = ui.textBrowserone
            Datainfo.textBrowsertwo = ui.textBrowsertwo

            ui.textBrowserone.append("欢迎运行 人工智能程序——okex自动交易v3.0")
  
            sys.exit(app.exec_()) # 使用exit()或者点击关闭按钮退出QApp



        def okex5M_buy(self):

            scheduler = BlockingScheduler()
            scheduler.add_job((self.getdatainfo), 'cron', args = ['5'], minute='*/5')
            print(scheduler.get_jobs())
            try:
                scheduler.start()
            except KeyboardInterrupt:
                scheduler.shutdown()

        
        def getdatainfo(self,minute):

            time.sleep(8)
            
            print(minute)
            isbuy  =  Datainfo.isbuy(minute)

            if('15单' == isbuy or '买单小于卖单'== isbuy):
                Datainfo.saveinfo('预测不买入。。。')
                return
            elif('买入' == isbuy):
                api_key, secret_key, passphrase, flag = Datainfo.get_userinfo()
                Datainfo.orderbuy(api_key, secret_key, passphrase, flag)
            elif('卖出' == isbuy):
                api_key, secret_key, passphrase, flag = Datainfo.get_userinfo()
                Datainfo.ordersell(api_key, secret_key, passphrase, flag)
            elif('不买卖' == isbuy):
                Datainfo.saveinfo('预测不买卖。。。')
                Datainfo.save_finalinfo('预测不买卖。。。')




           
#发钉钉的类先声明
class SendDingding:
    def sender(sendtexts):
             
        headers = {
        'Content-Type' : 'application/json'
        }
        timestamp = str(round(time.time()*1000))
        secret ="SEC050a3b2c9e5d8d0c777bbdd61270676a8bdad3608b36a086d70e95b712ad2db0"
        secret_enc = secret.encode('utf-8' )
        string_to_sign ='{}\n{}'.format(timestamp,secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        


        params = {
            'sign' :sign,
    
            'timestamp' : timestamp
        }
        text_data ={
        "msgtype" :"text" ,
            "text":{
                "content": str(datetime.now())+'--->>>我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^     -->> '+sendtexts
            }
        }
        roboturl='https://oapi.dingtalk.com/robot/send?access_token=f8195c9e4ad6da4427d67e80dffed5d07ecaca1d1e79462fb5c0a9c6b12e90f2'
        r.post(roboturl, data=json.dumps(text_data),params=params, headers=headers )

if __name__ == '__main__':

  
    
    #启动
    
  
    print('=============================================================================================')
    print('我们是守护者，也是一群时刻对抗危险和疯狂的可怜虫 ！^_^')
    print('=============================================================================================')
    print('=============================================================================================')


    


    paths = []
    paths.append(f'./datas/okex/')
    paths.append(f'./datas/okex/eth')        
    paths.append(f'./datas/log/')

    for p in paths :
        try:
            os.makedirs(p,exist_ok=True)
        except:
            pass
    
    time.sleep(3)

    
    f_info = f'./datas/log/infodata.txt'
    f_day = f'./datas/log/day_buy.txt'

    #清空文件内容
    file = open(f'./datas/log/day_buy.txt', 'w',encoding='utf-8').close()
    file = open(f'./datas/log/infodata.txt', 'w',encoding='utf-8').close()


    with open(f_info,"a+",encoding='utf-8') as file:   #a :   写入文件，若文件不存在则会先创建再写入，但不会覆盖原文件，而是追加在文件末尾 
        file.write("开始运行okex API 获取数据==="+str(datetime.now()))

    time.sleep(3)

    mywindowsmultiprocessing = Datainfo.mywindows_multiprocessing
    mywindowsmultiprocessing.run()
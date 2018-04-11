
import os
import pandas as pd
import seaborn as sns
import numpy as np
import talib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
#pd.set_option('display.mpl_style', 'default')
#import alpha_quant as aq
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARMA
mod = ARMA(rb['last'], order=(1,0))
res = mod.fit()
print(res.summary())
#rb.plot(colormap='Dark2')
BIC = np.zeros(10)
for p in range(10):
    mod = ARMA(rb['last'], order=(p,0))
    res = mod.fit()
    BIC[p] = res.bic

plt.plot(range(1,10), BIC[1:10], marker='o')    
plt.xlabel('Order of AR Model')
plt.ylabel('BIC')
plt.show()

ax = rb['last'].plot(figsize=(15,9))
ax.table(cellText=rb.describe().values, colWidths=[0.3]*len(rb.columns),
         rowLabels=rb.describe().index, colLabels=rb.describe().columns,
         loc='top')
plt.show()

def tsplot2(y, title, lags=None, figsize=(12,9)):
    #examine ACF/PACF
    fig=plt.figure(figsize=figsize)
    layout=(2,2)
    ts_ax = plt.subplot2grid(layout,(0,0))
    hist_ax = plt.subplot2grid(layout,(0,1))
    acf_ax = plt.subplot2grid(layout,(1,0))
    pacf_ax = plt.subplot2grid(layout,(1,1))      
    y.plot(ax=ts_ax)
    ts_ax.set_title(title, fontsize=14, fontweight='bold')
    y.plot(ax=hist_ax,kind='hist', bins=25)
    hist_ax.set_title('Hist')
    plot_acf(y,lags=lags,ax=acf_ax)
    plot_pacf(y,lags=lags,ax=pacf_ax)
    [ax.set_xlim(0) for ax in [acf_ax,pacf_ax]]
    sns.despine()
    plt.tight_layout()
    return ts_ax, acf_ax, pacf_ax

def getRangeData(dataPath, asset, startDate, endDate):
        path = dataPath + asset
        files = sorted([x for x in os.listdir(path) if startDate <= x <= endDate])
        
        
        df = pd.DataFrame([])
        for filename in files:
            targetPath = path + '/' + filename        
            print (targetPath)
            newdata = pd.read_csv(targetPath, sep=' ',
                          names = ["date","contract", "open", "high", "low", "close", "preclose", "time", "second", "last", 
                                   "bid", "ask", "bsize", "asize", "volume", "oi", "notional", "limitdown", "limitup"], header=0)
            df = pd.concat([df, newdata], ignore_index = True)
        return df
    

dataPath = '//home/linmich/data/commod/'    


assets = ['crude']
asset_dict = {}
for asset in assets:
    startDate = '20180325'
    endDate = '20180327'
    rb = getRangeData(dataPath, asset, startDate, endDate)  
    rb['chg']=100*rb['close']/(rb['close'].shift())-100
    rb['time']=pd.to_datetime(rb['time'])
    rb['vwap']=rb['close']
    rb['sector']='commodity futures'
    rb.set_index('time',inplace=True)
    #rb.close.plot(x='time', y='close')
    asset_dict[asset] = rb

rb['dtstr'] = rb['date'].astype(str) + rb['time'] + rb['second'].astype(str)
rb['dt'] = [datetime.datetime.strptime(x, "%Y%m%d%H:%M:%S%f") for x in rb['dtstr']]
rb.set_index('dt',inplace=True)

num_var = len(rb.iloc[1,:])
for i in range(2, num_var-3):
    tsplot2(rb.iloc[:,i].dropna(), title = rb.columns[i], lags=12)


ax = rb['last'].add_suffix('_min').plot()
rb['last'].resample('5Min', how='last').add_suffix('_5min').plot(ax = ax)


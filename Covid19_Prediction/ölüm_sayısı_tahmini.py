# -*- coding: utf-8 -*-
"""Ölüm_Sayısı_Tahmini.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JTrI6CJUod6XheGjpv15LPeFSq9d_Ifz

# **Türkiye'de Corona Ölüm Sayısının Tahmini**

Bu projede, Python'un Pandas kütüphanesi ile Basit Zaman Serisi tahmin yöntemlerini kullanarak koronavirüs olan ölüm sayısını tahmin edeceğiz.

Bu nedenle 27 Mart 2020'den 17 Haziran 2021'e kadar Türkiye'nin günlük raporlarını kullanacağız.

> Kütüphaneler
"""

import pandas as pd
# prophet by Facebook
from fbprophet import Prophet
from sklearn.metrics import mean_absolute_error
import warnings; warnings.simplefilter('ignore')
import matplotlib.pyplot as plt

"""# Google Drive """

from google.colab import drive
drive.mount('/content/gdrive')
!ln -s /content/gdrive/My\ Drive/ /mydrive
!ls /mydrive

# Commented out IPython magic to ensure Python compatibility.
# %cd /mydrive/Dersler/COVID19_Prediction/
!ls /mydrive/Dersler/COVID19_Prediction/

"""# Veri Seti"""

covid= pd.read_csv('veri_dead.csv',encoding= 'unicode_escape',sep=';')
covid.head()

covid= covid[['Date','Today_Dead','Tomorrow_Dead']].copy()
covid.tail()

covid['ds'] = pd.to_datetime(covid['Date'],  dayfirst = True)
covid.plot(x='ds',   figsize=(20, 5))

"""# Tahmin Methodu 1: Facebook's Prophet Model

## Prophet Modeli için veriyi hazırlama
"""

newcovid = covid[['ds', 'Today_Dead']].copy()                                      #ds:date stamp, zaman damgası
covid.drop(['ds'], axis=1, inplace=True)  
newcovid.rename(columns={'Today_Dead': 'y'}, inplace=True)                         #tahmin edilmesi için yeni veri seti hazırlandı

newcovid.tail()

"""## Eğitim ve Tahmin"""

m = Prophet( )
m.fit(newcovid)                                                                 #model fit() fonksiyonu ile eğitildi       
horizon= 1                                                                      #modelimizden bir gün sonrasını tahmin etmesini istediğimiz için 1 olarak belirledik
future = m.make_future_dataframe(periods=horizon)                               #tahmin edilmesi beklenen güne göre bir zaman kümesi oluşturuldu
forecast = m.predict(future)                                                    #buna göre predict() fonksiyonu ile tahmin yapıldı
forecast[['ds',  'yhat', 'yhat_lower', 'yhat_upper']].tail()                    #ythat= tahmin ettiği değer ; yhat_lower ve ythat_upper değerleri %95 güvenirlilik değerine göre belirleniyor

fig1 = m.plot(forecast)                                                         #Prophet, kırılmaları yakalayamıyor ve trende göre devam edeceği şeklinde çalışmaya devam ediyor

"""##Mean Absolute Error """

MAE={}                                                                          #Ortalama yapılan genel hata

MAE['Prophet'] =  mean_absolute_error(newcovid['y'], forecast[:-horizon]['yhat'])

print("MAE : {}".format(MAE))

"""Sonuç olarak, Prophet her değer için +,- %51 değerden sapıyor demek; bu da oldukça yüksek bir oran.

## Tahmin Edilen Sonuçları Karşılaştırma
"""

comparison= pd.DataFrame()
comparison['ds']=newcovid['ds'].copy()
comparison['Tomorrow_Dead']=covid['Tomorrow_Dead'].copy()
comparison['Prediction_Prophet'] = forecast[:-1].yhat
comparison.plot(title="comparison",x='ds',figsize=(20, 6))

"""# Tahmin Methodu 2: Simple Moving Average (SMA)

3 günlük penceere ile Simple Moving Average methodu

##Eğitim ve Tahmin
"""

window= 3
covid['Prediction_ SMA_3'] = covid.iloc[:,1].rolling(window=window).mean()
covid.head()

"""Mean Absolute Error """

MAE['SMA_3'] =  mean_absolute_error(covid[2:-1]['Tomorrow_Dead'], covid[2:-1]['Prediction_ SMA_3'])
print("MAE : {}".format(MAE))

"""## Standard Sapma'yı Hesaplama (upper/lower bands)

"""

rstd = covid.iloc[:,2].rolling(window=window).std()
bands = pd.DataFrame()
bands['Date']= covid['Date'].copy()
bands['lower'] = covid['Prediction_ SMA_3'] - 2 * rstd
bands['upper'] = covid['Prediction_ SMA_3'] + 2 * rstd


bands = bands.join(covid['Tomorrow_Dead']).join(covid['Prediction_ SMA_3'])
fig = plt.figure(figsize=(20, 6))
ax = bands.plot(title='Prediction_ SMA_3', figsize=(20, 6))
ax.fill_between(bands.index, bands['lower'], bands['upper'], color='#ADCCFF', alpha=0.4)
ax.set_xlabel('date')
ax.set_ylabel('Total Tomorrow_Dead')
ax.grid()

plt.show()

"""## Tahmin Edilen Sonuçları Karşılaştırma """

comparison['Prediction_SMA_3'] = covid['Prediction_ SMA_3']
print(comparison.tail())
comparison.plot(title="comparison",x='ds',figsize=(20, 6))

"""# Tahmin Method 3: Exponential Moving Average (EMA)

## Eğitim ve Tahmin
"""

covid['Prediction_EMA_3'] = covid.iloc[:,1].ewm(span=window,adjust=False).mean()
covid.head()

"""##Mean Absolute Error """

MAE['EMA_3'] =  mean_absolute_error(covid[1:-1]['Tomorrow_Dead'], covid[1:-1]['Prediction_EMA_3'])
print("MAE : {}".format(MAE))

"""## Standard Sapma'yı Hesaplama (upper/lower bands)"""

rstd = covid.iloc[:,2].rolling(window=window).std()
bands = pd.DataFrame()
bands['Date']= covid['Date'].copy()
bands['lower'] = covid['Prediction_EMA_3'] - 2 * rstd
bands['upper'] = covid['Prediction_EMA_3'] + 2 * rstd
bands = bands.join(covid['Tomorrow_Dead']).join(covid['Prediction_EMA_3'])
fig = plt.figure(figsize=(20, 6))
ax = bands.plot(title='Prediction_EMA_3', figsize=(20, 6))
ax.fill_between(bands.index, bands['lower'], bands['upper'], color='#ADCCFF', alpha=0.4)
ax.set_xlabel('date')
ax.set_ylabel('Tomorrow_Dead')
ax.grid()
plt.show()

"""## Tahmin Edilen Sonuçları Karşılaştırma """

comparison['Prediction_EMA_3'] = covid['Prediction_EMA_3']
comparison.plot(title="comparison",x='ds',figsize=(20, 6))

"""#Özet

"""

print('Mean Absolute Errors (MAE): {}'.format(MAE))


errorsDF = pd.DataFrame(MAE, index=['MAE']) 
ax = errorsDF.plot.bar(rot=0, figsize=(10, 7))

"""# Sonuç
Elde edilen veri seti ile Prophet SMA, EMA modelleri kullanılarak gelecek günkü toplam ölüm sayısı tahminleri gerçekleştirilmiştir.
* Veri seti 448 günün verilerinden oluşturulmuştur.
* EMA en düşük hata oranına sahiptir.


"""
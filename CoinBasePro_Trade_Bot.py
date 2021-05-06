#!/usr/bin/env python3

"""
Author: banhao@gmail.com
Version: 4.7.0

Issue Date: May 04, 2021
Release Note: optimize the code, remove redundancy code. Custome quote currency list that can support ETH, USDT, DAI as anchor cryptocurrencies.
Issue Date: April 27, 2021
Release Note: CoinBase API had 500 Internal Server Error on April 27, 2021. So add the exception code to handle it.
"""

import json, hmac, hashlib, time, requests, base64, collections, statistics, os
from requests.auth import AuthBase
from datetime import datetime, timedelta, date
from tqdm import tqdm
import pandas as pd
import numpy as np
import dateutil.parser as dp
import matplotlib
import pylab
import ta
from ta import add_all_ta_features
from ta.utils import dropna
from pandas import DataFrame
from math import isnan
from variable import *


# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        if type(request.body) is bytes:
                message = (timestamp + request.method + request.path_url + (request.body.decode('utf-8') or '')).encode('utf-8')
        else:
                message = (timestamp + request.method + request.path_url + (request.body or '')).encode('utf-8')

        hmac_key = base64.b64decode(bytes(self.secret_key, 'utf-8'))
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


def Error(responsecode):
    if responsecode == 500:
        print(responsecode, "Internal Server Error -- We had a problem with our server",  file=open("output.txt", "a"))
    if responsecode == 400:
        print(responsecode, "Bad Request -- Invalid request format",  file=open("output.txt", "a"))
    if responsecode == 401 :
        print(responsecode, "Unauthorized -- Invalid API Key",  file=open("output.txt", "a"))
    if responsecode == 403 :
        print(responsecode, "Forbidden -- You do not have access to the requested resource",  file=open("output.txt", "a"))
    if responsecode == 404 :
        print(responsecode, "Not Found",  file=open("output.txt", "a"))
    os.kill(os.getpid(), 9)

def available_quote_currency():
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))
    global BTC_USD_Price, current_property, USDC_balance, USDC_available, quote_currency_list
    quote_currency_list = []
    current_property = requests.get(api_url + 'accounts', auth=auth)
    if current_property.status_code != 200:
        Error(current_property.status_code)
    time.sleep(0.3)
    BTC_USDC_ticker = requests.get(api_url + 'products/BTC-USDC/ticker', auth=auth)
    if BTC_USDC_ticker.status_code != 200:
        Error(BTC_USDC_ticker.status_code)
    time.sleep(0.3)
    BTC_USD_Price = float(BTC_USDC_ticker.json()['price'])
    for item in current_property.json():
        if item['currency'] in quote_currency and item['currency'] != 'USDC':
            current_ticker = requests.get(api_url + 'products/' + item['currency'] + '-USDC/ticker', auth=auth)
            if current_ticker.status_code != 200:
                Error(current_ticker.status_code)
            time.sleep(0.3)
            if float(item['available']) != 0:
                quote_currency_USD_Price = float(current_ticker.json()['price'])
                quote_currency_balance = float(item['balance'])
                quote_currency_available = float(item['available'])
                quote_currency_value = float(format(quote_currency_available*quote_currency_USD_Price, '.2f'))
                print('%4s' % item['currency'], "Balance: ", '%15s' % format(quote_currency_balance, '.6f'), '%4s' % item['currency'],"| Available USDC: ", '%15s' % quote_currency_value, "| Equal BTC : ", format(quote_currency_value/BTC_USD_Price, '.6f'), file=open("output.txt", "a"))
                print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))
                quote_currency_list.append([item['currency'], quote_currency_USD_Price, quote_currency_balance, quote_currency_available, quote_currency_value])
        elif item['currency'] == 'USDC':
            USDC_balance = float(item['balance'])
            USDC_available = float(item['available'])
            print("USDC Balance: ", '%15s' % format(USDC_balance, '.6f'), "USDC | Available USDC: ", '%15s' % format(USDC_available, '.2f'), "| Equal BTC : ", format(USDC_available/BTC_USD_Price, '.6f'), file=open("output.txt", "a"))
            print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))
            quote_currency_list.append([item['currency'], 1, USDC_balance, USDC_available, USDC_available])



def calculate_cost(id):
    order_list = []
    done_orders = requests.get(api_url + 'orders?status=done&product_id='+id, auth=auth)
    if done_orders.status_code != 200:
        Error(done_orders.status_code)
    time.sleep(0.3)
    for _item in done_orders.json(): # Generate order_list
        if _item['side'] == 'sell' and _item['created_at'].split("T")[0] >= order_start_date:
            if _item['type'] == 'market':
                order_list.append( [id, "sell", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
            else:
                order_list.append( [id, "sell", float(_item['filled_size']), float(_item['price'])] )
        elif _item['side'] == 'buy' and _item['created_at'].split("T")[0] >= order_start_date:
            if _item['type'] == 'market':
                order_list.append( [id, "buy", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
            else:
                order_list.append( [id, "buy", float(_item['filled_size']), float(_item['price'])] )
    value = 0.000000
    size = 0.000000
    if len(order_list) == 0:
        cost = 0
        profit_and_loss = 0
        size = 0
    else:
        for j in range(len(order_list)):
            if order_list[j][1] == 'sell':
                break
            value = value + float(order_list[j][2]) * float(order_list[j][3])
            size = size + float(order_list[j][2])
    if size == 0:
        cost = 0
        profit_and_loss = 0
    else:
        cost = float(value)/float(size)
        id = order_list[0][0]
        current_ticker = requests.get(api_url + 'products/'+id+'/ticker', auth=auth)
        if current_ticker.status_code != 200:
            Error(current_ticker.status_code)
        time.sleep(0.3)
        last_trade_price = float(current_ticker.json()['price'])
        profit_and_loss = (last_trade_price-cost)/cost*100
    return(cost, size, profit_and_loss)


def get_current_property():
    total_value = 0
    available_quote_currency()
    for item in current_property.json():
        if item['currency'] == 'USDC':
            total_value = total_value + float(USDC_balance)
        elif float(item['balance']) > 0:
            for _item in quote_currency:
                id = item['currency'] + "-" + _item
                if id in products_list:
                    currency_cost = calculate_cost(id)
                    if currency_cost[1] != 0:
                        current_ticker = requests.get(api_url + 'products/'+id+'/ticker', auth=auth)
                        if current_ticker.status_code != 200:
                            Error(current_ticker.status_code)
                        time.sleep(0.3)
                        if _item == "USDC":
                            if float(item['balance']) < float(currency_cost[1]):
                                total_value = total_value + float(item['balance'])*float(current_ticker.json()['price'])
                                print('%4s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%4s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(item['balance'])*float(current_ticker.json()['price']), '.6f'), "USDC", file=open("output.txt", "a"))
                            else:
                                total_value = total_value + float(currency_cost[1])*float(current_ticker.json()['price'])
                                print('%4s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%4s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(currency_cost[1])*float(current_ticker.json()['price']), '.6f'), "USDC", file=open("output.txt", "a"))
                        else:
                            quote_currency_ticker = requests.get(api_url + 'products/' + _item + '-USDC/ticker', auth=auth)
                            if quote_currency_ticker.status_code != 200:
                                Error(quote_currency_ticker.status_code)
                            time.sleep(0.3)
                            if float(item['balance']) < float(currency_cost[1]):
                                total_value = total_value + float(item['balance'])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price'])
                                print('%4s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%4s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(item['balance'])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price']), '.6f'), "USDC", file=open("output.txt", "a"))
                            else:
                                total_value = total_value + float(currency_cost[1])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price'])
                                print('%4s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%4s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(currency_cost[1])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price']), '.6f'), "USDC", file=open("output.txt", "a"))
                        if float(currency_cost[2]) > 10:
                            sell_currency(id, item['balance'])
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))
    print('Total Value:', format(total_value, '.2f'), 'USDC | Total BTC:', format(total_value/BTC_USD_Price, '.6f'), file=open("output.txt", "a"))
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))


def min_max_price(Long_Term_Indicator_days, id):
    global min_max_list
    low_price_list = []
    high_price_list = []
    sell_sign_list = []
    regress_history_data_price = requests.get(api_url + 'products/'+id+'/candles?start='+start_datetime+'&end='+end_datetime+'&granularity='+str(Long_Term_Indicator_days_granularity), auth=auth)
    if regress_history_data_price.status_code != 200:
        Error(regress_history_data_price.status_code)
    time.sleep(2)
    if regress_history_data_price.json():
        for i in range(len(regress_history_data_price.json())):
            high_price_list.append([regress_history_data_price.json()[i][0], regress_history_data_price.json()[i][2]])
            low_price_list.append([regress_history_data_price.json()[i][0], regress_history_data_price.json()[i][1]])
        max_value, max_index = max((row[1], i)
                           for i, row in enumerate(high_price_list))
        min_value, min_index = min((row[1], i)
                           for i, row in enumerate(low_price_list))
    if ((datetime.utcfromtimestamp(current_datetime.json()['epoch']) - datetime.utcfromtimestamp(high_price_list[max_index][0])).days) * 10 <= (datetime.utcfromtimestamp(current_datetime.json()['epoch']) - datetime.utcfromtimestamp(low_price_list[min_index][0])).days :
        sell_signal = False
    else:
        sell_signal = True
    min_max_list.append([id, len(regress_history_data_price.json()), datetime.utcfromtimestamp(high_price_list[max_index][0]).__format__('%Y-%m-%d %H:%M:%S'), max_value, datetime.utcfromtimestamp(low_price_list[min_index][0]).__format__('%Y-%m-%d %H:%M:%S'), min_value, sell_signal])    
    print('%10s' % id," | ", '%4s' % len(regress_history_data_price.json())," | hightest price date:",datetime.utcfromtimestamp(high_price_list[max_index][0]).__format__('%Y-%m-%d %H:%M:%S')," | ", '%12s' % format(max_value, '.6f')," | lowest price date:", datetime.utcfromtimestamp(low_price_list[min_index][0]).__format__('%Y-%m-%d %H:%M:%S')," | ", '%12s' % format(min_value, '.6f'), file=open("output.txt", "a"))


def Short_Term_Indicator(Short_Term_Indicator_days, id):
    global df,short_term_simulation_data
    current_datetime = requests.get(api_url + 'time', auth=auth)
    if current_datetime.status_code != 200:
        Error(current_datetime.status_code)
    time.sleep(2)
    start_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']-86400*Short_Term_Indicator_days).__format__('%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']).__format__('%Y-%m-%d %H:%M:%S')
    regress_history_data_price = requests.get(api_url + 'products/'+id+'/candles?start='+start_datetime+'&end='+end_datetime+'&granularity='+str(Short_Term_Indicator_days_granularity), auth=auth)
    if regress_history_data_price.status_code != 200:
        Error(regress_history_data_price.status_code)
    time.sleep(0.3)
    df = regress_history_data_price.json()
    df.reverse()
    labels = ['Date', 'Low', 'High', 'Open', 'Close', 'Volume']
    df = pd.DataFrame.from_records(df, columns=labels)
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df = df.set_index('Date')
    df = dropna(df)
    indicator_MACD = ta.trend.MACD(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9, fillna = False)
    indicator_RSI7 = ta.momentum.RSIIndicator(df['Close'], window=7, fillna=False)
    indicator_RSI14 = ta.momentum.RSIIndicator(df['Close'], window=14, fillna=False)
    indicator_AROON = ta.trend.AroonIndicator(df['Close'], window=14, fillna=False)
    indicator_SMA5 = ta.trend.SMAIndicator(df['Close'], window=5, fillna=False)
    indicator_SMA10 = ta.trend.SMAIndicator(df['Close'], window=10, fillna=False)
    indicator_SMA60 = ta.trend.SMAIndicator(df['Close'], window=60, fillna=False)
    indicator_EMA = ta.trend.EMAIndicator(df['Close'], window=20, fillna=False)
    indicator_WMA = ta.trend.WMAIndicator(df['Close'], window=20, fillna=False)
    indicator_BOLLINGER = ta.volatility.BollingerBands(df['Close'], window=55,window_dev=2,fillna=False)
    indicator_CCI = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=144, constant=0.015, fillna=False)
    short_term_simulation_data = pd.DataFrame()
    short_term_simulation_data = df
    short_term_simulation_data['MACD'] = indicator_MACD.macd()
    short_term_simulation_data['MACD_DIFF'] = indicator_MACD.macd_diff()
    short_term_simulation_data['MACD_SIGNAL'] = indicator_MACD.macd_signal()
    short_term_simulation_data['RSI7'] = indicator_RSI7.rsi()
    short_term_simulation_data['RSI14'] = indicator_RSI14.rsi()
    short_term_simulation_data['ARRON_DOWN'] = indicator_AROON.aroon_down()
    short_term_simulation_data['ARRON_UP'] = indicator_AROON.aroon_up()
    short_term_simulation_data['ARRON'] = indicator_AROON.aroon_indicator()
    short_term_simulation_data['SMA5'] = indicator_SMA5.sma_indicator()
    short_term_simulation_data['SMA10'] = indicator_SMA10.sma_indicator()
    short_term_simulation_data['SMA60'] = indicator_SMA60.sma_indicator()
    short_term_simulation_data['EMA'] = indicator_EMA.ema_indicator()
    short_term_simulation_data['WMA'] = indicator_WMA.wma()
    short_term_simulation_data['BOLLINGER_HBAND'] = indicator_BOLLINGER.bollinger_hband()
    short_term_simulation_data['BOLLINGER_HBAND_INDICATOR'] = indicator_BOLLINGER.bollinger_hband_indicator()
    short_term_simulation_data['BOLLINGER_LBAND'] = indicator_BOLLINGER.bollinger_lband()
    short_term_simulation_data['BOLLINGER_LBAND_INDICATOR'] = indicator_BOLLINGER.bollinger_lband_indicator()
    short_term_simulation_data['BOLLINGER_MAVG'] = indicator_BOLLINGER.bollinger_mavg()
    short_term_simulation_data['BOLLINGER_PBAND'] = indicator_BOLLINGER.bollinger_pband()
    short_term_simulation_data['BOLLINGER_WBAND'] = indicator_BOLLINGER.bollinger_wband()
    short_term_simulation_data['CCI'] = indicator_CCI.cci()


def Long_Term_Indicator(Long_Term_Indicator_days, id):
    global df,long_term_simulation_data
    current_datetime = requests.get(api_url + 'time', auth=auth)
    if current_datetime.status_code != 200:
        Error(current_datetime.status_code)
    time.sleep(2)
    start_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']-86400*Long_Term_Indicator_days).__format__('%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']).__format__('%Y-%m-%d %H:%M:%S')
    regress_history_data_price = requests.get(api_url + 'products/'+id+'/candles?start='+start_datetime+'&end='+end_datetime+'&granularity='+str(Long_Term_Indicator_days_granularity), auth=auth)
    if regress_history_data_price.status_code != 200:
        Error(regress_history_data_price.status_code)
    time.sleep(0.3)
    df = regress_history_data_price.json()
    df.reverse()
    labels = ['Date', 'Low', 'High', 'Open', 'Close', 'Volume']
    df = pd.DataFrame.from_records(df, columns=labels)
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df = df.set_index('Date')
    df = dropna(df)
    indicator_MACD = ta.trend.MACD(df['Close'], window_slow = 26, window_fast = 12, window_sign = 9, fillna = False)
    indicator_RSI7 = ta.momentum.RSIIndicator(df['Close'], window=7, fillna=False)
    indicator_RSI14 = ta.momentum.RSIIndicator(df['Close'], window=14, fillna=False)
    indicator_AROON = ta.trend.AroonIndicator(df['Close'], window=14, fillna=False)
    indicator_SMA5 = ta.trend.SMAIndicator(df['Close'], window=5, fillna=False)
    indicator_SMA10 = ta.trend.SMAIndicator(df['Close'], window=10, fillna=False)
    indicator_SMA60 = ta.trend.SMAIndicator(df['Close'], window=60, fillna=False)
    indicator_EMA = ta.trend.EMAIndicator(df['Close'], window=20, fillna=False)
    indicator_WMA = ta.trend.WMAIndicator(df['Close'], window=20, fillna=False)
    indicator_BOLLINGER = ta.volatility.BollingerBands(df['Close'], window=55,window_dev=2,fillna=False)
    indicator_CCI = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=144, constant=0.015, fillna=False)
    long_term_simulation_data = pd.DataFrame()
    long_term_simulation_data = df
    long_term_simulation_data['MACD'] = indicator_MACD.macd()
    long_term_simulation_data['MACD_DIFF'] = indicator_MACD.macd_diff()
    long_term_simulation_data['MACD_SIGNAL'] = indicator_MACD.macd_signal()
    long_term_simulation_data['RSI7'] = indicator_RSI7.rsi()
    long_term_simulation_data['RSI14'] = indicator_RSI14.rsi()
    long_term_simulation_data['ARRON_DOWN'] = indicator_AROON.aroon_down()
    long_term_simulation_data['ARRON_UP'] = indicator_AROON.aroon_up()
    long_term_simulation_data['ARRON'] = indicator_AROON.aroon_indicator()
    long_term_simulation_data['SMA5'] = indicator_SMA5.sma_indicator()
    long_term_simulation_data['SMA10'] = indicator_SMA10.sma_indicator()
    long_term_simulation_data['SMA60'] = indicator_SMA60.sma_indicator()
    long_term_simulation_data['EMA'] = indicator_EMA.ema_indicator()
    long_term_simulation_data['WMA'] = indicator_WMA.wma()
    long_term_simulation_data['BOLLINGER_HBAND'] = indicator_BOLLINGER.bollinger_hband()
    long_term_simulation_data['BOLLINGER_HBAND_INDICATOR'] = indicator_BOLLINGER.bollinger_hband_indicator()
    long_term_simulation_data['BOLLINGER_LBAND'] = indicator_BOLLINGER.bollinger_lband()
    long_term_simulation_data['BOLLINGER_LBAND_INDICATOR'] = indicator_BOLLINGER.bollinger_lband_indicator()
    long_term_simulation_data['BOLLINGER_MAVG'] = indicator_BOLLINGER.bollinger_mavg()
    long_term_simulation_data['BOLLINGER_PBAND'] = indicator_BOLLINGER.bollinger_pband()
    long_term_simulation_data['BOLLINGER_WBAND'] = indicator_BOLLINGER.bollinger_wband()
    long_term_simulation_data['CCI'] = indicator_CCI.cci()


def buy_currency(id, currency, available_balance):
    in_hold_list = False
    order_size = 0
    current_ticker = requests.get(api_url + 'products/'+id+'/ticker', auth=auth)
    if current_ticker.status_code != 200:
        Error(current_ticker.status_code)
    time.sleep(0.3)
    current_product = requests.get(api_url + 'products/'+id, auth=auth)
    if current_product.status_code != 200:
        Error(current_product.status_code)
    time.sleep(0.3)
    base_min_size = float(current_product.json()['base_min_size'])
    last_trade_price = float(current_ticker.json()['price'])
    for item in current_property.json(): # When already hold this currency
        if currency == item['currency'] and float(item['balance']) > 0:
            print(id, "is in the HOLD LIST", file=open("output.txt", "a"))
            in_hold_list = True
    if in_hold_list:
        order_list = []
        done_orders = requests.get(api_url + 'orders?status=done&product_id='+id, auth=auth)
        if done_orders.status_code != 200:
            Error(done_orders.status_code)
        time.sleep(0.3)
        for _item in done_orders.json(): # Generate order_list
            if _item['side'] == 'sell' and _item['created_at'].split("T")[0] >= order_start_date:
                if _item['type'] == 'market':
                    order_list.append( [id, "sell", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
                else:
                    order_list.append( [id, "sell", float(_item['filled_size']), float(_item['price'])] )
            elif _item['side'] == 'buy' and _item['created_at'].split("T")[0] >= order_start_date:
                if _item['type'] == 'market':
                    order_list.append( [id, "buy", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
                else:
                    order_list.append( [id, "buy", float(_item['filled_size']), float(_item['price'])] )
        cost_price = []
        if len(order_list) == 0:
            min_price = 0.0
        elif len(order_list) == 1:
            min_price = order_list[0][3]
        elif len(order_list) > 1 and order_list[1][1] == "sell":
            min_price = order_list[0][3]
        elif len(order_list) > 1 and order_list[0][1] == "sell":
            min_price = 0.0
        else:
            for j in range(len(order_list)):
                if order_list[j][1] == 'buy':
                    cost_price.append(order_list[j][3])
                if order_list[j][1] == 'sell':
                    break
            min_price = min(cost_price)
        print(id, "Minimun buy price is:", format(min_price, '.6f'), file=open("output.txt", "a"))
        if float(last_trade_price) < float(min_price*(1-third_buy_percent)): # when price less than the minimum price third_buy_percent
            Short_Term_Indicator(Short_Term_Indicator_days, id)
            Long_Term_Indicator(Long_Term_Indicator_days, id)
            if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
                print("Holding the currency", id, "price is less than the minimum price *", 1-third_buy_percent, file=open("output.txt", "a"))
                order_size = int(available_balance*third_buy_percent/last_trade_price*(1/base_min_size))/(1/base_min_size)
                order = {
                        'size': order_size,
                        'price': last_trade_price,
                        'side': 'buy',
                        'product_id': id,
                        }
                print(order, file=open("output.txt", "a"))
                request_order = requests.post(api_url + 'orders', json=order, auth=auth)
                if request_order.status_code != 200:
                    Error(request_order.status_code)
                time.sleep(0.3)
                print(json.dumps(request_order.json(), indent=4), file=open("output.txt", "a"))
                time.sleep(seconds_cancel_order)
                available_quote_currency()
        elif float(last_trade_price) < float(min_price*(1-second_buy_percent)): # when price less than the minimum price second_buy_percent
            Short_Term_Indicator(Short_Term_Indicator_days, id)
            Long_Term_Indicator(Long_Term_Indicator_days, id)
            if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
                print("Holding the currency", id, "price is less than the minimum price *", 1-second_buy_percent, file=open("output.txt", "a"))
                order_size = int(available_balance*second_buy_percent/last_trade_price*(1/base_min_size))/(1/base_min_size)
                order = {
                        'size': order_size,
                        'price': last_trade_price,
                        'side': 'buy',
                        'product_id': id,
                        }
                print(order, file=open("output.txt", "a"))
                request_order = requests.post(api_url + 'orders', json=order, auth=auth)
                if request_order.status_code != 200:
                    Error(request_order.status_code)
                time.sleep(0.3)
                print(json.dumps(request_order.json(), indent=4), file=open("output.txt", "a"))
                time.sleep(seconds_cancel_order)
                available_quote_currency()
        else:
            print("Holding the currency", id, "price is NOT less than the minimum price *",1-second_buy_percent, file=open("output.txt", "a"))
    elif not in_hold_list:
        Short_Term_Indicator(Short_Term_Indicator_days, id)
        Long_Term_Indicator(Long_Term_Indicator_days, id)
        if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100 and long_term_simulation_data['Low'].iloc[-1] < long_term_simulation_data['BOLLINGER_LBAND'].iloc[-1]:
            print("First buy:", id, file=open("output.txt", "a"))
            order_size = int(available_balance*first_buy_percent/last_trade_price*(1/base_min_size))/(1/base_min_size)
            order = {
                    'size': order_size,
                    'price': last_trade_price,
                    'side': 'buy',
                    'product_id': id,
                    }
            print(order, file=open("output.txt", "a"))
            request_order = requests.post(api_url + 'orders', json=order, auth=auth)
            if request_order.status_code != 200:
                Error(request_order.status_code)
            time.sleep(0.3)
            print(json.dumps(request_order.json(), indent=4), file=open("output.txt", "a"))
            time.sleep(seconds_cancel_order)
            available_quote_currency()


def sell_currency(id, balance):
    currency_cost = calculate_cost(id)
    current_ticker = requests.get(api_url + 'products/'+id+'/ticker', auth=auth)
    if current_ticker.status_code != 200:
        Error(current_ticker.status_code)
    time.sleep(0.3)
    Short_Term_Indicator(Short_Term_Indicator_days, id)
    Long_Term_Indicator(Long_Term_Indicator_days, id)
    last_trade_price = float(current_ticker.json()['price'])
    if float(balance) > float(currency_cost[1]):
        sell_size = float(currency_cost[1])
    elif float(balance) <= float(currency_cost[1]):
        sell_size = float(balance)
    if float(last_trade_price) > currency_cost[0]*profit_rate and short_term_simulation_data['CCI'].iloc[-1] > 100 and long_term_simulation_data['Close'].iloc[-1] > long_term_simulation_data['BOLLINGER_HBAND'].iloc[-1] and currency_cost[1] != 0:
        order = {
                'size': sell_size,
                'price': last_trade_price,
                'side': 'sell',
                'product_id': id,
                }
        print(order, file=open("output.txt", "a"))
        request_order = requests.post(api_url + 'orders', json=order, auth=auth)
        if request_order.status_code != 200:
            Error(request_order.status_code)
        print(json.dumps(request_order.json(), indent=4), file=open("output.txt", "a"))
        time.sleep(seconds_cancel_order)


def cancel_order():
    open_orders = requests.get(api_url + 'orders?status=open', auth=auth)
    if open_orders.status_code != 200:
        Error(open_orders.status_code)
    time.sleep(0.3)
    for item in open_orders.json():
        if item['side'] == 'sell':
            print("Open Order - Sell: ", item['product_id'], item['size'], "| price: ", float(item['price'])*float(item['size']), "BTC | value: ", format(float(item['price'])*float(item['size'])*float(BTC_USD_Price), '.2f'), "USD", file=open("output.txt", "a"))
        else:
            print("Open Order - buy: ", item['product_id'], item['size'], "| price: ", float(item['price'])*float(item['size']), "BTC | value: ", format(float(item['price'])*float(item['size'])*float(BTC_USD_Price), '.2f'), "USD", file=open("output.txt", "a"))
        # Cancel Order which is created more than x seconds (define by variable "seconds_cancel_order")
        order_created_at = datetime.strptime(str(item['created_at']),'%Y-%m-%dT%H:%M:%S.%fZ')+timedelta(seconds=seconds_cancel_order)
        if (datetime.strptime(str(current_datetime.json()['iso']),'%Y-%m-%dT%H:%M:%S.%fZ')) > order_created_at:
            cancel_order = requests.delete(api_url + 'orders/'+item['id'], auth=auth)
            if cancel_order.status_code != 200:
                Error(cancel_order.status_code)
            time.sleep(0.3)
            print("Cancel Order: ", json.dumps(cancel_order.json(), indent=4), file=open("output.txt", "a"))


api_url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangeAuth(api_key, secret_key, passphrase)
while True:
    global order_list, products_list, min_max_list, coinbase_products
    order_list = []
    products_list = []
    min_max_list = []
    current_datetime = requests.get(api_url + 'time', auth=auth)
    if current_datetime.status_code != 200:
        Error(current_datetime.status_code)
    time.sleep(0.3)
    start_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']-86400*Long_Term_Indicator_days).__format__('%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.utcfromtimestamp(current_datetime.json()['epoch']).__format__('%Y-%m-%d %H:%M:%S')
    print('============================================================================================================================================', file=open("output.txt", "a"))
    print("Current local date time(CST): ", datetime.utcfromtimestamp(current_datetime.json()['epoch']+seconds_UTC2local).__format__('%Y-%m-%d %H:%M:%S'), file=open("output.txt", "a"))
    print("Start Date(UTC) : ",start_datetime,"   End Date(UTC) : ", end_datetime, file=open("output.txt", "a"))
    coinbase_products = requests.get(api_url + 'products', auth=auth)
    if coinbase_products.status_code != 200:
        Error(coinbase_products.status_code)
    time.sleep(0.3)
    if len(include_currency) != 0:
        for _item in include_currency:
            products_list.append(_item)
    else:
        for _item in coinbase_products.json():
            if (_item['id'] not in exclude_currency) and (_item['status_message'] == "") and (_item['quote_currency'] in quote_currency):
                products_list.append(_item['id'])
    get_current_property()
    for item in current_property.json():
        for _item in quote_currency:
            id = item['currency'] + "-" + _item
            if id in products_list:
                min_max_price(Long_Term_Indicator_days,id)
                for i in range(len(quote_currency_list)):
                    if (quote_currency_list[i][0] == _item) and (float(quote_currency_list[i][4]) > float(quote_lower_limit[_item])):
                        available_balance = quote_currency_list[i][3]
                        buy_currency(id, item['currency'], available_balance)
                    elif (quote_currency_list[i][0] == _item) and (float(quote_currency_list[i][4]) < float(quote_lower_limit[_item])):
                        print('Available ' + _item + ' is less than the ' + _item + ' Lower Limit for buying ', id, file=open("output.txt", "a"))
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open("output.txt", "a"))
    cancel_order()


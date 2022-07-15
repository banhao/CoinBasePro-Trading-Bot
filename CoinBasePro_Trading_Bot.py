#!/usr/bin/env python3

"""
Disclaimer:
This project is for informational purposes only. You should not construe any such information or other material as legal, tax, investment, financial, or other advice. Nothing contained here constitutes a solicitation, recommendation, endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such jurisdiction.
If you plan to use real money, USE AT YOUR OWN RISK.
Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs, or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.
免责声明：
该项目仅供参考。您不应将任何此类信息或其他材料解释为法律、税务、投资、财务或其他建议。此处包含的任何内容均不构成我或任何第三方服务提供商在本或任何其他司法管辖区购买或出售任何证券或其他金融工具的招揽、推荐、背书或要约此类司法管辖区的法律。
如果您打算使用真钱，请自行承担风险。
在任何情况下，我均不对任何索赔、损害、损失、费用、成本或义务承担任何责任，包括但不限于任何直接或间接的利润损失损害。


This product is protected by Canadian Copyright Act, please do not use any behavior that violates the law, For more detail please refer to https://laws-lois.justice.gc.ca/eng/acts/C-42/FullText.html
本作品受加拿大版权法保护，请不要使用任何有违法律的行为，详细请参见 https://laws-lois.justice.gc.ca/eng/acts/C-42/FullText.html

Author: banhao@gmail.com
Version: 5.7
Issue Date: July 14,2022
Release Note: 
    final version
Copyright © Hao Ban - 2022
"""


import json, hmac, hashlib, time, requests, base64, collections, statistics, os, string, random, decimal
import urllib.parse as urlparse
from urllib.parse import unquote, urlencode
from requests.auth import AuthBase
from datetime import datetime, timedelta, date
from calendar import timegm
from tqdm import tqdm
from cryptography.fernet import Fernet
from decimal import *
import pandas as pd
import numpy as np
import dateutil.parser as dp
import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import pylab
import ta
import xml.etree.ElementTree as ET
from ta import add_all_ta_features
from ta.utils import dropna
from pandas import DataFrame
from math import isnan
from xml.dom import minidom
from importlib import reload
from twilio.rest import Client
from import_file import import_file


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
        print(responsecode, "Internal Server Error -- We had a problem with our server",  file=open(variable.output_file, "a"))
    if responsecode == 400:
        print(responsecode, "Bad Request -- Invalid request format",  file=open(variable.output_file, "a"))
    if responsecode == 401 :
        print(responsecode, "Unauthorized -- Invalid API Key",  file=open(variable.output_file, "a"))
    if responsecode == 403 :
        print(responsecode, "Forbidden -- You do not have access to the requested resource",  file=open(variable.output_file, "a"))
    if responsecode == 404 :
        print(responsecode, "Not Found",  file=open(variable.output_file, "a"))
    os.kill(os.getpid(), 9)


def available_quote_currency(output_screen):
    if output_screen:
        print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open(variable.output_file, "a"))
    global BTC_USD_Price, current_property, quote_currency_list, total_value
    total_value = 0
    quote_currency_list = []
    current_property = requests.get(api_url + 'accounts', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if current_property.status_code != 200:
        Error(current_property.status_code)
    BTC_USD_ticker = requests.get(api_url + 'products/BTC-USD/ticker', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if BTC_USD_ticker.status_code != 200:
        Error(BTC_USD_ticker.status_code)
    BTC_USD_Price = float(BTC_USD_ticker.json()['price'])
    for item in current_property.json():
        if item['currency'] in variable.quote_currency :
            current_ticker = requests.get(api_url + 'products/' + item['currency'] + '-USD/ticker', headers=headers, auth=auth)
            time.sleep(variable.seconds_pause_request)
            if current_ticker.status_code != 200:
                Error(current_ticker.status_code)
            if float(item['available']) != 0:
                quote_currency_USD_Price = float(current_ticker.json()['price'])
                quote_currency_balance = float(item['balance'])
                quote_currency_available = float(item['available'])
                quote_currency_value = float(format(quote_currency_available*quote_currency_USD_Price, '.2f'))
                if output_screen:
                    print('%5s' % item['currency'], "Balance: ", '%15s' % format(quote_currency_balance, '.6f'), '%4s' % item['currency'],"| Available USD: ", '%15s' % quote_currency_value, "| Equal BTC : ", format(quote_currency_value/BTC_USD_Price, '.6f'), file=open(variable.output_file, "a"))
                    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open(variable.output_file, "a"))
                quote_currency_list.append([item['currency'], quote_currency_USD_Price, quote_currency_balance, quote_currency_available, quote_currency_value])
                total_value = total_value + quote_currency_value


def calculate_cost(id):
    order_list = []
    last_buy_date_list = []
    done_orders = requests.get(api_url + 'orders?status=done&product_id='+id, headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if done_orders.status_code != 200:
        Error(done_orders.status_code)
    for _item in done_orders.json(): # Generate order_list
        if _item['side'] == 'sell' and _item['created_at'].split("T")[0] >= variable.order_start_date:
            if _item['type'] == 'market':
                order_list.append( [id, "sell", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
            else:
                order_list.append( [id, "sell", float(_item['filled_size']), float(_item['price'])] )
        elif _item['side'] == 'buy' and _item['created_at'].split("T")[0] >= variable.order_start_date:
            last_buy_date_list.append(_item['created_at'].split("T")[0])
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
        current_ticker = requests.get(api_url + 'products/'+id+'/ticker', headers=headers, auth=auth)
        time.sleep(variable.seconds_pause_request)
        if current_ticker.status_code != 200:
            Error(current_ticker.status_code)
        last_trade_price = float(current_ticker.json()['price'])
        profit_and_loss = (last_trade_price-cost)/cost*100
    if len(last_buy_date_list) != 0:
        last_buy_date = max(last_buy_date_list)
    else:
        last_buy_date = ''
    return(cost, size, profit_and_loss, last_buy_date, order_list)


def get_current_property():
    available_quote_currency(True)
    global total_value
    for item in current_property.json():
        if float(item['balance']) > 0:
            for _item in variable.quote_currency:
                id = item['currency'] + "-" + _item
                if id in products_list:
                    currency_cost = calculate_cost(id)
                    if currency_cost[1] != 0:
                        current_ticker = requests.get(api_url + 'products/'+id+'/ticker', headers=headers, auth=auth)
                        time.sleep(variable.seconds_pause_request)
                        if current_ticker.status_code != 200:
                            Error(current_ticker.status_code)
                        quote_currency_ticker = requests.get(api_url + 'products/' + _item + '-USD/ticker', headers=headers, auth=auth)
                        time.sleep(variable.seconds_pause_request)
                        if quote_currency_ticker.status_code != 200:
                            Error(quote_currency_ticker.status_code)
                        if float(item['balance']) < float(currency_cost[1]):
                            if item['currency'] not in variable.quote_currency:
                                total_value = total_value + float(item['balance'])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price'])
                            print('%5s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%5s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(item['balance'])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price']), '.6f'), "USD", file=open(variable.output_file, "a"))
                        else:
                            if item['currency'] not in variable.quote_currency:
                                total_value = total_value + float(item['balance'])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price'])
                            print('%5s' % item['currency'], "Balance: ",'%15s' % format(float(item['balance']), '.6f'), '%5s' % item['currency'], "| order cost:" , '%15s' % format(float(currency_cost[0]), '.6f'), '%4s' % _item, "| order size:", '%15s' % format(float(currency_cost[1]), '.6f'), " | ", '%10s' % format(float(currency_cost[2]), '.2f'),"%", " | ", '%15s' % format(float(currency_cost[1])*float(current_ticker.json()['price'])*float(quote_currency_ticker.json()['price']), '.6f'), "USD", file=open(variable.output_file, "a"))
                        if float(currency_cost[2]) > 0 and (not variable.Buy_Sale_Policy_1) :
                            sell_currency(id)
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open(variable.output_file, "a"))
    print('Total Value:', format(total_value, '.2f'), 'USD | Total BTC:', format(total_value/BTC_USD_Price, '.6f'), file=open(variable.output_file, "a"))
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open(variable.output_file, "a"))


def min_max_price(interval, limit, id):
    global min_max_list
    low_price_list = []
    high_price_list = []
    sell_sign_list = []
    regress_history_data_price = requests.get(api_url + 'products/'+id+'/candles?start='+datetime.utcfromtimestamp(float(time.time())-interval*limit).__format__('%Y-%m-%d %H:%M:%S')+'&end='+datetime.utcfromtimestamp(float(time.time())).__format__('%Y-%m-%d %H:%M:%S')+'&granularity='+str(interval), headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if regress_history_data_price.status_code != 200:
        Error(regress_history_data_price.status_code)
    if regress_history_data_price.json():
        for i in range(len(regress_history_data_price.json())):
            high_price_list.append([regress_history_data_price.json()[i][0], regress_history_data_price.json()[i][2]])
            low_price_list.append([regress_history_data_price.json()[i][0], regress_history_data_price.json()[i][1]])
        max_value, max_index = max((row[1], i)
                           for i, row in enumerate(high_price_list))
        min_value, min_index = min((row[1], i)
                           for i, row in enumerate(low_price_list))
    min_max_list.append([id, len(regress_history_data_price.json()), datetime.utcfromtimestamp(high_price_list[max_index][0]).__format__('%Y-%m-%d %H:%M:%S'), max_value, datetime.utcfromtimestamp(low_price_list[min_index][0]).__format__('%Y-%m-%d %H:%M:%S'), min_value ])
    print('%10s' % id," | ", '%4s' % len(regress_history_data_price.json())," | highest price date:",datetime.utcfromtimestamp(high_price_list[max_index][0]).__format__('%Y-%m-%d %H:%M:%S')," | ", '%12s' % format(max_value, '.6f')," | lowest price date:", datetime.utcfromtimestamp(low_price_list[min_index][0]).__format__('%Y-%m-%d %H:%M:%S')," | ", '%12s' % format(min_value, '.6f'), file=open(variable.output_file, "a"))


def BOLLINGER_DELTA(window,serial_data):
    BOLLINGER_DELTA = []
    i = 0
    while i < len(serial_data):
        BOLLINGER_DELTA.append( serial_data['BOLLINGER_HBAND'][i] - serial_data['BOLLINGER_LBAND'][i] )
        i += 1
    serial_data['BOLLINGER_DELTA'] = BOLLINGER_DELTA
    
    i = len(serial_data)
    while i >= (len(serial_data) - np.count_nonzero(~np.isnan(serial_data['BOLLINGER_DELTA'])) + window):
        if pd.notna(serial_data['BOLLINGER_DELTA'][i-1]):
            serial_data.iloc[i-window:i,serial_data.columns.get_loc('BOLLINGER_DELTA_SQUARE')] = serial_data['BOLLINGER_DELTA'].iloc[i-window:i] ** 2
            MAX_DELTA_SQUARE = serial_data['BOLLINGER_DELTA_SQUARE'].iloc[i-window:i].max()
            MIN_DELTA_SQUARE = serial_data['BOLLINGER_DELTA_SQUARE'].iloc[i-window:i].min()
            K = 100/(MAX_DELTA_SQUARE - MIN_DELTA_SQUARE)
            serial_data.iloc[i-window:i,serial_data.columns.get_loc('BOLLINGER_DELTA_Indicator')] = (serial_data['BOLLINGER_DELTA_SQUARE'].iloc[i-window:i] - MIN_DELTA_SQUARE) * K
        i -= 1


def BOLLINGER_OUTSTANDING_KLINE(serial_data):
    up_bollinger = []
    down_bollinger = []
    for i in list(serial_data.index):
        if i > (serial_data['CCI'].index[serial_data['CCI'].apply(np.isnan)][-1] + timedelta(days=variable.indicator_CCI_window)):
            if serial_data['Close'][i] >  serial_data['BOLLINGER_HBAND'][i] and serial_data['Open'][i] > serial_data['BOLLINGER_HBAND'][i] and serial_data['CCI'][i] > 100:
                up_bollinger.append(float(serial_data['High'][i]))
                down_bollinger.append(np.nan)
            elif serial_data['Close'][i] <  serial_data['BOLLINGER_LBAND'][i] and serial_data['Open'][i] < serial_data['BOLLINGER_LBAND'][i] and serial_data['CCI'][i] < -100:
                up_bollinger.append(np.nan)
                down_bollinger.append(float(serial_data['Low'][i]))
            else:
                up_bollinger.append(np.nan)
                down_bollinger.append(np.nan)
        else:
            up_bollinger.append(np.nan)
            down_bollinger.append(np.nan)
    return(up_bollinger, down_bollinger)


def Serial_Data_Indicator(interval, limit, id):
    regress_history_data_price = requests.get(api_url + 'products/'+id+'/candles?start='+datetime.utcfromtimestamp(float(time.time())-interval*limit).__format__('%Y-%m-%d %H:%M:%S')+'&end='+datetime.utcfromtimestamp(float(time.time())).__format__('%Y-%m-%d %H:%M:%S')+'&granularity='+str(interval), headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if regress_history_data_price.status_code != 200:
        Error(regress_history_data_price.status_code)
    df = regress_history_data_price.json()
    df.reverse()
    labels = ['Date', 'Low', 'High', 'Open', 'Close', 'Volume']
    df = pd.DataFrame.from_records(df, columns=labels)
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df = df.set_index('Date')
    df = dropna(df)
    indicator_BOLLINGER = ta.volatility.BollingerBands(df['Close'], window=variable.indicator_BOLLINGER_window,window_dev=2,fillna=False)
    indicator_EMA = ta.trend.EMAIndicator(df['Close'], window=variable.indicator_EMA_window, fillna=False)
    indicator_RSI = ta.momentum.RSIIndicator(df['Close'], window=variable.indicator_RSI_window, fillna=False)
    indicator_CCI = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=variable.indicator_CCI_window, constant=0.015, fillna=False)
#   indicator_SMA = ta.trend.SMAIndicator(df['Close'], window=variable.indicator_SMA_window, fillna=False)
    serial_data = pd.DataFrame()
    serial_data = df
    serial_data['BOLLINGER_HBAND'] = indicator_BOLLINGER.bollinger_hband()
    serial_data['BOLLINGER_LBAND'] = indicator_BOLLINGER.bollinger_lband()
    serial_data['BOLLINGER_DELTA_SQUARE'] = np.nan
    serial_data['BOLLINGER_DELTA_Indicator'] = np.nan
    serial_data['EMA'] = indicator_EMA.ema_indicator()
#   serial_data['SMA'] = indicator_SMA.sma_indicator()
    serial_data['RSI'] = indicator_RSI.rsi()
    serial_data['rsi_overbought'] = [70.]*len(serial_data)
    serial_data['rsi_oversold'] = [30.]*len(serial_data)
    serial_data['CCI'] = indicator_CCI.cci()
    serial_data['UP_BOLLINGER_OUTSTANDING'] = np.nan
    serial_data['DOWN_BOLLINGER_OUTSTANDING'] = np.nan
    BOLLINGER_DELTA(variable.indicator_BOLLINGER_DELTA_window, serial_data)
    up_down_bollinger = BOLLINGER_OUTSTANDING_KLINE(serial_data)
    serial_data['UP_BOLLINGER_OUTSTANDING'] = up_down_bollinger[0]
    serial_data['DOWN_BOLLINGER_OUTSTANDING'] = up_down_bollinger[1]
    return(serial_data)


def buy_currency(id, currency, available_balance):
    order_id_list = []
    variable = import_file('./CoinBasePro_variable.py')
    in_hold_list = False
    current_ticker = requests.get(api_url + 'products/'+id+'/ticker', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if current_ticker.status_code != 200:
        Error(current_ticker.status_code)
    current_product = requests.get(api_url + 'products/'+id, headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if current_product.status_code != 200:
        Error(current_product.status_code)
    base_min_size = current_product.json()['base_min_size']
    last_trade_price = float(current_ticker.json()['price'])
    for item in current_property.json(): # When already hold this currency
        if currency == item['currency'] and float(item['balance']) > 0:
            currency_cost = calculate_cost(id)
            if currency_cost[0] != 0:
                in_hold_list = True
    exist_buy_order(id)
    if not in_hold_list:
        max_interval_serial_data = Serial_Data_Indicator(max([interval for interval in variable.Kline_dictionary.keys()]), variable.Kline_dictionary[max([interval for interval in variable.Kline_dictionary.keys()])], id)
        if max_interval_serial_data['BOLLINGER_DELTA_Indicator'].iloc[-1] ==  100 and max_interval_serial_data['Open'].iloc[-1] > max_interval_serial_data['EMA'].iloc[-1] and max_interval_serial_data['Close'].iloc[-1] > max_interval_serial_data['Open'].iloc[-1]:
            min_interval_serial_data = Serial_Data_Indicator(min([interval for interval in variable.Kline_dictionary.keys()]), variable.Kline_dictionary[min([interval for interval in variable.Kline_dictionary.keys()])], id)
            if min_interval_serial_data['Close'].iloc[-1]  < min_interval_serial_data['BOLLINGER_LBAND'].iloc[-1] and  min_interval_serial_data['Open'].iloc[-1] < min_interval_serial_data['BOLLINGER_LBAND'].iloc[-1] :
                print("  ---First buy---: ", id, file=open("order.txt", "a"))
                buy_size = round(available_balance*variable.Grid_Buy_Strategy[max([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]/last_trade_price/float(base_min_size), 0)*float(base_min_size)
                order = {
                        'size': buy_size,
                        'price': last_trade_price,
                        'side': 'buy',
                        'product_id': id,
                        }
                print(order, file=open("order.txt", "a"))
                request_order = requests.post(api_url + 'orders', json=order, headers=headers, auth=auth)
                time.sleep(variable.seconds_pause_request)
                if request_order.status_code != 200:
                    Error(request_order.status_code)
                print(json.dumps(request_order.json(), indent=4), file=open("order.txt", "a"))
                if variable.enable_TG :
                    send_tg_message(order)
                    send_tg_message(json.dumps(request_order.json(), indent=4))
                available_quote_currency(False)
                sell_currency(id)
    if in_hold_list:
        if variable.Buy_Sale_Policy_1:
            del variable.Grid_Buy_Strategy[max([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]
            print('            |_', id , "is in the HOLD LIST. Average cost is:", format(currency_cost[0], '.6f'), "Current Price is: ", format(last_trade_price, '.6f'),  " | ",  format((last_trade_price-currency_cost[0])/currency_cost[0]*100, '.2f'), "%", file=open(variable.output_file, "a"))
            for i in range(len(variable.Grid_Buy_Strategy.items())) :
                if last_trade_price <= currency_cost[0] * min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()]) :
                    buy_size = round(available_balance*variable.Grid_Buy_Strategy[min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]/last_trade_price/float(base_min_size), 0)*float(base_min_size)
                    order = {
                            'size': buy_size,
                            'price': last_trade_price,
                            'side': 'buy',
                            'product_id': id,
                            }
                    print(order, file=open("order.txt", "a"))
                    request_order = requests.post(api_url + 'orders', json=order, headers=headers, auth=auth)
                    time.sleep(variable.seconds_pause_request)
                    if request_order.status_code != 200:
                        Error(request_order.status_code)
                    print(json.dumps(request_order.json(), indent=4), file=open("order.txt", "a"))
                    if variable.enable_TG :
                        send_tg_message(order)
                        send_tg_message(json.dumps(request_order.json(), indent=4))
                    available_quote_currency(False)
                    cancel_sell_order(id)
                    sell_currency(id)
                    break
                else:
                    del variable.Grid_Buy_Strategy[min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]
        else:
            order_list = []
            done_orders = requests.get(api_url + 'orders?status=done&product_id='+id, headers=headers, auth=auth)
            time.sleep(variable.seconds_pause_request)
            if done_orders.status_code != 200:
                Error(done_orders.status_code)
            for _item in done_orders.json(): # Generate order_list
                if _item['side'] == 'sell' and _item['created_at'].split("T")[0] >= variable.order_start_date:
                    if _item['type'] == 'market':
                        order_list.append( [id, "sell", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
                    else:
                        order_list.append( [id, "sell", float(_item['filled_size']), float(_item['price'])] )
                elif _item['side'] == 'buy' and _item['created_at'].split("T")[0] >= variable.order_start_date:
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
            del variable.Grid_Buy_Strategy[max([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]
            print('            |_', id , "is in the HOLD LIST. Minimun buy price is:", format(min_price, '.6f'), "Current Price is: ", format(last_trade_price, '.6f'), " | ",  format((last_trade_price-min_price)/min_price*100, '.2f'), "%", file=open(variable.output_file, "a"))
            for i in range(len(variable.Grid_Buy_Strategy.items())) :
                if last_trade_price <= min_price * min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()]) :
                    buy_size = round(available_balance*variable.Grid_Buy_Strategy[min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])]/last_trade_price/float(base_min_size), 0)*float(base_min_size)
                    order = {
                            'size': buy_size,
                            'price': last_trade_price,
                            'side': 'buy',
                            'product_id': id,
                            }
                    print(order, file=open("order.txt", "a"))
                    request_order = requests.post(api_url + 'orders', json=order, headers=headers, auth=auth)
                    time.sleep(variable.seconds_pause_request)
                    if request_order.status_code != 200:
                        Error(request_order.status_code)
                    print(json.dumps(request_order.json(), indent=4), file=open("order.txt", "a"))
                    if variable.enable_TG :
                        send_tg_message(order)
                        send_tg_message(json.dumps(request_order.json(), indent=4))
                    available_quote_currency(False)
                    break
                else:
                    del variable.Grid_Buy_Strategy[min([price_percent for price_percent in variable.Grid_Buy_Strategy.keys()])] 


def sell_currency(id):
    variable = import_file('./CoinBasePro_variable.py')
    trailing_stop_price = 0
    currency_cost = calculate_cost(id)
    remain_size = float(format(float(currency_cost[1]), '.6f'))
    current_ticker = requests.get(api_url + 'products/'+id+'/ticker', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if current_ticker.status_code != 200:
        Error(current_ticker.status_code)
    current_product = requests.get(api_url + 'products/'+id, headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if current_product.status_code != 200:
        Error(current_product.status_code)
    base_min_size = current_product.json()['base_min_size']
    symbol_kline_data = Serial_Data_Indicator(max([interval for interval in variable.Kline_dictionary.keys()]), variable.Kline_dictionary[max([interval for interval in variable.Kline_dictionary.keys()])], id)
    last_trade_price = float(current_ticker.json()['price'])
    if variable.Buy_Sale_Policy_1: #方案一预挂卖单
        for i in range(len(variable.Grid_Sell_Strategy.items())) :
            if i == (len(variable.Grid_Sell_Strategy.items()) -1):
                sell_size = round(remain_size,abs(decimal.Decimal(current_product.json()['quote_increment']).as_tuple().exponent))
            else:
                sell_size = float(Decimal(round(currency_cost[1] * list(variable.Grid_Sell_Strategy.values())[i]/float(base_min_size), 0))*Decimal(base_min_size))
                remain_size -= sell_size
            if sell_size != 0:
                sell_price = float(Decimal(round(currency_cost[0] *  list(variable.Grid_Sell_Strategy.keys())[i]/float(current_product.json()['quote_increment']),0)) * Decimal(current_product.json()['quote_increment']))
                order = {
                        'size': sell_size,
                        'price': sell_price,
                        'side': 'sell',
                        'product_id': id,
                        }
                print('方案一预挂单', file=open("order.txt", "a"))
                print(order, file=open("order.txt", "a"))
                request_order = requests.post(api_url + 'orders', json=order, headers=headers, auth=auth)
                time.sleep(variable.seconds_pause_request)
                if request_order.status_code != 200:
                    Error(request_order.status_code)
                print(json.dumps(request_order.json(), indent=4), file=open("order.txt", "a"))
#                if variable.enable_TG :
#                    send_tg_message('方案一预挂单')
#                    send_tg_message(order)
#                    send_tg_message(json.dumps(request_order.json(), indent=4))
    else:
        if last_trade_price >= currency_cost[0] * variable.profit_rate :
            cancel_sell_order(id) #清理方案一的预挂卖单
            max_value, max_index = max((row, i) for i, row in enumerate(symbol_kline_data['High'].loc[currency_cost[3]:datetime.utcfromtimestamp(float(time.time())).__format__('%Y-%m-%d')]))
            trailing_stop_price = variable.trailing_stop_rate * max_value + (1-variable.trailing_stop_rate) * currency_cost[0]
            if last_trade_price <= trailing_stop_price:
                sell_size = currency_cost[1]
                order = {
                        'size': sell_size,
                        'price': last_trade_price,
                        'side': 'sell',
                        'product_id': id,
                        }
                print(order, 'Trailing Stop Price: ', trailing_stop_price, file=open("order.txt", "a"))
                request_order = requests.post(api_url + 'orders', json=order, headers=headers, auth=auth)
                time.sleep(variable.seconds_pause_request)
                if request_order.status_code != 200:
                    Error(request_order.status_code)
                print(json.dumps(request_order.json(), indent=4), file=open("order.txt", "a"))
                if variable.enable_TG :
                    send_tg_message(order)
                    send_tg_message(json.dumps(request_order.json(), indent=4))


def exist_buy_order(symbol):
    open_orders = requests.get(api_url + 'orders?status=open', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if open_orders.status_code != 200:
        Error(open_orders.status_code)
    for item in open_orders.json():
        if item['product_id'] == symbol and item['side'] == 'buy' and last_trade_price < item['price'] :
            cancel_order = requests.delete(api_url + 'orders/'+item['id'], headers=headers, auth=auth)
            time.sleep(variable.seconds_pause_request)
            if cancel_order.status_code != 200:
                Error(cancel_order.status_code)    


def cancel_sell_order(symbol):
    open_orders = requests.get(api_url + 'orders?status=open', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if open_orders.status_code != 200:
        Error(open_orders.status_code)
    for item in open_orders.json():
        if item['product_id'] == symbol and item['side'] == 'sell' :
            cancel_order = requests.delete(api_url + 'orders/'+item['id'], headers=headers, auth=auth)
            time.sleep(variable.seconds_pause_request)
            if cancel_order.status_code != 200:
                Error(cancel_order.status_code)


def send_tg_message(message):
    for chat_id in variable.chat_id:
        response = requests.get(TG_URL + "sendMessage?text={}&chat_id={}".format(message, chat_id))


def send_tg_image(plot):
    for chat_id in variable.chat_id:
        files = {'photo': open(plot, 'rb')}
        requests.post(TG_URL + "sendPhoto?chat_id={}".format(chat_id), files=files)


#api_url = 'https://api.pro.coinbase.com/'
api_url = 'https://api.exchange.coinbase.com/'
headers = {"Accept": "application/json"}
while True:
    variable = import_file('./CoinBasePro_variable.py')
    TG_URL = "https://api.telegram.org/bot{}/".format(variable.TOKEN)
    auth = CoinbaseExchangeAuth(variable.api_key, variable.secret_key, variable.passphrase)
    global order_list, products_list, min_max_list, coinbase_products
    order_list = []
    products_list = []
    min_max_list = []
    print('===========================================', file=open(variable.output_file, "a"))
    print('|       July 14,2022   Version: 5.7       |', file=open(variable.output_file, "a"))
    print('|          Copyright © - 2022             |', file=open(variable.output_file, "a"))
    print('===========================================', file=open(variable.output_file, "a"))
    print('Current UTC Time: ', datetime.utcfromtimestamp(float(time.time())).__format__('%Y-%m-%d %H:%M:%S'), file=open(variable.output_file, "a"))
    print("Current Local Time(" + variable.time_zone + "): ", datetime.utcfromtimestamp(float(time.time())+variable.seconds_UTC2local).__format__('%Y-%m-%d %H:%M:%S'), file=open(variable.output_file, "a"))
    coinbase_products = requests.get(api_url+'products', headers=headers, auth=auth)
    time.sleep(variable.seconds_pause_request)
    if coinbase_products.status_code != 200:
        Error(coinbase_products.status_code)
    if len(variable.include_symbol) != 0:
        for _item in variable.include_symbol:
            products_list.append(_item)
    else:
        for _item in coinbase_products.json():
            if (_item['id'] not in variable.exclude_symbol) and (_item['status_message'] == "") and (_item['quote_currency'] in variable.quote_currency):
                products_list.append(_item['id'])
    get_current_property()
    for item in current_property.json():
        for _item in variable.quote_currency:
            id = item['currency'] + "-" + _item
            if id in products_list:
                interval = max([interval for interval in variable.Kline_dictionary.keys()])
                limit = variable.Kline_dictionary[max([interval for interval in variable.Kline_dictionary.keys()])]
#               for interval, limit in variable.Kline_dictionary.items():
                min_max_price(interval, limit, id)
                for i in range(len(quote_currency_list)):
                    if (quote_currency_list[i][0] == _item) and (float(quote_currency_list[i][4]) >= float(variable.quote_lower_limit[_item])):
                        available_balance = quote_currency_list[i][3]
                        buy_currency(id, item['currency'], available_balance)
                    elif (quote_currency_list[i][0] == _item) and (float(quote_currency_list[i][4]) < float(variable.quote_lower_limit[_item])):
                        currency_cost = calculate_cost(id)
                        if currency_cost[0] != 0:
                            current_ticker = requests.get(api_url + 'products/'+id+'/ticker', headers=headers, auth=auth)
                            if current_ticker.status_code != 200:
                                Error(current_ticker.status_code)
                            last_trade_price = float(current_ticker.json()['price'])
                            if variable.Buy_Sale_Policy_1:
                                print('            |_', id , "is in the HOLD LIST. Average cost is:", format(currency_cost[0], '.6f'), "Current Price is: ", format(last_trade_price, '.6f'),  " | ",  format((last_trade_price-currency_cost[0])/currency_cost[0]*100, '.2f'), "%", file=open(variable.output_file, "a"))
                                open_orders = requests.get(api_url + 'orders?status=open', headers=headers, auth=auth)
                                time.sleep(variable.seconds_pause_request)
                                if open_orders.status_code != 200:
                                    Error(open_orders.status_code)
                                for symbol in open_orders.json():
                                    if symbol['product_id'] == id and symbol['side'] == 'sell' :
                                        exist_sell_order = True
                                        break
                                    else:
                                        exist_sell_order = False
                                if not exist_sell_order:        
                                    sell_currency(id)
                            else:
                                order_list = []
                                done_orders = requests.get(api_url + 'orders?status=done&product_id='+id, headers=headers, auth=auth)
                                time.sleep(variable.seconds_pause_request)
                                if done_orders.status_code != 200:
                                    Error(done_orders.status_code)
                                for _item in done_orders.json(): # Generate order_list
                                    if _item['side'] == 'sell' and _item['created_at'].split("T")[0] >= variable.order_start_date:
                                        if _item['type'] == 'market':
                                            order_list.append( [id, "sell", float(_item['filled_size']), float(_item['executed_value'])/float(_item['filled_size'])] )
                                        else:
                                            order_list.append( [id, "sell", float(_item['filled_size']), float(_item['price'])] )
                                    elif _item['side'] == 'buy' and _item['created_at'].split("T")[0] >= variable.order_start_date:
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
                                print('            |_', id , "is in the HOLD LIST. Minimun buy price is:", format(min_price, '.6f'), "Current Price is: ", format(last_trade_price, '.6f'), " | ",  format((last_trade_price-min_price)/min_price*100, '.2f'), "%", file=open(variable.output_file, "a"))
    print('--------------------------------------------------------------------------------------------------------------------------------------------', file=open(variable.output_file, "a"))

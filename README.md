# **WARNING! This software will not be maintained any more. So please be very careful if you want to use it on CoinBase or CoinBase Pro.**
# **CoinBase is very very very sucks! Don't use their service, because you will never get any reply from a people, and they will never resolve your issue.**
=========================================================================

I'm developing a new program which will work on Binance.

<!--
# CoinBasePro Trading Bot
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

CoinBasePro Trading Bot can trade cryptocurrencies automatically by using CoinBasePro API.

### *If you think this program is helpful, please give me a star ⭐. If you have any thoughs or advices then submit an Issue or send me an e-mail.*
:arrow_right:

<img src="/screenshot/01.jpg">

## Disclaimer
This project is for informational purposes only. You should not construe any such information or other material as legal, tax, investment, financial, or other advice. Nothing contained here constitutes a solicitation, recommendation, endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the securities laws of such jurisdiction.

If you plan to use real money, USE AT YOUR OWN RISK.

Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs, or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.

# THERE IS NO "STOP LOSS" SETTING IN THIS PROGRAM. IF YOU ARE TRADING USING LEVERAGE YOU MAY LOSE ALL YOUR MONEY WHEN THE MARKET IS OSCILLATING.

## Test results:
    Windows10 + Python3.9.1  |  passed
    Linux + Python3.8.5      |  passed
------------------------------------------------------------------------

## CoinBase Pro Setup

-  Create a [CoinBase account](https://www.coinbase.com/join/ban_c) (Includes my referral link, I'll be super grateful if you use it).
-  Enable Two-factor Authentication.
-  Go to [pro.coinbase.com](https://pro.coinbase.com) to generate a new API key in the CoinBase Pro "API SETTINGS" page. Recommend to only generate "View/Trade" permissions API KEY and use the "IP Whitelist" to block all unauthorised access.
-  Buy or Send cryptocurrencies into your account. If you are in Canada, CoinBase doesn't support buy cryptocurrencies from your bank accounts very well. So you can use [shakepay.com](https://shakepay.me/r/ZMLG4KJ) or [bitbuy.ca](https://bitbuy.ca/sign-up?c=G72SCTTHK) (Includes my referral link, I'll be super grateful if you use it).
-  Recommended only to send BTC, USDC, ETH, USDT, DAI into your account. Because in this program all these 5 cryptocurrencies can be defined as anchor cryptocurrencies. If you send other cryptocurrencies into your account but without history orders, so the program can't sell it because of no cost. 


## Linux environment
- Start program
```
$nohup ./startCBP.sh >/dev/null 2>&1 & echo $! > run.pid
$tail -f output.txt
```
- Stop program
```
$./stopCBP.sh
```


## variable.py
```
#Initial Parameters
import ctypes
import os
api_key = ''
secret_key = ''
passphrase = ''
if os.name == 'nt':
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
Long_Term_Indicator_days = 300
Long_Term_Indicator_days_granularity = 86400 #{60, 300, 900, 3600, 21600, 86400}
Short_Term_Indicator_days = 1
Short_Term_Indicator_days_granularity = 300 #{60, 300, 900, 3600, 21600, 86400}
seconds_UTC2local = -25200
profit_rate = 1.10
skip_indicator_profit_rate = 1.50
seconds_pause_request = 0.5
seconds_cancel_order = 60
first_buy_percent = 0.10
second_buy_percent = 0.20
third_buy_percent = 0.30
quote_currency = ["BTC","USDC","ETH","USDT"]
quote_lower_limit = {'BTC':100, 'USDC':100, 'ETH':10, 'USDT':10}
exclude_currency = ["XRP-BTC","DAI-USDC","WBTC-BTC"] # "exclude_currency" and "include_currency" only one can have items or both empty
include_currency = [] # "exclude_currency" and "include_currency" only one can have items or both empty
output_data_file = 'output_data.txt'
close_plot_second = 5 # "0" will not show the plot, just use for generate data
order_start_date = '2021-02-01'
min_history_data = 30 # new cryptocurrency involved into CoinBase without enoough data may cause the indicators error. use this parameter to skip those new cryptocurrencies.
```

-  api_key - CoinBase Pro API key generated in the CoinBase Pro API SETTINGS page. Recommend to only generate "View/Trade" permissions API KEY and use the "IP Whitelist" to block all unauthorised access.
-  secret_key - CoinBase Pro secret key generated in the CoinBase Pro API SETTINGS page.
-  passphrase - CoinBase Pro passphrase generated in the CoinBase Pro API SETTINGS page.
-  screen_width and screen_height - only used for [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator)
-  Long_Term_Indicator_days - The maximum number is 300, CoinBase only supply 300 records. if "granularity" is 86400 then CoinBase will return 300 days data.
-  Long_Term_Indicator_days_granularity - 86400 is 1 day, 21600 is 6 hours, 3600 is 1 hour, 900 is 15 minutes, 300 is 5 minutes, 60 is 1 minute.
-  Short_Term_Indicator_days - The maximum number is 300, CoinBase only supply 300 records. if "granularity" is 300 then CoinBase will return 1 days and 1 hour data.
-  Short_Term_Indicator_days_granularity - 86400 is 1 day, 21600 is 6 hours, 3600 is 1 hour, 900 is 15 minutes, 300 is 5 minutes, 60 is 1 minute.
-  seconds_UTC2local - Seconds between your local time and UTC.
-  profit_rate - Define how much you want to earn, if buy price is $10, then when the price is "greater than or equal to" $11 the sell action will be triggered.
-  skip_indicator_profit_rate - Define the profit percent that skip the indicators condition and sell directly.
-  seconds_pause_request - Custom the sleep time after each requests, less than 0.5 may exceed API rate limits.
-  seconds_cancel_order - If Transaction doesn't match after seconds the order will be cancelled.
-  first_buy_percent - The percent of money when buy a cryptocurrency at first time. Calculate by USDC.
-  second_buy_percent - The percent of money when buy a cryptocurrency at second time. Calculate by USDC.
-  third_buy_percent - The percent of money when buy a cryptocurrency at third time. Calculate by USDC.
-  quote_currency - Define anchor cryptocurrencies, current CoinBase Pro support BTC, USDT, USDC, DAI, ETH
-  quote_lower_limit - Define how much anchor cryptocurrencies your want to keep in account and don't want to input into Transaction. Calculate by USDC
-  exclude_currency - The cryptocurrencies you don't want to trade such as stablecoins.
-  include_currency - The cryptocurrencies you want to trade. If it is blank, the cryptocurrency products are depend on CoinBase. 
-  output_data_file - only used for [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator). Export indicators into this file.
-  close_plot_second - only used for [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator).
-  order_start_date - The start date you want the program to grab history orders.
-  min_history_data - New cryptocurrency involved into CoinBase without enoough data may cause the indicators error. use this parameter to skip those new cryptocurrencies.

## Buy Condition
-  First Buy
( (5 minutes "Green Candle" and 'Close' price less than 'BOLLINGER_LBAND') OR (5 minutes "Red Candle" and 'Open' price less than 'BOLLINGER_LBAND') )AND (5 minutes 'CCI' less than -100) AND ( 1 day 'Low' price less than 'BOLLINGER_LBAND')
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100 and long_term_simulation_data['Low'].iloc[-1] < long_term_simulation_data['BOLLINGER_LBAND'].iloc[-1]:
```

-  Second Buy
(Current Price less than minum buy order price * 0.8) AND 
( (5 minutes "Green Candle" and 'Close' price less than 'BOLLINGER_LBAND') OR (5 minutes "Red Candle" and 'Open' price less than 'BOLLINGER_LBAND') )AND (5 minutes 'CCI' less than -100)
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
```

-  Third Buy
(Current Price less than minum buy order price * 0.7) AND 
( (5 minutes "Green Candle" and 'Close' price less than 'BOLLINGER_LBAND') OR (5 minutes "Red Candle" and 'Open' price less than 'BOLLINGER_LBAND') )AND (5 minutes 'CCI' less than -100)
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
```


## Sell Condition
- (current price is grater than the cost * 1.1) AND (5 minutes 'CCI' is greater than 100) AND (1 day 'Close' is grater than 'BOLLINGER_HBAND') AND (cryptocurrency size is not ZERO)
```
if float(last_trade_price) > currency_cost[0]*profit_rate and short_term_simulation_data['CCI'].iloc[-1] > 100 and long_term_simulation_data['Close'].iloc[-1] > long_term_simulation_data['BOLLINGER_HBAND'].iloc[-1] and currency_cost[1] != 0:
```

### You also can build your own trade conditions and use [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator) to do the simulate. I'm still trying to figure out how to easyly create trade conditions and share between [CoinBasePro_Trading_Bot](https://github.com/banhao/coinbasepro-Trading-Bot) and [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator)


## Support the Project
If this program helped you to earn money from cryptocurrency market, I'll be appreciate if you can use the following link to buy me a cup of coffee, Thanks! 

<a href="https://www.buymeacoffee.com/haoban" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

[PayPal.Me](https://paypal.me/HAOBAN99?locale.x=en_US)
-->

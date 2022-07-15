# **警告！此软件已不再维护。所以，如果你想在CoinBase或CoinBase Pro使用它，请务必小心使用。**
# **本版本为最终版本5.7**
========================================================================================

基于Binance的机器人请参见：https://twitter.com/CC_Tradingchart

<!--
# CoinBasePro Trading Bot
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

CoinBasePro Trading Bot 通过使用CoinBasePro API来进行加密货币的自动交易.

### *如果你觉得这个程序对你有帮助，请给个点赞 ⭐。 如果你有任何的想法或者建议请提交issues或者给我发邮件。*
:arrow_right:

<img src="/screenshot/01.jpg">

## 免责申明
本项目仅供参考。你不应将任何此类信息或其他材料解释为法律、税务、投资、财务或其他建议。此处包含的任何内容均不构成我或任何第三方服务提供商在本或任何其他司法管辖区购买或出售任何证券或其他金融工具的招揽、推荐、背书或要约，根据证券，此类招揽或要约在该司法管辖区是非法的此类司法管辖区的法律。

如果你打算使用真钱，请自行承担风险。

在任何情况下，本人都不以任何方式对任何索赔、损害、损失、费用、成本或责任承担任何责任，包括但不限于任何直接或间接的利润损失损害。

# 本程序没有设置“止损”功能。 如果你使用杠杆那么在市场震荡情况下你有可能损失你所有的钱。

## 测试结果:
    Windows10 + Python3.9.1  |  passed
    Linux + Python3.8.5      |  passed
------------------------------------------------------------------------

## CoinBase Pro 设置

-  创建一个CoinBase账户 [CoinBase account](https://www.coinbase.com/join/ban_c) (链接中包含了我的推荐信息，如果你能使用该链接注册，我将不胜感谢).
-  启用双因素认证。
-  进入到 [pro.coinbase.com](https://pro.coinbase.com) 进入到CoinBase Pro 的 "API SETTINGS" 页面来创建一个新的API KEY。强烈建议只生成具有”只读/交易“权限的API KEY并启用 "IP Whitelist" 来阻止未授权的访问。
-  购买或转入加密货币到你的账户里。 如果你居住在加拿大CoinBase对通过使用银行账户购买加密货币的支持不太友好。你可以通过使用[shakepay.com](https://shakepay.me/r/ZMLG4KJ) 或者 [bitbuy.ca](https://bitbuy.ca/sign-up?c=G72SCTTHK) (链接中包含了我的推荐信息，如果你能使用该链接注册，我将不胜感谢).
-  建议只转入BTC, USDC, ETH, USDT, DAI到你的账户里，因为这5种加密货币是锚定货币。如果你转入其他的加密货币由于缺少历史交易记录，程序会因为无法计算出成本而无法进行买卖交易。 


## Linux 环境下的程序启动
- 启动程序
```
$nohup ./startCBP.sh >/dev/null 2>&1 & echo $! > run.pid
$tail -f output.txt
```
- 停止程序
```
$./stopCBP.sh
```


## 对variable.py中各个参数的说明
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

-  api_key - 请填入你自己的 CoinBase Pro API key.
-  secret_key - 请填入你自己的 CoinBase Pro secret key.
-  passphrase - 请填入你自己的 CoinBase Pro passphrase.
-  screen_width and screen_height - 该参数只被用在本人的另外一个程序中 [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator)
-  Long_Term_Indicator_days - CoinBase的API每次调用最大只能返回300个数据，如果颗粒度"granularity" 设置为86400秒也就是一天，那么就是返回300天的数据。
-  Long_Term_Indicator_days_granularity - 颗粒度86400秒就是一天, 21600秒就是6小时, 3600秒就是1小时, 900秒就是15分钟, 300秒就是5分钟, 60秒就是1分钟。
-  Short_Term_Indicator_days - CoinBase的API每次调用最大只能返回300个数据，如果颗粒度"granularity" 设置为300秒也就是5分钟，那么就是返回1天1小时的数据。
-  Short_Term_Indicator_days_granularity - 颗粒度86400秒就是一天, 21600秒就是6小时, 3600秒就是1小时, 900秒就是15分钟, 300秒就是5分钟, 60秒就是1分钟。
-  seconds_UTC2local - 本地时间和UTC之间的时差需要换算成秒。
-  profit_rate - 定义最低利润率，默认是10%。当前价格达到了成本价格的1.1倍后，如果还满足技术指标条件那么卖出条件就达成程序会自动卖出相应的加密货币。也就是说最低利润能确保10%。
-  skip_indicator_profit_rate - 定义屏蔽技术指标的利润率，默认是50%。当前价格达到了成本价格的1.5倍后，无论是否满足技术指标，程序都会启动全部卖出相应的加密货币。
-  seconds_pause_request - 定义每次调用API后的停顿时间, 由于受到API调用次数频度的限制，如果停顿少于0.5秒有可能触发API调用限制。
-  seconds_cancel_order - 如果交易在设定的时间之内没有匹配交易成功那么该笔交易将会被取消。
-  first_buy_percent - 初次购买，当买入条件满足时使用多少的资金买入加密货币，默认设定为10%，资金按照换算成USDC计算。
-  second_buy_percent - 第二次购买，当买入条件满足时使用多少的资金买入加密货币，默认设定为20%，资金按照换算成USDC计算。
-  third_buy_percent - 第三次购买，当买入条件满足时使用多少的资金买入加密货币，默认设定为30%，资金按照换算成USDC计算。
-  quote_currency - 锚定货币设定，目前CoinBase Pro支持BTC, USDT, USDC, DAI, ETH等5种货币为锚定货币。
-  quote_lower_limit - 设定锚定货币最低资金限额，当达到该限额后买入行为将会停止，资金按照换算成USDC计算。假如你有相当于1000USDC的比特币在账户里，当设定限额为500时，当卖出比特币买入其他加密货币后，比特币的余额小于500USDC时，将不会再有任何卖出比特币买入其他加密货币的交易行为。此参数的目的是为了当有需要保留一部分锚定货币做长期投资打算，而不打算用来做货币对交易时使用。
-  exclude_currency - 排除的交易货币对，例如某些稳定币
-  include_currency - 限定只交易某些货币对。如果空白，交易货币对将会是CoinBase所支持的所有货币对。 
-  output_data_file - 数据输出文件，该参数只被用在本人的另外一个程序中 [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator)。
-  close_plot_second - 该参数只被用在本人的另外一个程序中 [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator).
-  order_start_date - 获取历史交易开始时间。长时间交易后会形成很长的交易记录，本程序根据交易记录自动生成成本价格，如果交易历史记录过长会导致程序计算时间变长，通过该参数可以屏蔽掉太久远的交易记录。
-  min_history_data - 新引入的加密货币由于缺少足够的历史数据，会引发指标出现错误。该参数设置默认为30天，确保新引入的加密货币有足够天数的数据后可正常生成各个技术指标。

## 买入条件

-  初次买入条件

(短期交易指标（默认为5分钟线）为阳线并且收盘价位于布林线下行线的下方 或者 短期交易指标（默认为5分钟线）为阴线并且开盘价位于布林线下行线的下方) 并且  短期交易指标（默认为5分钟线）CCI小于-100 并且 长期交易指标（默认为1天线）最低价位于布林线下行线的下方
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100 and long_term_simulation_data['Low'].iloc[-1] < long_term_simulation_data['BOLLINGER_LBAND'].iloc[-1]:
```

-  第二次买入条件
 
(当前价格低于历史成交买入最低交易价格的80%) 并且 (短期交易指标（默认为5分钟线）为阳线并且收盘价位于布林线下行线的下方 或者 短期交易指标（默认为5分钟线）为阴线并且开盘价位于布林线下行线的下方) 并且 短期交易指标（默认为5分钟线）CCI小于-100 
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
```

-  第三次买入条件

(当前价格低于历史成交买入最低交易价格的70%) 并且 (短期交易指标（默认为5分钟线）为阳线并且收盘价位于布林线下行线的下方 或者 短期交易指标（默认为5分钟线）为阴线并且开盘价位于布林线下行线的下方) 并且 短期交易指标（默认为5分钟线）CCI小于-100
```
if ((short_term_simulation_data['Close'].iloc[-1] > short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])or (short_term_simulation_data['Close'].iloc[-1] < short_term_simulation_data['Open'].iloc[-1] and short_term_simulation_data['Open'].iloc[-1] < short_term_simulation_data['BOLLINGER_LBAND'].iloc[-1])) and short_term_simulation_data['CCI'].iloc[-1] < -100:
```


## 卖出条件
- (当前价格达到成本价的1.1倍 并且 短期交易指标（默认为5分钟线）CCI大于100 并且 长期交易指标（默认为1天线）收盘价位于布林线上行线的上方) 或者 (当前价格达到成本价的1.5倍)并且 货币余额大于零 
```
if (( float(last_trade_price) > currency_cost[0]*profit_rate and short_term_simulation_data['CCI'].iloc[-1] > 100 and long_term_simulation_data['Close'].iloc[-1] > long_term_simulation_data['BOLLINGER_HBAND'].iloc[-1] ) or ( float(last_trade_price) > currency_cost[0]*skip_indicator_profit_rate )) and currency_cost[1] != 0
```

### 你也可以定制你自己的交易条件并通过使用我的另一个程序 [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator) 来进行仿真验证。 目前我仍然在研究如果能方便的设置交易条件并且可在两个程序 [CoinBasePro_Trading_Bot](https://github.com/banhao/coinbasepro-Trading-Bot) 间 [CoinBasePro Trading Simulator](https://github.com/banhao/CoinBasePro-Trading-Simulator) 共享


## 支持本项目
如果你觉得本程序能帮助你在加密货币市场中挣到钱，如能通过下面的链接帮我买一杯咖啡，我将非常感谢！

<a href="https://www.buymeacoffee.com/haoban" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

[PayPal.Me](https://paypal.me/HAOBAN99?locale.x=en_US)
-->

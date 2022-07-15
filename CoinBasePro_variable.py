#Plot Window Configuration
import ctypes
import os
if os.name == 'nt':
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    
#CoinBase Pro API Configuration
api_key = ''
secret_key = ''
passphrase = ''

#Symbol Monitor List
quote_currency = ["BTC", "ETH", "USDT"]
quote_lower_limit = {'BTC':50, 'ETH':50, 'USDT':50}
exclude_symbol = ["XRP-BTC","DAI-USDC","WBTC-BTC","ICP-USDT","ICP-BTC","FIL-BTC"] # "exclude_currency" and "include_currency" only one can have items or both empty
include_symbol = [] # "exclude_currency" and "include_currency" only one can have items or both empty

#General Configuration
seconds_pause_request = 3
Kline_dictionary = { 86400:300, 21600:300, 3600:300, 900:300, 300:300, 60:300 } #{60, 300, 900, 3600, 21600, 86400}
time_zone = "CST"
seconds_UTC2local = -21600
output_file = 'output.txt'
order_start_date = '2021-02-01'

#Profit & Loss Rate Configuration
#目前支持使用两种不同的买卖策略。 #方案一. 根据持仓成本进行二买三买甚至四买，从而拉低平均成本。卖出则根据成本计算利润进行一卖二卖三卖。均在Grid_Buy_Strategy和Grid_Sell_Strategy中定义。
                               #方案二. 根据多次买入时的最低价进行后续的三买四买，卖出则采用动态跟随的方式，依据最高点价格计算卖出价格后在达到后一次性卖出全部持仓数量。在profit_rate，trailing_stop_rate和Grid_Buy_Strategy中定义。
Buy_Sale_Policy_1 = True
profit_rate = 1.3
trailing_stop_rate = 0.786
Grid_Buy_Strategy = { 1:0.5, 0.80:0.25, 0.50:1 }  #{ 1:0.5 first buy 50 percent fund, 0.80:0.25 lower than 0.80 buy 25 percent fund, 0.50:1 lower than 0.50 buy 100 percent fund }
Grid_Sell_Strategy = { 1.3:0.2, 1.5:0.4, 1.7:0.4 } #{ 1.3:0.2 30% profit sell 20 percent, 1.5:0.4 50% profit sell 40 percent, 1.7:0.5 70% profit sell 40% }

#Indicatro Settings
indicator_BOLLINGER_window = 21
indicator_EMA_window = 21
indicator_RSI_window = 14
indicator_CCI_window = 21
indicator_SMA_window = 200
indicator_BOLLINGER_DELTA_window = 7

#Telgram Configuration
enable_TG = False
TOKEN = ""
USERNAME_BOT = ""
chat_id = [""]

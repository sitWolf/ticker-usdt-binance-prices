#! python3
# gbp.py - Get Binance SYMBOL/USDT Prices

# On OS X, the shebang line is #! /usr/bin/env python3
# On Linux, the shebang line is #! /usr/bin/python3
# For windows users add also make sure that python.exe to your path environmental variables

# As long as this text is visible: this code has not been tested nor cleaned!

import os
import pytz
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

import numpy as np
import urllib
import datetime as dt

from binance.client import Client
from datetime import timedelta, timezone
from mpl_finance import candlestick_ohlc

import time, sys

import itertools
import threading
import time
import sys

__author__ = 'Petronia'

# Use at your own risk!

# This script plots the Open, High, Low, Close (OHLC) Candlestick Chart for USDT prices of a crypto ticker (symbol).
# It is linked to binance data. In binance you get the price against a market (e.g. BTC, BNB)
# and not USDT.
# The market is linked to USDT, so conversion is required if you want the USDT OHLC candlestick chart
# of a symbol.
# The purpose of this script is to plot a graph that depicts the true gain in price of a symbol.
# Because finally, changes in a USDT market such as BTC affect the true price of a ticker againts a market.

# Generate an API Key and assign relevant permissions at https://www.binance.com/userCenter/createApi.html
# Never share this information with anybody.


print("warning: use at your own risk!".upper())
print('''This script plots the Open, High, Low, Close (OHLC)
    Candlestick Chart against USDT prices of
    a crypto ticker (symbol)''')

# Only required if you want to hook your funds to the prices.
api_key = ""
api_secret = ""

# Connect to binance
done = False

def connecting():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rConnecting to Binance... ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\nDONE\n')

t = threading.Thread(target=connecting)
t.start()

#long process here
client = Client(api_key, api_secret)

done = True

time.sleep(1) # Else, the below will query the use to soon mixing up text

def query_user():
    user_symbol = input("\nEnter symbol e.g. ETH, NEBL, TRX:\n> ").upper()
    user_market = input("Enter market e.g. ETH, BNB [BTC]:\n> ").upper() or "BTC"
    return user_symbol + user_market, user_symbol + "/" + user_market, user_market+"USDT"

def check_user_input():
    prices = client.get_all_tickers()
    for item in prices:
        if user_query in item['symbol']:
            return True
    return False

user_query = ""
if not user_query:
    user_query, query_label, user_market = query_user()
    while check_user_input() == False:
        print("{} is not a binance valid ticker. Please try again".format(user_query))
        
        user_query, query_label, user_market = query_user()

std_text = "Same as binance"

options ={1:{"description": "1m", "time_slice":2, "comment": "Limited to 1 day of data", "code": Client.KLINE_INTERVAL_1MINUTE, "width": 0.0005},
          2:{"description": "5m", "time_slice":2, "comment": "Limited 2 days of data", "code": Client.KLINE_INTERVAL_5MINUTE, "width": 0.0005},
          3:{"description": "15m", "time_slice":2, "comment": "Limited 3 day of data", "code": Client.KLINE_INTERVAL_15MINUTE, "width": 0.005},
          4:{"description": "30m", "time_slice":1, "comment": "Same as binance", "code": Client.KLINE_INTERVAL_30MINUTE, "width": 0.01},
          5:{"description": "1h", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_1HOUR, "width": 0.01},
          6:{"description": "2h", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_2HOUR, "width": 0.01},
          7:{"description": "4h", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_4HOUR, "width": 0.01},
          8:{"description": "6h", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_6HOUR, "width": 0.01},
          9:{"description": "12h", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_12HOUR, "width": 0.01},
          10:{"description": "1D", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_1DAY, "width": 0.5},
          11:{"description": "1W", "time_slice":1, "comment": std_text, "code": Client.KLINE_INTERVAL_1WEEK, "width": 1},
          }

# Choose interval
def query_user_for_interval():
    user_interval = 0
    print("Time Interval Options")
    for k, v in options.items():
        opt = "[" + str(k) + "] "
        opt_formatted = "{:{align}{width}}".format(opt, align='<', width='6')
        opt_text = opt_formatted + "{:{align}{width}}".format(v["description"], align='>', width='3')
        print (opt_text)

    while not 0 < user_interval < 12:
        try:
            user_interval = int(input("Enter interval corresponding number (e.g. 3 for 15 minutes):\n> "))
            if not 0 < user_interval < 12:
                print("{} is not a valid input". format(user_interval))
                continue
        except ValueError:
            print("Invalid input")
            continue
        else:
            break
    return user_interval

user_interval = query_user_for_interval()

# Low interval requires graphical changes
def return_code_interval(interval):
    return options[interval]["code"]

def return_interval_slice(interval):
    return options[interval]["time_slice"]

def return_candle_width(interval):
    return options[interval]["width"]
    
candles = client.get_klines(symbol=user_query, interval=return_code_interval(user_interval))
candles_market = client.get_klines(symbol=user_market, interval=return_code_interval(user_interval))

# Data format (list of list)
'''
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore
  ]
]
'''
   
usdt_stock_data = []
usdt_stock_data.append("Datetime,Open,High,Low,Close")


data_points_sliced_at = int(len(candles) / return_interval_slice(user_interval))

for r, item in enumerate(candles[-data_points_sliced_at:]):
    string = ""
    for c, dot in enumerate(item[:5], 0): # strip and leave only the open time and OHLC
        if c == 0:
            stamp_datetime = datetime.datetime.fromtimestamp(int(dot)/1000).strftime('%Y-%m-%d %H:%M:%S') # %H:%M:%S
            string += str(stamp_datetime) + ","
        elif 1 <= c < 4:
            usdt_price = float(dot) * float(candles_market[r][c])
            string += str(usdt_price) + ","
        else:
            usdt_price = float(dot) * float(candles_market[r][c])
            string += str(usdt_price)
    usdt_stock_data.append(string)

def bytespdate2num(fmt, encoding='utf-8'):
    strconverter = mdates.strpdate2num(fmt)
    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)
    return bytesconverter
    
def graph_data(stock):

    fig = plt.figure()
    ax1 = plt.subplot2grid((1,1), (0,0))
    
    # Datetime, Open, High, Low, Close
    date, openp, highp, lowp, closep = np.loadtxt(usdt_stock_data[1:],
                                                      delimiter=',',
                                                      unpack=True,
                                                      converters={0: bytespdate2num('%Y-%m-%d %H:%M:%S')})
    x = 0
    y = len(date)
    ohlc = []

    while x < y:
        append_me = date[
            x], openp[x], highp[x], lowp[x], closep[x] #, volume[x]
        ohlc.append(append_me)
        x+=1

    candlestick_ohlc(ax1, ohlc, width=return_candle_width(user_interval), colorup='#77d879', colordown='#db3f3f')

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.grid(True)
    
    red_patch = mpatches.Patch(color='red', label='To price coverted OHLC chart (Binance prices)')

    plt.xlabel('Date')
    plt.ylabel('USDT Price')
    plt.title(stock)
    plt.legend(handles=[red_patch])
    plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
    plt.show()

# run the script
graph_data(query_label)



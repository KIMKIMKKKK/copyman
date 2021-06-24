import ccxt 
import pprint
import time
import datetime
import pandas as pd
import math

api_key = 'L1OUjVgU53rcWhoMHKRpkSsTRd78lMPm5yDCLHu6nAodVG5C3xDpjx9yHcPoJA9E'
secret  = 'RJtkAy1FfYKpXIGHM4Hbm6joX4rh3TkfjppcNMltwC0rK3BvLIOUJTm3spLFohxf'

binance = ccxt.binance(config={
    'apiKey': api_key, 
    'secret': secret,
    'enableRateLimit': True,
    'options': {
    'defaultType': 'future'
    }
})

def cal_target(exchange, symbol):
    btc = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='1d', 
        since=None, 
        limit=10
    )
    
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.45
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.45
    return long_target, short_target

def bitcoin_target_price():
    btc = binance.fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe='1d', 
        since=None, 
        limit=10
    )
    
    df = pd.DataFrame(data=btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)

    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    bit_long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.25
    bit_short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.25
    return bit_long_target, bit_short_target

symbol = "DOGE/USDT"
long_target, short_target = cal_target(binance, symbol)
bit_long_target, bit_short_target = bitcoin_target_price()
ticker = "BTC/USDT"
btc_price = binance.fetch_ticker(ticker)
balance = binance.fetch_balance()
usdt = balance['total']['USDT']
position = {
    "type": None,
    "amount": 0
}

def cal_amount(usdt_balance, cur_price):
    portion = 0.95
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount

def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position):
    if cur_price >= long_target and 0 < btc_price['last'] - bit_long_target:        
        position['type'] = 'long'
        position['amount'] = amount
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
    elif cur_price <= short_target and 0 > btc_price['last'] - bit_short_target:      
        position['type'] = 'short'
        position['amount'] = amount
        exchange.create_market_sell_order(symbol=symbol, amount=amount)

def exit_position(exchange, symbol, position):
    amount = position['amount']
    if position['type'] == 'long':
        exchange.create_market_sell_order(symbol=symbol, amount=amount)
        position['type'] = None 
    elif position['type'] == 'short':
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
        position['type'] = None 

while True: 
    now = datetime.datetime.now()

    if now.hour == 8 and now.minute == 50 and (0 <= now.second < 10):
        if position['type'] is not None:
            exit_position(binance, symbol, position)

    # udpate target price
    if now.hour == 9 and now.minute == 0 and (20 <= now.second < 30):
        long_target, short_target = cal_target(binance, symbol)
        balance = binance.fetch_balance()
        usdt = balance['total']['USDT']
        time.sleep(10)

    ticker = binance.fetch_ticker(symbol)
    cur_price = ticker['last']
    amount = cal_amount(usdt, cur_price)

    if position['type'] is None:
        enter_position(binance, symbol, cur_price, long_target, short_target, amount, position)

    print(now, long_target, cur_price, short_target, balance['USDT'], btc_price['last'] - bit_short_target)
    time.sleep(1)

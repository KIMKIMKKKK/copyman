import ccxt 
import pprint
import time
import datetime
import pandas as pd
import math
import schedule
from fbprophet import Prophet

api_key = ''
secret  = ''

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
    long_target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.5
    short_target = today['open'] - (yesterday['high'] - yesterday['low']) * 0.5
    return long_target, short_target 

btc = binance.fetch_ohlcv(
    symbol="BTC/USDT", 
    timeframe='30m', 
    since=None, 
    limit=400)

symbol = "BTC/USDT"
long_target, short_target = cal_target(binance, symbol)
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

btc = binance.fetch_ohlcv(
    symbol="BTC/USDT", 
    timeframe='30m', 
    since=None, 
    limit=400)

predicted_close_price = 0
def predict_price(ticker):
    global predicted_close_price
    df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
    predict_price("BTC/USDT")
    schedule.every().hour.do(lambda: predict_price("BTC/USDT"))

def enter_position(exchange, symbol, cur_price, long_target, short_target, amount, position):
    if cur_price > long_target and cur_price < predicted_close_price:       
        position['type'] = 'long'
        position['amount'] = amount
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
    elif cur_price < short_target and predicted_close_price < cur_price:     
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

    print(now, short_target, cur_price, long_target, predicted_close_price)
    time.sleep(1)

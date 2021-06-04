import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = ""
secret = ""

now = datetime.datetime.now()
upbit = pyupbit.Upbit(access, secret)

def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * 0.49
    return target_price

def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

start_time = get_start_time("KRW-BTC")
end_time = start_time + datetime.timedelta(days=1)

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def get_ma20(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    ma20 = df['close'].rolling(15).mean().iloc[-1]
    return ma20

def get_ma15(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

predicted_close_price = 0
def predict_price(ticker):
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
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

def buy(coin):
    if start_time < now < end_time - datetime.timedelta(seconds=45):
        predict_price(coin)
        schedule.every().hour.do(lambda: predict_price(coin))
        target_price = get_target_price(coin)
        ma5 = get_ma5(coin)
        ma15 = get_ma15(coin)
        ma20 = get_ma20(coin)
        current_price = get_current_price(coin)
        if target_price <= current_price and current_price <= target_price*1.01 and ma15 <= current_price and current_price <= predicted_close_price and ma20*0.97 <= ma5:
            krw = get_balance("KRW")
            if krw > 5000:
                upbit.buy_market_order(coin, krw*0.2)

def sell(coin, KRW):
    btc = get_balance(coin)
    if btc > 0.00008:
        upbit.sell_market_order(KRW, btc)
        time.sleep(1)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=45):
            print("Target_price Searching start", now)
            buy("KRW-BTC")
            buy("KRW-ETH")
            buy("KRW-ADA")
            buy("KRW-DOGE")
            buy("KRW-XRP")
            buy("KRW-DOT")
            buy("KRW-BCH")
            buy("KRW-LINK")
            buy("KRW-LTC")
            buy("KRW-XLM")
            buy("KRW-THETA")
            buy("KRW-VET")
            buy("KRW-ETC")
            buy("KRW-EOS")
            buy("KRW-TRX")
            buy("KRW-NEO")
            buy("KRW-IOTA")
            buy("KRW-ATOM")
            buy("KRW-BTT")
        else:
            print("last_price selling", now)
            sell("BTC", "KRW-BTC")
            sell("ETH", "KRW-ETH")
            sell("ADA", "KRW-ADA")
            sell("DOGE", "KRW-DOGE")
            sell("XRP", "KRW-XRP")
            sell("DOT", "KRW-DOT")
            sell("BCH", "KRW-BCH")
            sell("LINK", "KRW-LINK")
            sell("LTC", "KRW-LTC")
            sell("XLM", "KRW-XLM")
            sell("THETA", "KRW-THETA")
            sell("VET", "KRW-VET")
            sell("ETC", "KRW-ETC")
            sell("EOS", "KRW-EOS")
            sell("TRX", "KRW-TRX")
            sell("NEO", "KRW-NEO")
            sell("IOTA", "KRW-IOTA")
            sell("ATOM", "KRW-ATOM")
            sell("BTT", "KRW-BTT")
    except Exception as e:
        print(e)
        time.sleep(1)          

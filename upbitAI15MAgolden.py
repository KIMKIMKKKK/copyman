import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = ""
secret = ""

now = datetime.datetime.now()
upbit = pyupbit.Upbit(access, secret)

def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

start_time = get_start_time("KRW-ETH")
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

def get_ma15(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_ma20(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    ma20 = df['close'].rolling(15).mean().iloc[-1]
    return ma20

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

def buy(coin, k):
    if start_time < now < end_time - datetime.timedelta(seconds=15):
        predict_price(coin)
        schedule.every().hour.do(lambda: predict_price(coin))
        target_price = get_target_price(coin, k)
        ma5 = get_ma5(coin)
        ma15 = get_ma15(coin)
        ma20 = get_ma20(coin)
        current_price = get_current_price(coin)
        if target_price < current_price and ma15 < current_price and current_price < predicted_close_price and (ma20*0.95) <= ma5:
            krw = get_balance("KRW")
            if krw > 5000:
                upbit.buy_market_order(coin, krw*0.9995)

def sell(coin, KRW):
    btc = get_balance(coin)
    if btc > 0.00008:
        upbit.sell_market_order(KRW, btc*0.9995)
        time.sleep(1)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=180):
            print("Target_price Searching start", now)
            buy("KRW-BTC", 0.5)
            buy("KRW-ETH", 0.5)
            buy("KRW-ADA", 0.5)
            buy("KRW-XRP", 0.5)
            buy("KRW-DOT", 0.5)
            buy("KRW-LINK", 0.5)
            buy("KRW-BCH", 0.5)
            buy("KRW-LTC", 0.5)
            buy("KRW-TRX", 0.5)
            buy("KRW-PCI", 0.5)
            buy("KRW-HUNT", 0.5)
            buy("KRW-STRK", 0.5)
            buy("KRW-XLM", 0.5)
            buy("KRW-VET", 0.5)
            buy("KRW-ATOM", 0.5)
            buy("KRW-ICX", 0.5)
            buy("KRW-BTT", 0.5)
            buy("KRW-DOGE", 0.5)
            buy("KRW-EDR", 0.5)
            buy("KRW-MFT", 0.5)
            buy("KRW-ORBS", 0.5)
            buy("KRW-NEO", 0.5)
            buy("KRW-ETC", 0.5)
            buy("KRW-ZIL", 0.5)
            buy("KRW-REP", 0.5)
            buy("KRW-IOTA", 0.5)
            buy("KRW-SRM", 0.5)
            buy("KRW-SBD", 0.5)
            buy("KRW-ZRX", 0.5)
            buy("KRW-MED", 0.5)
        else:
            print("last_price selling", now)
            sell("BTC", "KRW-BTC")
            sell("ETH", "KRW-ETH")
            sell("ADA", "KRW-ADA")
            sell("XRP", "KRW-XRP")
            sell("DOT", "KRW-DOT")
            sell("LINK", "KRW-LINK")
            sell("BCH", "KRW-BCH")
            sell("LTC", "KRW-LTC")
            sell("TRX", "KRW-TRX")
            sell("PCI", "KRW-PCI")
            sell("HUNT", "KRW-HUNT")
            sell("STRK", "KRW-STRK")
            sell("XLM", "KRW-XLM")
            sell("VET", "KRW-VET")
            sell("ATOM", "KRW-ATOM")
            sell("ICX", "KRW-ICX")
            sell("BTT", "KRW-BTT")
            sell("DOGE", "KRW-DOGE")
            sell("EDR", "KRW-EDR")
            sell("MFT", "KRW-MFT")
            sell("ORBS", "KRW-ORBS")
            sell("NEO", "KRW-NEO")
            sell("ETC", "KRW-ETC")
            sell("ZIL", "KRW-ZIL")
            sell("REP", "KRW-REP")
            sell("IOTA", "KRW-IOTA")
            sell("SRM", "KRW-SRM")
            sell("SBD", "KRW-SBD")    
            sell("ZRX", "KRW-ZRX")
            sell("MED", "KRW-MED")
    except Exception as e:
        print(e)
        time.sleep(1)          

import websocket, json, pprint
import numpy as np
import talib as ta
import math
from binance.client import Client

SOCKET = "wss://stream.binance.com:9443/ws/dogeusdt@kline_1m"

PAIR = "DOGEUSDT"

BUY_QUANTITY = 100.0

ATR_FACTOR = 3

closes = []
highs = []
lows = []

class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """
    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)

filename = 'credentials.txt'
connection = BinanceConnection(filename)

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def supertrendcheck(atr_factor, closes, highs, lows):

    close_array = np.asarray(closes)

    high_array = np.asarray(highs)

    low_array = np.asarray(lows)

    try:
        atr = ta.ATR(high_array, low_array, close_array, 10)
    except Exception as exp:
        print(f'exception: {str(exp)}')
        return False, False

    previous_final_upperband = 0
    previous_final_lowerband = 0
    final_upperband = 0
    final_lowerband = 0
    previous_close = 0
    previous_supertrend = 0
    supertrend = []
    supertrendc = 0

    for i in range(1, len(close_array)):
        if np.isnan(close_array[i]):
            pass
        else:
            highc = high_array[i]
            lowc = low_array[i]
            atrc = atr[i]
            closec = close_array[i]

            if math.isnan(atrc):
                atrc = 0

            basic_upperband = (highc + lowc) / 2 + atr_factor * atrc
            basic_lowerband = (highc + lowc) / 2 - atr_factor * atrc

            if basic_upperband < previous_final_upperband or previous_close > previous_final_upperband:
                final_upperband = basic_upperband
            else:
                final_upperband = previous_final_upperband

            if basic_lowerband > previous_final_lowerband or previous_close < previous_final_lowerband:
                final_lowerband = basic_lowerband
            else:
                final_lowerband = previous_final_lowerband

            if previous_supertrend == previous_final_upperband and closec <= final_upperband:
                supertrendc = final_upperband
            else:
                if previous_supertrend == previous_final_upperband and closec >= final_upperband:
                    supertrendc = final_lowerband
                else:
                    if previous_supertrend == previous_final_lowerband and closec >= final_lowerband:
                        supertrendc = final_lowerband
                    elif previous_supertrend == previous_final_lowerband and closec <= final_lowerband:
                        supertrendc = final_upperband

            supertrend.append(supertrendc)

            previous_close = closec

            previous_final_upperband = final_upperband

            previous_final_lowerband = final_lowerband

            previous_supertrend = supertrendc

    if close_array.size < 2:
        return False, False

    prev_close = close_array[-1]
    prev_prev_close = close_array[-2]

    color_change = False
    trend_positive = False

    if len(supertrend) < 2:
        return color_change, trend_positive

    last_supert = supertrend[-1]
    previous_supert = supertrend[-2]

    if prev_close > last_supert and prev_prev_close < previous_supert:
        color_change = True

    if prev_close < last_supert and prev_prev_close > previous_supert:
        color_change = True

    if prev_close > last_supert:
        trend_positive = True

    if prev_close < last_supert:
        trend_positive = False

    return color_change, trend_positive

def on_message(ws, message):
    global closes, highs, lows

    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']

    if is_candle_closed:
        close = float(candle['c'])
        high = float(candle['h'])
        low = float(candle['l'])
        print('close', close, 'high', high, 'low', low)

        # listelerimize ekliyoruz
        closes.append(close)
        highs.append(high)
        lows.append(low)

        if len(closes) > 10:
            color_change, trend_positive = supertrendcheck(ATR_FACTOR, closes, highs, lows)

            if color_change and trend_positive:
                print('al sinyali', flush=True)
                # buy_order = connection.client.order_market_buy(
                #     symbol=PAIR,
                #     quantity=BUY_QUANTITY)
            elif color_change and not trend_positive:
                print('sat sinyali', flush=True)
                # sell_order = connection.client.order_market_sell(
                #     symbol=PAIR,
                #     quantity=BUY_QUANTITY)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
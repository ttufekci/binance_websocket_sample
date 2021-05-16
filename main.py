import websocket, json, pprint

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

closes = []
highs = []
lows = []

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    global closes, highs, lows

    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    close = candle['c']
    high = candle['h']
    low = candle['l']
    print('close', close, 'high', high, 'low', low)

    # listelerimize ekliyoruz
    closes.append(close)
    highs.append(high)
    lows.append(low)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
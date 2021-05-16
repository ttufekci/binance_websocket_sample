from binance.client import Client
import time
client = Client("API_KEY", "API_SECRET")

pair = "ETHUSDT"
interval = "4h"
limit = 500

def supertrend_buy_sinyali_veriyor(klines):
    pass

while True:

    time.sleep(10)

    klines = client.get_klines(symbol=pair, interval=interval, limit=limit)

    if supertrend_buy_sinyali_veriyor(klines):
        buy_order = client.order_market_buy(
            symbol=pair,
            quantity=100)

# -*- coding: utf-8 -*-
import hashlib
import json
import time
import hmac
from urllib.parse import urlparse
import requests
access_id = ""  # Replace with your access id
secret_key = "" # Replace with your secret key
from enum import Enum

class leverages(Enum):
    LEVERAGE_100 = 100
    LEVERAGE_50 = 50
    LEVERAGE_30 = 30
    LEVERAGE_20 = 20
    LEVERAGE_15 = 15
    LEVERAGE_10 = 10
    LEVERAGE_8 = 8
    LEVERAGE_5 = 5
    LEVERAGE_3 = 3
    LEVERAGE_2 = 2
    LEVERAGE_1 = 1

class RequestsClient(object):
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "X-COINEX-KEY": "",
        "X-COINEX-SIGN": "",
        "X-COINEX-TIMESTAMP": "",
    }

    def __init__(self):
        self.access_id = access_id
        self.secret_key = secret_key
        self.url = "https://api.coinex.com/v2"
        self.headers = self.HEADERS.copy()

    # Generate your signature string
    def gen_sign(self, method, request_path, body, timestamp):
        prepared_str = f"{method}{request_path}{body}{timestamp}"
        signature = hmac.new(
            bytes(self.secret_key, 'latin-1'), 
            msg=bytes(prepared_str, 'latin-1'), 
            digestmod=hashlib.sha256
        ).hexdigest().lower()
        return signature

    def get_common_headers(self, signed_str, timestamp):
        headers = self.HEADERS.copy()
        headers["X-COINEX-KEY"] = self.access_id
        headers["X-COINEX-SIGN"] = signed_str
        headers["X-COINEX-TIMESTAMP"] = timestamp
        headers["Content-Type"] = "application/json; charset=utf-8"
        return headers

    def request(self, method, url, params={}, data=""):
        req = urlparse(url)
        request_path = req.path

        timestamp = str(int(time.time() * 1000))
        if method.upper() == "GET":
            # If params exist, query string needs to be added to the request path
            if params:
                query_params = []
                for item in params:
                    if params[item] is None:
                        continue
                    query_params.append(item + "=" + str(params[item]))
                query_string = "?{0}".format("&".join(query_params))
                request_path = request_path + query_string

            signed_str = self.gen_sign(
                method, request_path, body="", timestamp=timestamp
            )
            response = requests.get(
                url,
                params=params,
                headers=self.get_common_headers(signed_str, timestamp),
            )

        else:
            signed_str = self.gen_sign(
                method, request_path, body=data, timestamp=timestamp
            )
            response = requests.post(
                url, data, headers=self.get_common_headers(signed_str, timestamp)
            )

        if response.status_code != 200:
            raise ValueError(response.text)
        return response


request_client = RequestsClient()


def get_spot_market():
    request_path = "/spot/market"
    params = {"market": "BTCUSDT"}
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response

def get_future_market():
    request_path = "/futures/market"
    params = {"market": "BTCUSDT"}
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response

def get_future_ticker():
    request_path = "/futures/ticker"
    params = {"market": "BTCUSDT"}
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response


def get_last_price():
    return get_future_ticker().json()['data'][0]['last']

def get_futures_balance():
    request_path = "/assets/futures/balance"
    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
    )
    return response

def get_futures_available():
    return get_futures_balance().json()['data'][0]['available']


def get_deposit_address():
    request_path = "/assets/deposit-address"
    params = {"ccy": "USDT", "chain": "BTC"}

    response = request_client.request(
        "GET",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        params=params,
    )
    return response


def spot_limit():
    request_path = "/spot/order"
    data = {
        "market": "BTCUSDT",
        "market_type": "SPOT",
        "side": "buy",
        "type": "limit",
        "amount": "10000",
        "price": "1",
        "client_id": "user1",
        "is_hide": True,
    }
    data = json.dumps(data)
    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )
    return response


def set_leverage(leverage: int = 100):
    request_path = "/futures/adjust-position-leverage"
    data = {
        "market": "BTCUSDT",
        "market_type": "FUTURES",
        "margin_mode": "isolated",
        "leverage": leverage,
    }
    data = json.dumps(data)
    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )

    return response


def set_stoploss(stoploss: str):
    request_path = "/futures/set-position-stop-loss"
    data = {
        "market": "BTCUSDT",
        "market_type": "FUTURES",
        "stop_loss_type": "mark_price",
        "stop_loss_price": stoploss,
    }
    data = json.dumps(data)
    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )

    return response

def set_takeprofit(takeprofit: str):
    request_path = "/futures/set-position-take-profit"
    data = {
        "market": "BTCUSDT",
        "market_type": "FUTURES",
        "take_profit_type": "mark_price",
        "take_profit_price": takeprofit,
    }
    data = json.dumps(data)
    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )

    return response

def market_buy(amount: str, stoploss: str = None, takeprofit: str = None, side="buy", market: str = "BTCUSDT"):
    request_path = "/futures/order"
    data = {
        "market": market,
        "market_type": "FUTURES",
        "side": side,
        "type": "market",
        "amount": amount,
        "client_id": "your_custom_client_id",
        "is_hide": True,
    }
    data = json.dumps(data)

    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )
    if stoploss:
        set_stoploss(stoploss)
    if takeprofit:
        set_takeprofit(takeprofit)
    
    
    return response



def limt_buy(amount: str, price: str, stoploss: str = None, takeprofit: str = None, side="buy", market: str = "BTCUSDT"):
    request_path = "/futures/order"
    data = {
        "market": market,
        "market_type": "FUTURES",
        "side": side,
        "type": "limit",
        "amount": amount,
        "price": price,
        "client_id": "your_custom_client_id",
        "is_hide": True,
    }
    data = json.dumps(data)
    print(data)
    full_url = "{url}{request_path}".format(url=request_client.url, request_path=request_path)
    print(f"Full URL: {full_url}")

    response = request_client.request(
        "POST",
        "{url}{request_path}".format(url=request_client.url, request_path=request_path),
        data=data,
    )
    
    if stoploss:
        set_stoploss(stoploss)
    if takeprofit:
        set_takeprofit(takeprofit)
    
    
    return response

def run_code():

    LEVERAGE = leverages.LEVERAGE_100.value
    BETPERCENT = 0.1
    STOPLOSS = 0.5 # [0, 1]
    
    response = set_leverage(LEVERAGE)
    if response.status_code == 200:
        print("Leverage = Good")

    assetPrice = float(get_last_price())
    print("Price of Asset " + str(assetPrice))
    
    currentBalance = float(get_futures_available())
    print("Total Balance: " + str(currentBalance))

    size = str(LEVERAGE * BETPERCENT * currentBalance / assetPrice)
    stopLoss = str(assetPrice * (1 - (STOPLOSS/LEVERAGE)))

    response_5 = market_buy(size, stopLoss)
    if response_5.status_code == 200:
        print("Position Opened")

if __name__ == "__main__":
    run_code()

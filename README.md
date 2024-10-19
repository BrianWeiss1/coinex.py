# coinex.py
API grabber for trading with coinex

Just input your access key with your private api key here and change the variables here:
```python
LEVERAGE = leverages.LEVERAGE_100.value
BETPERCENT = 0.1
STOPLOSS = 0.5 # [0, 1]
```
```python
access_id = ""  # Replace with your access id
secret_key = "" # Replace with your secret key
```

To place the trade:
1. Determine the number of units of the asset you would like to purchase, currently it places a trade based on current balance and leverage
2. stopLoss is derived from STOPLOSS, which if multiplied by 100, is the percentage of the position until stoploss. 
3. takeProfit can be added onto market_buy or limit_buy functions. 
```python
size = str(LEVERAGE * BETPERCENT * currentBalance / assetPrice)
stopLoss = str(assetPrice * (1 - (STOPLOSS/LEVERAGE)))

response_5 = market_buy(size, stopLoss)
```

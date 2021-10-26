    #  binance = {
    #                 "symbol": "LINKBUSD",
    #                 "orderId": 376772363,
    #                 "orderListId": -1,
    #                 "clientOrderId": "yFIxBC6F3WLKnQ7SbRcPpa",
    #                 "transactTime": 1635111687221,
    #                 "price": "0.00000000",
    #                 "origQty": "0.34000000",
    #                 "executedQty": "0.34000000",
    #                 "cummulativeQuoteQty": "10.06060000",
    #                 "status": "FILLED",
    #                 "timeInForce": "GTC",
    #                 "type": "MARKET",
    #                 "side": "BUY",
    #                 "fills": [
    #                     {
    #                         "price": "29.59000000",
    #                         "qty": "0.34000000",
    #                         "commission": "0.00034000",
    #                         "commissionAsset": "LINK",
    #                         "tradeId": 14704963
    #                     }
    #                 ]
    #             }

from datetime import datetime
#at the start of the script:
start_time = datetime.now()
# ... some stuff ...
# when you want to print the time elapsed so far:
now_time = datetime.now()
print(now_time - start_time)
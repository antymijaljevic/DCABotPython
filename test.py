# import schedule, time

# def do_nothing():
#     print("Hello there!")


# schedule.every().day.at("09:51").do(do_nothing)
# # schedule.every(10).seconds.do(do_nothing)

# schedule.run_pending()
# while 1:
#     schedule.run_pending()
#     time.sleep(1)

# data = {
#     'symbol': 'ADA/BUSD', 
#     'timestamp': 1631959078681, 
#     'datetime': '2021-09-18T09:57:58.681Z', 
#     'high': 2.414, 
#     'low': 2.312, 
#     'bid': 2.399, 
#     'bidVolume': 10584.5, 
#     'ask': 2.4, 
#     'askVolume': 12101.3, 
#     'vwap': 2.3683262, 
#     'open': 2.398, 
#     'close': 2.4, 
#     'last': 2.4, 
#     'previousClose': 2.398, 
#     'change': 0.002, 
#     'percentage': 0.083, 
#     'average': 2.399, 
#     'baseVolume': 51714910.5, 
#     'quoteVolume': 122477777.376, 
#     'info': {
#         'symbol': 'ADABUSD', 
#         'priceChange': '0.00200000', 
#         'priceChangePercent': '0.083', 
#         'weightedAvgPrice': '2.36832620', 
#         'prevClosePrice': '2.39800000', 
#         'lastPrice': '2.40000000', 
#         'lastQty': '442.80000000', 
#         'bidPrice': '2.39900000', 
#         'bidQty': '10584.50000000', 
#         'askPrice': '2.40000000', 
#         'askQty': '12101.30000000', 
#         'openPrice': '2.39800000', 
#         'highPrice': '2.41400000', 
#         'lowPrice': '2.31200000', 
#         'volume': '51714910.50000000', 
#         'quoteVolume': '122477777.37600000', 
#         'openTime': '1631872678681', 
#         'closeTime': '1631959078681', 
#         'firstId': '51968194', 
#         'lastId': '52103787', 
#         'count': '135594'
#         }
#     }

data = {'symbol': 'ADA/BUSD', 'timestamp': 1631959796858, 'datetime': '2021-09-18T10:09:56.858Z', 'high': 2.416, 'low': 2.312, 'bid': 2.413, 'bidVolume': 6889.0, 'ask': 2.414, 'askVolume': 263.3, 'vwap': 2.36868535, 'open': 2.394, 'close': 2.414, 'last': 2.414, 'previousClose': 2.395, 'change': 0.02, 'percentage': 0.835, 'average': 2.404, 'baseVolume': 51920553.9, 'quoteVolume': 122983455.2327, 'info': {'symbol': 'ADABUSD', 'priceChange': '0.02000000', 'priceChangePercent': '0.835', 'weightedAvgPrice': '2.36868535', 'prevClosePrice': '2.39500000', 'lastPrice': '2.41400000', 'lastQty': '10897.70000000', 'bidPrice': '2.41300000', 'bidQty': '6889.00000000', 'askPrice': '2.41400000', 'askQty': '263.30000000', 'openPrice': '2.39400000', 'highPrice': '2.41600000', 'lowPrice': '2.31200000', 'volume': '51920553.90000000', 'quoteVolume': '122983455.23270000', 'openTime': '1631873396858', 'closeTime': '1631959796858', 'firstId': '51970116', 'lastId': '52105555', 'count': '135440'}}

report = data['info']['priceChangePercent']
print(round(float(report), 2),"%")
#written by antymijaljevic@gmail.com

import ccxt, telegram_send, schedule, time, multiprocessing, gspread
from keys import API_KEY, SECRET
from datetime import datetime

#connecting on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})

#connecting on the google spreadsheet
spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
order_1_sheet = spreadsheet_id.get_worksheet(0)
order_2_sheet = spreadsheet_id.get_worksheet(1)
report_sheet = spreadsheet_id.get_worksheet(2)

#trading set up
orderOnePair = 'ADA/BUSD'
orderTwoPair = 'ETH/BUSD'
#investment
orderOneInvestment = 10
orderTwoInvestment = 10
#time of buying every day
orderOneTime = "01:15"
orderTwoTime = "01:15"


#spot wallet balance
def walletBalance():
    now = str(datetime.now())
    balance = exchange.fetch_total_balance()
    balancePrint = "***SPOT WALLET BALANCE***\n\n" + "Date: " + now[:16] + "\n" +  "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + orderOnePair[:3] + " = " + str(int(balance[orderOnePair[:3]])) + " " + orderOnePair[:1]  + "\n" + orderTwoPair[:3] + " = " + str(int(balance[orderTwoPair[:3]])) + " " + orderTwoPair[0:1]
    #telegram notification
    telegram_send.send(messages=[balancePrint])
    print('Spot wallet report ... SENT', now[:16])

#prices of the pairs telegram notification
def lastPrices():
    now = str(datetime.now())
    pairOnePrice = exchange.fetch_ticker(orderOnePair)
    pairTwoPrice = exchange.fetch_ticker(orderTwoPair)
    priceReport = "***CURRENT PRICES***\n\n" + "Date: " + now[:16] + "\n" + orderOnePair[:3] + " >> " + str(round(pairOnePrice['last'], 2))+"$" + "\n" + orderTwoPair[:3] + " >> " + str(round(pairTwoPrice['last'], 2))+"$"
    telegram_send.send(messages=[priceReport])
    print('Last prices report ... SENT', now[:16])

#for this method please check google spreadsheet which I shared with you, sheet"Every day 10$ + 60$ on -10% dips"
def percentageReport():
    now = str(datetime.now())
    firstPair = exchange.fetch_ticker(orderOnePair)
    firstPairP = round(float(firstPair['info']['priceChangePercent']), 2)
    secondPair = exchange.fetch_ticker(orderTwoPair)
    secondPairP = round(float(secondPair['info']['priceChangePercent']), 2)
    #alert message
    alert = "***DIP ALERT!***\n\n" + "Date: " + now[:16] + "\n" + orderOnePair[0:3] + " >> " + str(firstPairP) + " %\n" + orderTwoPair[0:3] + " >> " + str(secondPairP) + " %\n\nDo you want to invest more?"

    #if there is dip more than -10% it notifies you to invest extra money manually
    if firstPairP < -9.99 or secondPairP < -9.99:
        #send reports to telegram and to sheet
        telegram_send.send(messages=[alert])
        sheetReport1 = now[:16], orderOnePair[0:3], str(firstPairP)+"%"
        report_sheet.append_row(sheetReport1)
        sheetReport2 = now[:16], orderTwoPair[0:3], str(secondPairP)+"%"
        report_sheet.append_row(sheetReport2)
        print('Percentage report ... SENT', now[:16])
    else:
        print("No extreme percentage ... STATUS OK", now[:16])

#first pair trade
def order_1():
    symbol = orderOnePair
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = orderOneInvestment
    try:
        now = str(datetime.now())
        data = exchange.create_order(symbol, type, side, amount, price)
        filledAt = float(data['info']['fills'][0]['price'])
        commissionRate = float(data['info']['fills'][0]['commission'])
        #send reports to telegram and to sheet
        telReport = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + now[:16] + "\n" + "Filled at: " + str(filledAt) + " $ \n" + "Amount: " + str(data.get('amount')) + " " + orderOnePair[:3] + "\n" + "Invested: " + str(round(data.get('cost'), 2)) + " $"
        telegram_send.send(messages=[telReport])
        sheetReport = now[:10], now[11:16], float(filledAt), round(data.get('cost'), 2), float(commissionRate), data.get('amount')
        order_1_sheet.append_row(sheetReport)
        print('ORDER 1 FULFILLED ... DONE', now[:16])
    except:
        telegram_send.send(messages=["Binance API connection issue!\n" + orderOnePair +  " buying order has failed!"])
#second pair trade
def order_2():
    symbol = orderTwoPair  
    type = 'market'  # or 'limit'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = orderTwoInvestment
    try:
        now = str(datetime.now())
        data = exchange.create_order(symbol, type, side, amount, price)
        filledAt = float(data['info']['fills'][0]['price'])
        commissionRate = float(data['info']['fills'][0]['commission'])
        #send reports to telegram and to sheet   
        telReport = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + now[:16] + "\n" + "Filled at: " + str(filledAt) + " $\n" + "Amount: " + str(data.get('amount')) + " " + orderTwoPair[:3] + "\n" + "Invested: " + str(round(data.get('cost'), 2)) + " $"
        telegram_send.send(messages=[telReport])
        sheetReport = now[:10], now[11:16], float(filledAt), round(data.get('cost'), 2), float(commissionRate), data.get('amount')
        order_2_sheet.append_row(sheetReport)
        print('ORDER 2 FULFILLED ... DONE', now[:16])
    except:
        telegram_send.send(messages=["Binance API connection issue!\n" + orderTwoPair +  " buying order has failed!"])


# multiprocessing 1|spot wallet 2| last price ada/sol 3| dip alert 4| first pair trade 5| second pair trade
first_process = multiprocessing.Process(name='first_process', target=walletBalance)
second_process = multiprocessing.Process(name='second_process', target=lastPrices)
third_process = multiprocessing.Process(name='third_process', target=percentageReport)
fourth_process = multiprocessing.Process(name='fourth_process', target=order_1)
fifth_process = multiprocessing.Process(name='fifth_process', target=order_2)

#running processes/functions in different times
#https://schedule.readthedocs.io/en/stable/examples.html

# # 1| Spot wallet report
# schedule.every(12).hours.do(first_process.run)
# # 2| last pairs prices
# schedule.every(3).hours.do(second_process.run)
# # 3| dip alert
# schedule.every(4).hours.do(third_process.run)
# # 4| first pair trade
# schedule.every().day.at(orderOneTime).do(fourth_process.run)
# # 5| second pair trade
# schedule.every().day.at(orderTwoTime).do(fifth_process.run)

# #only for testing purposes
#spot wallet report
schedule.every(10).seconds.do(first_process.run)
#last price report
schedule.every(10).seconds.do(second_process.run)
#dip alert
schedule.every(10).seconds.do(third_process.run)
# # first pair trade
# schedule.every(10).seconds.do(fourth_process.run)
# # second pair trade
# schedule.every(10).seconds.do(fifth_process.run)

schedule.run_pending()

while 1:
    schedule.run_pending()
    time.sleep(1)
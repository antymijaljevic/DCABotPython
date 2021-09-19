#written by antymijaljevic@gmail.com

import ccxt, telegram_send, schedule, time, multiprocessing
from keys import API_KEY, SECRET
from datetime import datetime

#connecting on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})

#trading set up
orderOnePair = 'ADA/BUSD'
orderTwoPair = 'SOL/BUSD'
#investment
orderOneInvestment = 10
orderTwoInvestment = 10
#time of buying every day
orderOne = "01:15"
orderTwo = "01:15"
#timestamp
now = str(datetime.now())


#spot wallet balance
def walletBalance():
	balance = exchange.fetch_total_balance()
	balancePrint = "***SPOT WALLET BALANCE***\n\n" + "DATE: " + now[:16] + "\n" +  "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + orderOnePair[:3] + " = " + str(int(balance[orderOnePair[:3]])) + " " + orderOnePair[:1]  + "\n" + orderTwoPair[:3] + " = " + str(int(balance[orderTwoPair[:3]])) + " " + orderTwoPair[0:1]
	#telegram notification
	telegram_send.send(messages=[balancePrint])


#prices of the pairs telegram notification
def lastPrices():
	pairOnePrice = exchange.fetch_ticker(orderOnePair)
	pairTwoPrice = exchange.fetch_ticker(orderTwoPair)
	priceReport = "***CURRENT PRICES***\n\n" + "DATE: " + now[:16] + "\n" + orderOnePair[:3] + " >> " + str(round(pairOnePrice['last'], 2))+"$" + "\n" + orderTwoPair[:3] + " >> " + str(round(pairTwoPrice['last'], 2))+"$"
	telegram_send.send(messages=[priceReport])

#for this method please check google spreadsheet which I shared with you, sheet"Every day 10$ + 60$ on -10% dips"
def percentageReport():
    firstPair = exchange.fetch_ticker(orderOnePair)
    firstPairP = round(float(firstPair['info']['priceChangePercent']), 2)
    secondPair = exchange.fetch_ticker(orderTwoPair)
    secondPairP = round(float(secondPair['info']['priceChangePercent']), 2)
    #alert message
    alert = "***DIP ALERT!***\n\n" + "DATE: " + now[:16] + "\n" + orderOnePair[0:3] + " >> " + str(firstPairP) + " %\n" + orderTwoPair[0:3] + " >> " + str(secondPairP) + " %\n\nDo you want to invest more?"

    #if there is dip more than -10% it notifies you to invest extra money manually
    if firstPairP < 1 or secondPairP < -9.99:
        telegram_send.send(messages=[alert])
        #possible call on buyAda function with 60$ extra or let user to buy manually
    else:
        print("SCRIPT STATUS ... OK", now[:16])

#first pair trade
#I have in plan to implement pysheet library to save data directly to google spreadsheet
def order_1():
    symbol = orderOnePair
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = orderOneInvestment
    try:
        data = exchange.create_order(symbol, type, side, amount, price)
        #send report
        report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + now[:16] + "\n" + "Amount: " + str(data.get('amount')) + orderOnePair[:3] + "\n" + "Cost: " + str(data.get('cost')) + " $"
        telegram_send.send(messages=[report])
    except:
        telegram_send.send(messages=["Binance API connection issue!\nADA buying order failed"])

#second pair trade
def order_2():
    symbol = orderTwoPair  
    type = 'market'  # or 'limit'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = orderTwoInvestment
    try:
        data = exchange.create_order(symbol, type, side, amount, price)
        #send report    
        report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + now[:16] + "\n" + "Amount: " + str(data.get('amount')) + orderTwoPair[:3] + "\n" + "Cost: " + str(data.get('cost')) + " $"
        telegram_send.send(messages=[report])
    except:
        telegram_send.send(messages=["Binance API connection issue!\nSOL buying order failed"])

if __name__ == '__main__':
    # multiprocessing 1|spot wallet 2| last price ada/sol 3| dip alert 4| first pair trade 5| second pair trade
    first_process = multiprocessing.Process(name='first_process', target=walletBalance)
    second_process = multiprocessing.Process(name='second_process', target=lastPrices)
    third_process = multiprocessing.Process(name='third_process', target=percentageReport)
    fourth_process = multiprocessing.Process(name='fourth_process', target=order_1)
    fifth_process = multiprocessing.Process(name='fifth_process', target=orderTwoPair)

    #running processes/functions in different times
    #https://schedule.readthedocs.io/en/stable/examples.html

    # # 1| Spot wallet report
    # schedule.every().day.at("12:00").do(first_process.run)
    # # 2| last price ada/sol
    # schedule.every(2).hours.do(second_process.run)
    # # 3| dip alert
    # schedule.every(4).hours.do(third_process.run)
    # # 4| first pair trade
    # schedule.every().day.at(orderOne).do(fourth_process.run)
    # # 5| second pair trade
    # schedule.every().day.at(orderTwo).do(fifth_process.run)

    #only for testing purposes
    #spot wallet report
    # schedule.every(3).seconds.do(first_process.run)
    # #last price report
    # schedule.every(3).seconds.do(second_process.run)
    # #dip alert
    schedule.every(3).seconds.do(third_process.run)
    # #buy ada
    # schedule.every(3).seconds.do(fourth_process.run)
    # #buy sol
    # schedule.every(3).seconds.do(fifth_process.run)

    schedule.run_pending()

    while 1:
        schedule.run_pending()
        time.sleep(1)
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

#spot wallet balance
def walletBalance():
	balance = exchange.fetch_total_balance()
	balancePrint = "***SPOT WALLET BALANCE***\n\n" + "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + "ADA = " + str(int(balance['ADA'])) + " ADA" + "\n" "SOL = " + str(int(balance['SOL'])) + " S"
	#telegram notification
	telegram_send.send(messages=[balancePrint])


#ada and sol last prices telegram notification
def lastPrices():
	currentAdaPrice = exchange.fetch_ticker('ADA/BUSD')
	currentSolPrice = exchange.fetch_ticker('SOL/BUSD')
	priceReport = "***CURRENT PRICES***\n\n" + "ADA >> " + str(round(currentAdaPrice['last'], 2))+"$" + "\n" + "SOL >> " + str(round(currentSolPrice['last'], 2))+"$"
	telegram_send.send(messages=[priceReport])

#for this method please check google spreadsheet which I shared with you, sheet"Every day 10$ + 60$ on -10% dips"
def percentageReport():
    ada = exchange.fetch_ticker('ADA/BUSD')
    ada = round(float(ada['info']['priceChangePercent']), 2)
    sol = exchange.fetch_ticker('SOL/BUSD')
    sol = round(float(sol['info']['priceChangePercent']), 2)
    #alert message
    alert = "***DIP ALERT!***\n\n" + "ADA >> " + str(ada) + " %" + "\nSOL >> " + str(sol) + " %\n\nDo you want to invest more?"

    #if there is dip more than -10% it notifies you to invest extra money manually
    if ada < -9.99 or sol < -9.99:
        print(ada, sol)
        telegram_send.send(messages=[alert])
        #possible call on buyAda function with 60$ extra or let user to buy manually
    else:
        now = str(datetime.now())
        print("SCRIPT STATUS ... OK", now[:16])

#buy or sell ada
#I have in plan to implement pysheet library to save data directly to google spreadsheet
def buyAda():
    symbol = 'ADA/BUSD'  
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    try:
        data = exchange.create_order(symbol, type, side, amount, price)
        #send report
        report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:1]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " ADA" + "\n" + "Cost: " + str(data.get('cost')) + " $"
        telegram_send.send(messages=[report])
    except:
        telegram_send.send(messages=["Binance API connection issue!\nADA buying order failed"])

#buy or sell sol
def buySol():
    symbol = 'SOL/BUSD'  
    type = 'market'  # or 'limit'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    try:
        data = exchange.create_order(symbol, type, side, amount, price)
        #send report    
        report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:10]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " SOL" + "\n" + "Cost: " + str(data.get('cost')) + " $"
        telegram_send.send(messages=[report])
    except:
        telegram_send.send(messages=["Binance API connection issue!\nSOL buying order failed"])

if __name__ == '__main__':
    # multiprocessing 1|spot wallet 2| last price ada/sol 3| dip alert 4| buy ada 5| buy sol
    first_process = multiprocessing.Process(name='first_process', target=walletBalance)
    second_process = multiprocessing.Process(name='second_process', target=lastPrices)
    third_process = multiprocessing.Process(name='third_process', target=percentageReport)
    fourth_process = multiprocessing.Process(name='fourth_process', target=buyAda)
    fifth_process = multiprocessing.Process(name='fifth_process', target=buySol)

    #running processes/functions in different times
    #https://schedule.readthedocs.io/en/stable/examples.html

    # 1| Spot wallet report
    schedule.every().day.at("12:00").do(first_process.run)
    # 2| last price ada/sol
    schedule.every(2).hours.do(second_process.run)
    # 3| dip alert
    schedule.every(4).hours.do(third_process.run)
    # 4| buy ada
    schedule.every().day.at("03:30").do(fourth_process.run)
    # 5| buy sol
    schedule.every(48).hours.do(fifth_process.run)

    #only for testing purposes
    # #spot wallet report
    # schedule.every(3).seconds.do(first_process.run)
    # #last price report
    # schedule.every(3).seconds.do(second_process.run)
    # #dip alert
    # schedule.every(3).seconds.do(third_process.run)
    # #buy ada
    # schedule.every(3).seconds.do(fourth_process.run)
    # #buy sol
    # schedule.every(3).seconds.do(fifth_process.run)

    schedule.run_pending()

    while 1:
        schedule.run_pending()
        time.sleep(1)
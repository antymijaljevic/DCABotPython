#written by antymijaljevic@gmail.com

import ccxt, telegram_send, schedule, time, multiprocessing
from keys import API_KEY, SECRET


#connecting on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})

#spot wallet balance (this is here only if neeeded)
def walletBalance():
	balance = exchange.fetch_total_balance()
	balancePrint = "***SPOT WALLET BALANCE***\n\n" + "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + "ADA = " + str(int(balance['ADA'])) + " ADA" + "\n" "SOL = " + str(int(balance['SOL'])) + " S"
	#telegram notification
	telegram_send.send(messages=[balancePrint])


#ada and sol last prices telegram notification (this is here only if neeeded)
def lastPrices():
	currentAdaPrice = exchange.fetch_ticker('ADA/BUSD')
	currentSolPrice = exchange.fetch_ticker('SOL/BUSD')
	priceReport = "***CURRENT PRICES***\n\n" + "ADA >> " + str(round(currentAdaPrice['last'], 2))+"$" + "\n" + "SOL >> " + str(round(currentSolPrice['last'], 2))+"$"
	telegram_send.send(messages=[priceReport])

#for this method please check google spreadsheet which I shared with you  sheet"Every day 10$ + 60$ on -10% dips"
def percentageReport():
    ada = exchange.fetch_ticker('ADA/BUSD')
    ada = round(float(ada['info']['priceChangePercent']), 2)
    sol = exchange.fetch_ticker('SOL/BUSD')
    sol = round(float(sol['info']['priceChangePercent']), 2)
    #alert message
    alert = "***DIP ALERT!***\n\n" + "ADA >> " + str(ada) + " %" + "\nSOL >> " + str(sol) + " %\n\nDo you want to invest more?"

    #if there is dip more than -10% it notifies you to invest extra money manually
    if ada -9.99 or sol < -9.99:
        telegram_send.send(messages=[alert])
        #possible call on buyAda function with 60$ extra or let user to buy manually
    else:
        pass

#buy or sell ada
#I have in plan to implement pysheet library to save data directly to google spreadsheet
def buyAda():
    symbol = 'ADA/BUSD'  
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    data = exchange.create_order(symbol, type, side, amount, price)
    report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:10]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " ADA" + "\n" + "Cost: " + str(data.get('cost')) + " $"
    telegram_send.send(messages=[report])

#buy or sell sol (this is here only if neeeded)
def buySol():
    symbol = 'SOL/BUSD'  
    type = 'market'  # or 'limit'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    data = exchange.create_order(symbol, type, side, amount, price)
    report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:10]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " SOL" + "\n" + "Cost: " + str(data.get('cost')) + " $"
    telegram_send.send(messages=[report])


if __name__ == '__main__':
    # multiprocessing 1 | spot wallet and ada/sol prices 2| orders
    first_process = multiprocessing.Process(name='first_process', target=buyAda)
    second_process = multiprocessing.Process(name='second_process', target=percentageReport)

    #set specific time to repeat the processes
    #first process is buying ada for $10 dollars per day
    # schedule.every().day.at("04:00").do(first_process.run)

    #second process is sending report about incoming dips
    #schedule.every(12).hours.do(second_process.run)

    #testing
    # schedule.every(5).seconds.do(second_process.run)

    #if needed
    # schedule.every(3).seconds.do(job)
    # schedule.every(3).minutes.do(job)
    # schedule.every(3).hours.do(job)
    # schedule.every(3).days.do(job)
    # schedule.every(3).weeks.do(job)

    schedule.run_pending()

    while 1:
        schedule.run_pending()
        time.sleep(1)
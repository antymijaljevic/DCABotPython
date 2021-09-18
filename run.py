#written by antymijaljevic@gmail.com

import ccxt, telegram_send, schedule, time, multiprocessing
from keys import API_KEY, SECRET


#connecting on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})

def walletBalance():
	#spot wallet balance
	balance = exchange.fetch_total_balance()
	balancePrint = "***SPOT WALLET BALANCE***\n\n" + "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + "ADA = " + str(int(balance['ADA'])) + " ADA" + "\n" "SOL = " + str(int(balance['SOL'])) + " S"
	#telegram notification
	telegram_send.send(messages=[balancePrint])


#ada and sol last prices telegram notification
def lastPrices():
	currentAdaPrice = exchange.fetch_ticker('ADA/BUSD')
	currentSolPrice = exchange.fetch_ticker('SOL/BUSD')
	priceReport = "***CURRENT PRICES***\n\n" + "ADA >> " + str(round(currentAdaPrice['last'], 2))+"$" + "\n" + "SOL >> " + str(round(currentSolPrice['last'], 2))+"$"
	#telegram notification
	telegram_send.send(messages=[priceReport])

def percentageReport():
	currentAdaPrice = exchange.fetch_ticker('ADA/BUSD')
	currentAdaPrice = float(currentAdaPrice['info']['priceChangePercent'])
	currentSolPrice = exchange.fetch_ticker('SOL/BUSD')
	currentSolPrice = float(currentSolPrice['info']['priceChangePercent'])
	currentPercentages = "***CURRENT PERCENTAGES***\n\n" + "ADA >> " + str(round(currentAdaPrice, 2)) + " %" + "\nSOL >> " + str(round(currentSolPrice, 2)) + " %\n\nDo you want to invest more?"
	# #telegram notification
	telegram_send.send(messages=[currentPercentages])

#buy or sell ada
def buyAda():
    symbol = 'ADA/BUSD'  
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    data = exchange.create_order(symbol, type, side, amount, price)
    report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:10]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " ADA" + "\n" + "Cost: " + str(data.get('cost')) + " $"
    #telegram notification
    telegram_send.send(messages=[report])

#buy or sell sol
def buySol():
    symbol = 'SOL/BUSD'  
    type = 'market'  # or 'limit'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = 10  # dollar investment every day
    data = exchange.create_order(symbol, type, side, amount, price)
    report = "***BUYING ORDER FULFILLED***\n\n" + "Date: " + str(data.get('datetime')[0:10]) + "\n" + "Time: " + str(data.get('datetime')[11:19]) + "\n" + "Amount: " + str(data.get('amount')) + " SOL" + "\n" + "Cost: " + str(data.get('cost')) + " $"
    #telegram notification
    telegram_send.send(messages=[report])


if __name__ == '__main__':
    # multiprocessing 1 | spot wallet and ada/sol prices 2| orders
    first_process = multiprocessing.Process(name='first_process', target=buyAda)
    second_process = multiprocessing.Process(name='second_process', target=buySol)

    #set specific time to repeat the processes
    # schedule.every(70).seconds.do(first_process.run)
    schedule.every().day.at("04:00").do(first_process.run)
    schedule.every().day.at("04:30").do(second_process.run)

    schedule.run_pending()

    while 1:
        schedule.run_pending()
        time.sleep(1)















# try:
# 	percentageReport()
# except:
# 	telegram_send.send(messages=["***Failed to read data!***"])


# try:
# 	walletBalance()
# except:
# 	telegram_send.send(messages=["***Failed to read data!***"])

# try:
# 	lastPrices()
# except:
# 	telegram_send.send(messages=["***Failed to read data!***"])

# try:
# 	buyAda()
# except:
# 	telegram_send.send(messages=["***Failed to fulfill order!***"])

# try:
# 	buySol()
# except:
# 	telegram_send.send(messages=["***Failed to fulfill order!***"])
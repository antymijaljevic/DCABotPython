# written by antymijaljevic@gmail.com

# necessary libraries and API key variables
import ccxt, telegram_send, schedule, time, gspread, re
from datetime import datetime
from keys import API_KEY, SECRET


# call on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})

# set TRUE for the binance testnet and change to the API testnet key
# exchange.set_sandbox_mode(True)


# variables to be set up manually by a user needs
Conversion_1 = 'BTC/BUSD' # put here you conversion pair 1
Conversion_2 = 'SOL/BUSD' # put here you conversion pair 2
matchCon_1 = re.search(r'([A-Z]*)/([A-Z]*)', Conversion_1)
matchCon_2 = re.search(r'([A-Z]*)/([A-Z]*)', Conversion_2)
Conversion_1FirstTicker = matchCon_1.group(1)
Conversion_1SecondTicker = matchCon_1.group(2)
Conversion_2FirstTicker = matchCon_2.group(1)
Conversion_2SecondTicker = matchCon_2.group(2)
orderTime = '01:00' # at what time you want to execute buying order?
orderInvestment = 10 # how much you want to invest?
dipInvestment = 20 # how much you want to invest during a dip?
dipPercentage = 12 # here you set the depth of a dip
checkForDip = 8 # dip check frequency (in hours)
walletBalanceCheck = "12:00" # at what time you want to get wallet balance report?


# call on the google spreadsheet API, specific sheets and appending report into the sheet
def sendSheetReport(sheetNum, reportNum, p_1, p_2, p_3, p_4=None, p_5=None, p_6=None, p_7=None):
    spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
    spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
    sheet = spreadsheet_id.get_worksheet(sheetNum)
    sheetReports =[
        [p_1[:19], p_2, str(p_3)], # spot wallet report
        [p_1[:19], p_2, str(p_3)+"%", p_4], # dip alert
        [p_1[:19], p_2, p_3, p_4, p_5, p_6, str(p_7)+"%"] # buying order conversion pair
    ]
    # append as new row
    sheet.append_row(sheetReports[reportNum])


# spot wallet balance
def walletBalance():
    now = str(datetime.now())
    # the balance of your spot wallet (will print all tickers that exist on the binanace)
    balance = exchange.fetch_total_balance()
    balances = {
        Conversion_1FirstTicker: float(balance[Conversion_1FirstTicker]),
        Conversion_1SecondTicker: int(balance[Conversion_1SecondTicker]),
        Conversion_2FirstTicker: float(balance[Conversion_2FirstTicker]),
        Conversion_2SecondTicker: int(balance[Conversion_2SecondTicker])
    }

    for ticker, balance in balances.items():
        # sending reports to the telegram and to the spreadsheet
        sendSheetReport(3, 0, now, ticker, balance)
        telMsg = "***SPOT WALLET BALANCE***\n\nDate: "+now[:19]+"\n"+ticker+" = "+str(balance)+" "+ticker[:1]
        telegram_send.send(messages=[telMsg])

    print("SPOT WALLET BALANCE ... SENT", now[:19])

# dip alert
def dipAlert():
    now = str(datetime.now())
    # all informations about specific conversion pair
    conversion_1Info = exchange.fetch_ticker(Conversion_1)
    conversion_2Info = exchange.fetch_ticker(Conversion_2)
    conversion_1InfoPrice= conversion_1Info['last']
    conversion_2InfoPrice= conversion_2Info['last']
    pairsPer = {Conversion_1FirstTicker:[round(float(conversion_1Info['info']['priceChangePercent']), 2), conversion_1InfoPrice], Conversion_2FirstTicker:[round(float(conversion_2Info['info']['priceChangePercent']), 2), conversion_2InfoPrice]}

    # checking if there is any below set dip percentage
    for ticker, percentage in pairsPer.items():
        if percentage[0] < dipPercentage:
            if ticker in Conversion_1:
                pricePerIn = Conversion_1SecondTicker
            else:
                pricePerIn = Conversion_2SecondTicker

            # sending the reports to a telegram and the spreadsheet (only for the tickers below set dip percentage)
            sendSheetReport(2, 1, now, ticker, percentage[0], percentage[1])
            telMsg = "***DIP ALERT!***\n\nDate: "+now[:19]+"\n"+ticker+" >>  "+str(percentage[0])+"%"+" at price "+ str(percentage[1])+" ("+pricePerIn+")"
            telegram_send.send(messages=[telMsg])
            print(ticker+" DIP ALERT ... BUYING REQUEST HAS BEEN SENT", now[:19])
            order(ticker+"/"+pricePerIn, dipInvestment)
            print(ticker + " DIP BUYING ORDER HAS BEEN EXECUTED", now[:19])
        else:
            print(ticker + ", NO DIP, STATUS... OK", now[:19])


def order(symbol, theInvestment):
    now = str(datetime.now())
    #sheet change
    if symbol != Conversion_1:
        sheet = 1
    else:
        sheet = 0
    # order parameters
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = theInvestment
    # request order and get info about conversion
    currentTickerInfo = exchange.fetch_ticker(symbol)
    dataBinance = exchange.create_order(symbol, type, side, amount, price)
    tickerPercentage = round(float(currentTickerInfo['info']['priceChangePercent']), 2)
    marketPrice = round(dataBinance['trades'][0]['price'], 2) 
    invested = round(float(dataBinance['cost']), 2)
    commission = float(dataBinance['trades'][0]['info']['commission'])
    assetQty = float(dataBinance['trades'][0]['info']['qty'])
    ticker = dataBinance['trades'][0]['info']['commissionAsset']
   
    # sending report to telegram and spreadsheet
    sendSheetReport(sheet, 2, now, marketPrice, invested, commission, assetQty, ticker, tickerPercentage)
    telMsg = "***BUYING ORDER FULFILLED***\n\n"+"Date: "+now[:19]+"\nAt market price: "+str(marketPrice)+" $\n"+"Coin quantity: "+str(assetQty)+" "+ticker+"\n"+"Invested: "+str(invested)+ " $"
    telegram_send.send(messages=[telMsg])
    print(ticker + " ORDER FULFILLED ... DONE", now[:19])


# #schedule specific time for each function
# #wallet balance
# schedule.every().day.at(walletBalanceCheck).do(walletBalance)
# # dip alert
# schedule.every(checkForDip).hours.do(dipAlert)
# # order 1
# schedule.every().day.at(orderTime).do(order, Conversion_1, orderInvestment)
# # order 2
# schedule.every().day.at(orderTime).do(order, Conversion_2, orderInvestment)
schedule.every(5).seconds.do(walletBalance)

while True:
    schedule.run_pending()
    time.sleep(1)
# written by antymijaljevic@gmail.com
# September 2021

# necessary libraries and API key variables
import ccxt, telegram_send, schedule, time, gspread, re
from datetime import datetime
import config


# call on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_SECRET_KEY,
    'enableRateLimit': True,
})

# set TRUE for the binance testnet and change to the API testnet key
# exchange.set_sandbox_mode(True)

# prevents from buying same dip percentage multiple times on a same day
stamp = []


# variables to be set up manually by a user needs
Conversion_1 = 'ADA/BUSD' # put here you conversion pair 1
Conversion_2 = 'SOL/BUSD' # put here you conversion pair 2
matchCon_1 = re.search(r'([A-Z]*)/([A-Z]*)', Conversion_1)
matchCon_2 = re.search(r'([A-Z]*)/([A-Z]*)', Conversion_2)
Conversion_1FirstTicker = matchCon_1.group(1)
Conversion_1SecondTicker = matchCon_1.group(2)
Conversion_2FirstTicker = matchCon_2.group(1)
Conversion_2SecondTicker = matchCon_2.group(2)
walletBalanceCheck = "12:00" # at what time you want to get wallet balance report?
dipPercentage = -10 # here you set the depth of a dip
checkForDip = 15 # dip check frequency (in minutes)
dipInvestment = 25 # how much you want to invest during a dip?
buyingOrder_1Time = '01:00' # at what time you want to execute first buying order?
buyingOrder_2Time = '01:00' # at what time you want to execute second buying order?
orderInvestment_1 = 11 # how much you want to invest in order 1?
orderInvestment_2 = 11 # how much you want to invest in order 2?

# trying more times to get response from Binance API
def binanceAPI(response):
    now = str(datetime.now())
    while True:
        try:
            data = response
            break
        except ccxt.NetworkError as e:
            print(exchange.id, 'Binance API error :'+now[:19], str(e))
            time.sleep(1)
    return data

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
    # current timestamp + day of a week
    now = str(datetime.now())
    day = datetime.today().strftime('%A')
    # the balance of your spot wallet (will print all tickers that exist on the binanace)
    balance = binanceAPI(exchange.fetch_total_balance())

    balances = {
        Conversion_1FirstTicker: float(balance[Conversion_1FirstTicker]),
        Conversion_1SecondTicker: int(balance[Conversion_1SecondTicker]),
        Conversion_2FirstTicker: float(balance[Conversion_2FirstTicker]),
        Conversion_2SecondTicker: int(balance[Conversion_2SecondTicker])
    }

    # collect all the reports
    telMsgAll = "***SPOT WALLET BALANCE***\n\nDate: "+now[:19]
    for ticker, balance in balances.items():
        # sending reports to the telegram and to the spreadsheet
        sendSheetReport(3, 0, now, ticker, balance)
        telMsg = "\n"+ticker+" = "+str(balance)+" "+ticker[:1]
        telMsgAll += telMsg
        
    telegram_send.send(messages=[telMsgAll])
    print("SPOT WALLET BALANCE ... SENT", now[:19])

    if day == "Monday":
        telegram_send.send(messages=["It's "+day+"! It's staking time!"])
        print("STAKING REMINDER ... SENT", now[:19])

# dip alert
def dipAlert():
    global stamp
    now = str(datetime.now())
    # all informations about specific conversion pair
    conversion_1Info = binanceAPI(exchange.fetch_ticker(Conversion_1))
    conversion_2Info = binanceAPI(exchange.fetch_ticker(Conversion_2))
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
            print(ticker+" DIP ALERT ... SENT", now[:19])

            # remove stamps from previous day and start with empty list for a new day
            if now[8:10] != stamp[0][8:10]:
                stamp = []
            # buy each dip percentage staring from -10 only once per day
            stampCreate = now[:10]+ticker+str(int(percentage[0]))
            if stampCreate not in stamp:
                stamp.append(stampCreate)
                order(ticker+"/"+pricePerIn, dipInvestment)
                print(ticker + " DIP BUYING ORDER HAS BEEN REQUESTED AT "+str(int(percentage[0]))+"%","TIME: "+now[:19])
        else:
            print(ticker + ", NO DIP, STATUS... OK", now[:19])


def order(symbol, theInvestment):
    now = str(datetime.now())
    # sheet change
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
    currentTickerInfo = binanceAPI(exchange.fetch_ticker(symbol))
    orderDataBinance = binanceAPI(exchange.create_order(symbol, type, side, amount, price))
    tickerPercentage = round(float(currentTickerInfo['info']['priceChangePercent']), 2)
    marketPrice = round(orderDataBinance['trades'][0]['price'], 2) 
    invested = round(float(orderDataBinance['cost']), 2)
    commission = float(orderDataBinance['trades'][0]['info']['commission'])
    assetQty = float(orderDataBinance['trades'][0]['info']['qty'])
    ticker = orderDataBinance['trades'][0]['info']['commissionAsset']
   
    # sending report to telegram and spreadsheet
    sendSheetReport(sheet, 2, now, marketPrice, invested, commission, assetQty, ticker, tickerPercentage)
    telMsg = "***BUYING ORDER FULFILLED***\n\n"+"Date: "+now[:19]+"\nAt market price: "+str(marketPrice)+" $\n"+"Coin quantity: "+str(assetQty)+" "+ticker+"\n"+"Invested: "+str(invested)+ " $"+"\n"+"24h%: "+str(tickerPercentage)+"%"
    telegram_send.send(messages=[telMsg])
    print(ticker + " ORDER FULFILLED ... DONE", now[:19])


# schedule specific time for each function
# wallet balance
schedule.every().day.at(walletBalanceCheck).do(walletBalance)
#schedule.every(15).seconds.do(walletBalance)
# dip alert
#schedule.every(5).seconds.do(dipAlert)
schedule.every(checkForDip).minutes.do(dipAlert)
# order 1
schedule.every().day.at(buyingOrder_1Time).do(order, Conversion_1, orderInvestment_1)
#schedule.every(10).seconds.do(order, Conversion_1, orderInvestment_1)
# order 2  # only if needed
# schedule.every().day.at(buyingOrder_2Time).do(order, Conversion_2, orderInvestment_2)
# schedule.every(60).seconds.do(order, Conversion_2, orderInvestment_2)

while True:
    schedule.run_pending()
    time.sleep(1)
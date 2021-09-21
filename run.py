# written by antymijaljevic@gmail.com

# necessary libraries and API keys variables
import ccxt, telegram_send, schedule, time, multiprocessing, gspread
from datetime import datetime
from keys import API_KEY, SECRET


# call on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET,
    'enableRateLimit': True,
})
# set TRUE for the binance testnet, and set test pairs
exchange.set_sandbox_mode(False)
# orderPair_1 = 'BTC/BUSD'
# orderPair_2 = 'ETH/BUSD'


# to be set up manually depends about user needs
# trading variables for order function
orderPair_1 = 'ADA/BUSD' # bug 1 regEx
orderPair_2 = 'ETH/BUSD'
orderTime = '01:15'
orderInvestment = 10


# call on the google spreadsheet, specific sheets and appending report into the sheet
def sendSheetReport(sheetNum, reportNum, p_1, p_2, p_3, p_4=None, p_5=None, p_6=None):
    spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
    spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
    sheet = spreadsheet_id.get_worksheet(sheetNum)
    sheetReports =[
        [p_1[:19], p_2, str(p_3)+"$"], # spot wallet
        [p_1[:19], p_2, str(p_3)+"%", p_4], # dip alert
        [p_1[:19], p_2, p_3, p_4, p_5, p_6] # buying order
    ]
    sheet.append_row(sheetReports[reportNum])


# spot wallet balance
def walletBalance():
    now = str(datetime.now())
    balance = exchange.fetch_total_balance()
    busdTicker = orderPair_1[4:] #str
    usdBalance = int(balance[busdTicker]) #float
    pairOneTicker = orderPair_1[:3] #str
    pairOneBalance = float(balance[pairOneTicker]) #float
    pairTwoTicker = orderPair_2[:3] #str
    pairTwoBalance = float(balance[pairTwoTicker]) #float

    # sending report to telegram and spreadsheet
    sendSheetReport(3, 0, now, busdTicker, usdBalance)
    telMsg = "***SPOT WALLET BALANCE***\n\nDate: "+now[:19]+"\n"+busdTicker+" = "+str(usdBalance)+"$\n"+pairOneTicker+" = "+str(pairOneBalance)+" "+pairOneTicker[:1]+"\n"+pairTwoTicker+" = "+str(pairTwoBalance)+" "+pairTwoTicker[:1]
    telegram_send.send(messages=[telMsg])
    print("SPOT WALLET BALANCE ... SENT", now[:19])


# dip alert
def dipAlert():
    now = str(datetime.now())
    pairOneInfo = exchange.fetch_ticker(orderPair_1)
    pairTwoInfo = exchange.fetch_ticker(orderPair_2)
    pairOnePrice= round(pairOneInfo['last'], 2)
    pairTwoPrice= round(pairTwoInfo['last'], 2)
    pairsPer = {orderPair_1[:3]:[round(float(pairOneInfo['info']['priceChangePercent']), 2), pairOnePrice], orderPair_2[:3]:[round(float(pairTwoInfo['info']['priceChangePercent']), 2), pairTwoPrice]}

    for key, value in pairsPer.items():
        if value[0] < -10:
            ticker = key
            percentage = value[0]
            price = value[1]
            # sending report to telegram and spreadsheet
            sendSheetReport(2, 1, now, ticker, percentage, price)
            telMsg = "***DIP ALERT!***\n\nDate: "+now[:19]+"\n"+ticker+" >>  "+str(percentage)+"%"+" at price "+ str(price)+"$"
            telegram_send.send(messages=[telMsg])
            print(key+" DIP ALERT ... SENT", now[:19])
        else:
            print(key + ", NO EXTREME DIPS. SCRIPT ... RUNNING", now[:19])


def order(thePair=None, theInvestment=None):
    now = str(datetime.now())
    #sheet change
    if thePair != 'ADA/BUSD':
        sheet = 1
    else:
        sheet = 0
    # order parameters
    symbol = thePair
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = theInvestment
    # request order
    dataBinance = exchange.create_order(symbol, type, side, amount, price)
    marketPrice = round(dataBinance['trades'][0]['price'], 2) 
    invested = round(float(dataBinance['cost']), 2)
    commission = float(dataBinance['trades'][0]['info']['commission'])
    assetQty = float(dataBinance['trades'][0]['info']['qty'])
    ticker = dataBinance['trades'][0]['info']['commissionAsset']
   
    # sending report to telegram and spreadsheet
    sendSheetReport(sheet, 2, now, marketPrice, invested, commission, assetQty, ticker)
    telMsg = "***BUYING ORDER FULFILLED***\n\n"+"Date: "+now[:19]+"\nAt market price: "+str(marketPrice)+" $\n"+"Coin quantity: "+str(assetQty)+" "+ticker+"\n"+"Invested: "+str(invested)+ " $"
    telegram_send.send(messages=[telMsg])
    print(ticker + " ORDER FULFILLED ... DONE", now[:19])


#schedule specific time for each function
#wallet balance
schedule.every(24).hours.do(walletBalance)
# dip alert
schedule.every(12).hours.do(dipAlert)
# order 1
schedule.every().day.at(orderTime).do(order, orderPair_1, orderInvestment)
# order 2
schedule.every().day.at(orderTime).do(order, orderPair_2, orderInvestment)

# # schedule specific time for each function
# schedule.every(9).seconds.do(walletBalance)
# schedule.every(9).seconds.do(dipAlert)
# schedule.every(9).seconds.do(order, orderPair_1, orderInvestment)
# schedule.every(9).seconds.do(order, orderPair_2, orderInvestment)

while True:
    schedule.run_pending()
    time.sleep(1)
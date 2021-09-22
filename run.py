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
# set TRUE for the binance testnet, set test pairs and change to API test key
# exchange.set_sandbox_mode(True)
# orderPair_1 = 'BTC/BUSD'
# orderPair_2 = 'ETH/BUSD'


# to be set up manually depends about user needs
# trading variables for order function
orderPair_1 = 'ADA/BUSD' # bug 1 regEx
orderPair_2 = 'ETH/BUSD'
orderTime = '01:00'
orderInvestment = 10


# call on the google spreadsheet, specific sheets and appending report into the sheet
def sendSheetReport(sheetNum, reportNum, p_1, p_2, p_3, p_4=None, p_5=None, p_6=None):
    spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
    spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
    sheet = spreadsheet_id.get_worksheet(sheetNum)
    sheetReports =[
        [p_1[:19], p_2, str(p_3)+"$"], # spot wallet
        [p_1[:19], p_2, str(p_3)+"%", p_4], # dip alert
        [p_1[:19], p_2, p_3, p_4, p_5, p_6] # buying order pair one and two
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
        if value[0] < 3:
            ticker = key
            percentage = value[0]
            price = value[1]
            # sending report to telegram and spreadsheet
            sendSheetReport(2, 1, now, ticker, percentage, price)
            telMsg = "***DIP ALERT!***\n\nDate: "+now[:19]+"\n"+ticker+" >>  "+str(percentage)+"%"+" at price "+ str(price)+"$"
            telegram_send.send(messages=[telMsg])
            print(key+" DIP ALERT ... BUYING REQUEST HAS BEEN SENT", now[:19])
            order(ticker+"/BUSD", 60)
            print(ticker + " DIP BUYING ORDER HAS BEEN EXECUTED", now[:19])
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
    #for testing only
    # dataBinance = {
    #     'info': {'symbol': 'ETHBUSD', 'orderId': '574926833', 'orderListId': '-1', 'clientOrderId': 'x-R4BD3S821058420866ddf407f78d90', 'transactTime': '1632210699815', 'price': '0.00000000', 'origQty': '4.70000000', 'executedQty': '4.70000000', 'cummulativeQuoteQty': '69.99220000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '2.12600000', 'qty': '4.70000000', 'commission': '0.00470000', 'commissionAsset': 'ETH', 'tradeId': '52730974'}]},
    #     'timestamp': 1632210699815, 'datetime': 
    #     '2021-09-21T07:51:39.815Z', 
    #     'price': 2.126,  
    #     'amount': 4.7, 
    #     'cost': 69.2222, 
    #     'average': 2.126, 
    #     'filled': 4.7, 
    #     'fee': {'cost': 0.0047, 'currency': 'ETH'}, 
    #     'trades': [{'info': {'price': '2.12600000', 'qty': '4.70000000', 'commission': '0.00470000', 'commissionAsset': 'ETH', 'tradeId': '52730974'}, 'timestamp': None, 'datetime': None, 'symbol': 'ETH/BUSD', 'id': None, 'order': None, 'type': None, 'side': None, 'takerOrMaker': None, 'price': 2.126, 'amount': 4.7, 'cost': 69.2222, 'fee': {'cost': 0.0047, 'currency': 'ETH'}}], 'fees': [{'cost': 0.0047, 'currency': 'ETH'}]
    # }

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


# #schedule specific time for each function
#wallet balance
schedule.every(24).hours.do(walletBalance)
# dip alert
schedule.every(12).hours.do(dipAlert)
# order 1
schedule.every().day.at(orderTime).do(order, orderPair_1, orderInvestment)
# order 2
schedule.every().day.at(orderTime).do(order, orderPair_2, orderInvestment)

# # schedule specific time for each function
# schedule.every(10).minutes.do(walletBalance)
#schedule.every(10).seconds.do(dipAlert)
# schedule.every(10).seconds.do(order, orderPair_1, orderInvestment)
# schedule.every(10).seconds.do(order, orderPair_2, orderInvestment)

while True:
    schedule.run_pending()
    time.sleep(1)
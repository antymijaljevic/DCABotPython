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
# orderOnePair = 'BTC/BUSD'
# orderTwoPair = 'ETH/BUSD'

# timestamp
now = str(datetime.now())

# to be set up manually depends about user needs
# trading pairs set up
orderOnePair = 'ADA/BUSD' # bug 1 regEx
orderTwoPair = 'ETH/BUSD'
# investment amount
orderOneInvestment = 10
orderTwoInvestment = 10


# call on the google spreadsheet, specific sheets and appending report into the sheet
def sendSheetReport(sheetNum, reportNum, p_1, p_2, p_3, p_4, p_5, p_6):
    spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
    spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
    sheet = spreadsheet_id.get_worksheet(sheetNum)
    sheetReports =[
        [p_1[:19], p_2, str(p_3)+"$"], # spot wallet (testing phase)
        [p_1[:19], p_2, str(p_3)+"%", p_4], # dip alert
        [p_1[:19], p_2, p_3, p_4, p_5, p_6] # buying order one
    ]
    sheet.append_row(sheetReports[reportNum])


# sending message report to the telegram bot
def sendTelReport(reportNo, p_1, p_2, p_3, p_4, p_5, p_6, p_7):
    telReports = [
        "***SPOT WALLET BALANCE***\n\nDate: "+p_1[:19]+"\n"+p_2+" = "+str(p_3)+"$\n"+p_4+" = "+str(p_5)+" "+p_4[:1]+"\n"+p_6+" = "+str(p_7)+" "+p_6[:1],
        "***DIP ALERT!***\n\nDate: "+p_1[:19]+"\n"+p_2+">>  "+str(p_3)+"%"+" at price "+ str(p_4)+"$",
        "***BUYING ORDER FULFILLED***\n\n"+"Date: "+p_1[:19]+"\nAt market price: "+str(p_2)+" $\n"+"Coin quantity: "+str(p_3)+" "+ p_4+"\n"+"Invested: "+str(p_5)+ " $",
    ]
    telegram_send.send(messages=[telReports[reportNo]])


# spot wallet balance
def walletBalance():
    balance = exchange.fetch_total_balance()
    busdTicker = orderOnePair[4:] #str
    usdBalance = int(balance[busdTicker]) #float
    pairOneTicker = orderOnePair[:3] #str
    pairOneBalance = float(balance[pairOneTicker]) #float
    pairTwoTicker = orderTwoPair[:3] #str
    pairTwoBalance = float(balance[pairTwoTicker]) #float

    # sending report to telegram and spreadsheet
    sendSheetReport(3, 0, now, busdTicker, usdBalance, "0", "0", "0")
    sendTelReport(0, now, busdTicker, usdBalance, pairOneTicker, pairOneBalance, pairTwoTicker, pairTwoBalance)
    print("SPOT WALLET BALANCE ... SENT", now[:19])


# dip alert
def dipAlert():
    pairOneInfo = exchange.fetch_ticker(orderOnePair)
    pairTwoInfo = exchange.fetch_ticker(orderTwoPair)
    pairOnePrice= round(pairOneInfo['last'], 2)
    pairTwoPrice= round(pairTwoInfo['last'], 2)
    pairsPer = {orderOnePair[:3]:[round(float(pairOneInfo['info']['priceChangePercent']), 2), pairOnePrice], orderTwoPair[:3]:[round(float(pairTwoInfo['info']['priceChangePercent']), 2), pairTwoPrice]}

    for key, value in pairsPer.items():
        if value[0] < -10:
            # sending report to telegram and spreadsheet
            sendSheetReport(2, 1, now, key, value[0], value[1], "0", "0")
            sendTelReport(1, now, key, value[0],value[1], "0", "0")
            print(key+" DIP ALERT ... SENT", now[:19])
        else:
            print(key + ", NO EXTREME DIPS. SCRIPT ... RUNNING", now[:19])


def buyingOrder1():
    # order parameters
    symbol = orderOnePair
    type = 'market'  # or 'limt'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore this one
    price = orderOneInvestment
    # request order
    # dataBinance = exchange.create_order(symbol, type, side, amount, price)
    dataBinance = {'info': {'symbol': 'ADABUSD', 'orderId': '574926833', 'orderListId': '-1', 'clientOrderId': 'x-R4BD3S821058420866ddf407f78d90', 'transactTime': '1632210699815', 'price': '0.00000000', 'origQty': '4.70000000', 'executedQty': '4.70000000', 'cummulativeQuoteQty': '9.99220000', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'fills': [{'price': '2.12600000', 'qty': '4.70000000', 'commission': '0.00470000', 'commissionAsset': 'ADA', 'tradeId': '52730974'}]}, 'id': '574926833', 'clientOrderId': 'x-R4BD3S821058420866ddf407f78d90', 'timestamp': 1632210699815, 'datetime': '2021-09-21T07:51:39.815Z', 'lastTradeTimestamp': None, 'symbol': 'ADA/BUSD', 'type': 'market', 'timeInForce': 'GTC', 'postOnly': False, 'side': 'buy', 'price': 2.126, 'stopPrice': None, 'amount': 4.7, 'cost': 9.9922, 'average': 2.126, 'filled': 4.7, 'remaining': 0.0, 'status': 'closed', 'fee': {'cost': 0.0047, 'currency': 'ADA'}, 'trades': [{'info': {'price': '2.12600000', 'qty': '4.70000000', 'commission': '0.00470000', 'commissionAsset': 'ADA', 'tradeId': '52730974'}, 'timestamp': None, 'datetime': None, 'symbol': 'ADA/BUSD', 'id': None, 'order': None, 'type': None, 'side': None, 'takerOrMaker': None, 'price': 2.126, 'amount': 4.7, 'cost': 9.9922, 'fee': {'cost': 0.0047, 'currency': 'ADA'}}], 'fees': [{'cost': 0.0047, 'currency': 'ADA'}]}
    marketPrice = round(dataBinance['trades'][0]['price'], 2) # float market price 
    invested = round(dataBinance['cost'], 2) # float invested
    commission = float(dataBinance['trades'][0]['info']['commission']) # str commission
    assetQty = float(dataBinance['trades'][0]['info']['qty']) #str asset qty.
    ticker = dataBinance['trades'][0]['info']['commissionAsset'] #str name of asset
   
    # sending report to telegram and spreadsheet
    sendSheetReport(0, 2, now, marketPrice, invested, commission, assetQty, ticker)
    sendTelReport(2, now, marketPrice, assetQty, ticker, invested, "0")




# test zone
walletBalance()
# dipAlert()
# buyingOrder1()
time.sleep(10)
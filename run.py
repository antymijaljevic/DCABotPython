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
exchange.set_sandbox_mode(True)
orderOnePair = 'BTC/BUSD' # bug 1 regEx
orderTwoPair = 'ETH/BUSD'

# timestamp
now = str(datetime.now())

# to be set up manually depends about user needs
# trading pairs set up
# orderOnePair = 'ADA/BUSD'
# orderTwoPair = 'ETH/BUSD'
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
        [p_1[:19], float(p_2), p_3, p_4, p_5, p_6[:3]] # buying order one
    ]
    sheet.append_row(sheetReports[reportNum])


# sending message report to the telegram bot
def sendTelReport(reportNo, p_1, p_2, p_3, p_4, p_5, p_6):
    telReports = [
        "***SPOT WALLET BALANCE***\n\nDate: "+p_1[:19]+"\n"+p_2[4:]+" = "+str(p_3)+"$\n"+p_2[:3]+" = "+str(p_4)+p_2[:1]+"\n"+p_5[:3]+" = "+str(p_6)+p_5[:1],
        "***DIP ALERT!***\n\nDate: "+p_1[:19]+"\n"+p_2+">>  "+str(p_3)+"%"+" at price "+ str(p_4)+"$",
        "***BUYING ORDER FULFILLED***\n\n"+"Date: "+p_1[:19]+"\nFilled at: "+str(p_2)+"\n"+" $\n"+"Coin quantity: "+str(p_3)+" "+ p_4[:1]+"\n"+"Invested: "+str(p_5)+ " $",
    ]
    telegram_send.send(messages=[telReports[reportNo]])


# spot wallet balance
def walletBalance():
    balance = exchange.fetch_total_balance()
    # sending report to telegram and spreadsheet
    sendSheetReport(3, 0, now, orderOnePair[4:], int(balance[orderOnePair[4:]]), "0", "0", "0") #ONLY FOR TESTING PURPOSES
    sendTelReport(0, now, orderOnePair, int(balance[orderOnePair[4:]]), int(balance[orderOnePair[:3]]), orderTwoPair, int(balance[orderTwoPair[:3]]))
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
    dataBinance = exchange.create_order(symbol, type, side, amount, price)
    filledAt = dataBinance['info']['fills'][0]['price'] # bug 2 float not allowed?
    commissionRate = dataBinance['info']['fills'][0]['commission']
    invested = dataBinance['cost'] # bug 3 float not allowed?
    assetQty = dataBinance['amount']

    # sending report to telegram and spreadsheet
    sendSheetReport(0, 2, now, filledAt, invested, commissionRate, assetQty, symbol)
    sendTelReport(2, now, filledAt, assetQty, symbol, invested, "0")



# test zone
# walletBalance()
# dipAlert()
buyingOrder1()
time.sleep(5)
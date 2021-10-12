from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.helpers import round_step_size
import config, json, telegram_send, schedule, gspread, time
from datetime import datetime
from os import system


class Binance():
    def __init__(self):
        #clear terminal
        system('cls')
        # coin/token pair to buy
        self.token = 'LINK'
        self.stableCoin = 'BUSD'
        self.pair = self.token+self.stableCoin
        # stable coin value to buy or sell
        self.stableValue = 10.5
        # alert percentage
        self.alertPer = -10

        # time schedule
        self.walletTime = '12:00'
        self.buyTime = '01:00'
        self.sellTime = '01:00'
        self.alertTime = 5 # in min



    # connecting on google ss
    def sendReports(self, sheetNum, reportNum, p_1, p_2=None, p_3=None, p_4=None, p_5=None, p_6=None, p_7=None):
        #current date&time
        now = str(datetime.now())

        # google ss api
        spreadsheet_credentials = gspread.service_account(filename='sheet_credentials.json')
        spreadsheet_id = spreadsheet_credentials.open_by_key('1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY')
        sheet = spreadsheet_id.get_worksheet(sheetNum)

        # sheet reports
        sheetReports =[
            [p_1, p_2, p_3, p_4, p_5, p_6, str(p_7)+"%"], # buying orders
            [p_1, p_2, p_3, p_4, p_5, p_6, str(p_7)+"%"], # selling orders
            [str(p_1)+"\n"+now[:19]], # spot wallet report
            [now[:19], p_1, str(p_2)+"$", str(p_3)+"%"], # dip alerts
            ["CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19]] # error loger
        ]

        # telegram notifications
        telegramReports = [
            ["***BUYING ORDER FULFILLED***\n\nAt market price: "+str(p_2)+" $"+"\nCoin quantity: "+str(p_5)+" "+str(p_6)+"\nInvested: "+str(p_3)+ " $\nPercentage: "+str(p_7)+"%\n\n"+now[:19]], # buying order
            ["***SELLING ORDER FULFILLED***\n\nSold at market price: "+str(p_2)+" $"+"\nCoin quantity sold: "+str(p_5)+" "+str(p_6)+"\nValue sold: "+str(p_3)+ " $\nPercentage: "+str(p_7)+"%\n\n"+now[:19]], # selling order
            ["***SPOT WALLET BALANCE***\n\n"+str(p_1)+"\n"+now[:19]], # spot wallet report
            ["***DIP ALERT***\n\n"+p_1+"\n"+str(p_2)+"$\n"+str(p_3)+"%\n\n"+now[:19]], # dip alert
            ["CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19]] # error loger
        ]

        # terminal notifications
        terNot = [
            "BUYING ORDER EXECUTED ... "+now[:19], # buying order
            "SELLING ORDER EXECUTED ... "+now[:19], # selling order
            "SPOT WALLET BALANCE HAS BEEN SENT ... "+now[:19], # spot wallet report
            "DIP ALERT TRIGGERED "+p_1+ "... "+now[:19], # dip alert
            "CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19] # error loger
        ]

        # append report to sheet
        sheet.append_row(sheetReports[reportNum])
        # send telegram notification
        telegram_send.send(messages=telegramReports[reportNum])
        # program status
        print(terNot[reportNum])


    # get response from API
    def apiCall(self, method):
        # connect on binance exchange
        self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY) #, testnet=True
        while True:
            try:
                response = method()
                break
            except BinanceAPIException as e:
                self.sendReports(4, 4, e.status_code, e.message)
                # try every 5 min
                time.sleep(300)

        # print(json.dumps(response, indent=2))
        return response


    # get ceiling value of coin/token
    def getCeilingVal(self):
        pairData = self.apiCall(lambda: self.client.get_symbol_ticker(symbol=self.pair))
        pairPrice = pairData["price"]
        ceilingVal = float(self.stableValue) / float(pairPrice)

        # round qty decimals to match a lot size
        aLotSize = self.getLotSize()
        rounded_amount = round_step_size(ceilingVal, aLotSize)

        # print(rounded_amount)
        return rounded_amount


    # get pair percentage
    def getPercentage(self):
        pairData = self.apiCall(lambda: self.client.get_ticker(symbol=self.pair))
        pairPer = round(float(pairData['priceChangePercent']), 2)
        # print(pairPer)
        return pairPer


    # get a lot size
    def getLotSize(self):
        info = self.apiCall(lambda: self.client.get_symbol_info(self.pair))
        lotSize = float(info['filters'][2]['minQty'])
        # print(lotSize)
        return lotSize


    # get account balance
    def spotWalletBalance(self):
        spotWallet = self.apiCall(lambda: self.client.get_account())
        balance = spotWallet["balances"]
        # get only free spot wallet balance
        balanceReport = ''
        for x in balance:
            if float(x['free']) > 0:
                quantity = round(float(x['free']), 2)
                balanceReport += x['asset']+": "+str(quantity)+"\n"

        # send reports
        self.sendReports(2, 2, balanceReport)

    
    # buy market order
    def buyMarket(self):
        # make market buy order
        orderData = self.apiCall(lambda: self.client.order_market_buy(symbol=self.pair, quantity=self.getCeilingVal()))

        # convert unix time
        unixTime = int(orderData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        filledAt = round(float(orderData['fills'][0]['price']), 2)
        invested = round(float(orderData['cummulativeQuoteQty']), 2)
        commission = float(orderData['fills'][0]['commission'])
        assetQty = float(orderData['fills'][0]['qty'])
        assetTicker = self.token
        currentPer = self.getPercentage()

        self.sendReports(0, 0, date, filledAt, invested, commission, assetQty, assetTicker, currentPer)


    # sell market order
    def sellMarket(self):
        # make market buy order
        orderData = self.apiCall(lambda: self.client.order_market_sell(symbol=self.pair, quantity=self.getCeilingVal()))

        # convert unix time
        unixTime = int(orderData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        soldAt = round(float(orderData['fills'][0]['price']), 2)
        valueSold = round(float(orderData['cummulativeQuoteQty']), 2)
        commission = float(orderData['fills'][0]['commission'])
        assetQtySold = float(orderData['fills'][0]['qty'])
        assetTicker = self.token
        currentPer = self.getPercentage()

        self.sendReports(1, 1, date, soldAt, valueSold, commission, assetQtySold, assetTicker, currentPer)


    # dip alert
    def dipAlert(self):
        # list of coins/token to be alerted
        pairList = ['BTCBUSD', 'ETHBUSD', 'ADABUSD', 'SOLBUSD', 'XRPBUSD', 'BNBBUSD', 'DOTBUSD', 'LINKBUSD']
        info = self.apiCall(lambda: self.client.get_ticker())

        # get those below -9.90
        for pair in info:
            if pair['symbol'] in pairList and float(pair['priceChangePercent']) < self.alertPer:
                symbol, percentage, price = pair['symbol'], round(float(pair['priceChangePercent']), 2), round(float(pair['lastPrice']), 2)
                # send reports
                self.sendReports(3, 3, symbol, price, percentage)

                # NEXT BUY OR SELL THE DIP ALGORITHM


if __name__ == "__main__":
    bot = Binance()
    # FOR TESTING ONLY

    # bot.getCeilingVal()
    # bot.getPercentage()
    # bot.getLotSize()
    # bot.spotWalletBalance()
    # bot.buyMarket()
    # bot.sellMarket()
    # bot.dipAlert()

    # spot wallet
    schedule.every().day.at(bot.walletTime).do(bot.spotWalletBalance)
    
    # market buy order
    schedule.every().day.at(bot.buyTime).do(bot.buyMarket)

    # # market sell order
    # schedule.every().day.at(bot.sellTime).do(bot.sellMarket)

    # dip alert
    schedule.every(bot.alertTime).minutes.do(bot.dipAlert)


    while True:
        schedule.run_pending()
        time.sleep(1)
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.helpers import round_step_size
import config, telegram_send, schedule, gspread, time
from datetime import datetime
from os import system


class Binance():
    def __init__(self):
        #clear terminal
        system('cls') # put 'clear' for linux server
        # coin/token pair to buy for DCA
        self.pair = 'ADABUSD'
        # stable coin value to buy or sell
        self.stableValue = 10.5
        # investment on dip
        self.dipInvestment = 20
        # alert percentage
        self.alertPer = -10
        # sell limit percentage
        self.sellLimitPer = 0.03
        # buying history
        self.historyStamps = []

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
            [p_1, str(p_2)+"$", str(p_3)+"$", p_4, str(p_5)+"%", str(p_6)], # dip orders
            [str(p_1)+"\n"+now[:19]], # spot wallet report
            ["CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19]] # error loger
        ]

        # telegram notifications
        telegramReports = [
            ["***BUYING ORDER FULFILLED***\n\nAt market price: "+str(p_2)+" $"+"\nCoin quantity: "+str(p_5)+" "+str(p_6)+"\nInvested: "+str(p_3)+ " $\nPercentage: "+str(p_7)+"%\n\n"+now[:19]], # buying order
            ["***SELLING ORDER FULFILLED***\n\nSold at market price: "+str(p_2)+" $"+"\nCoin quantity sold: "+str(p_5)+" "+str(p_6)+"\nValue sold: "+str(p_3)+ " $\nPercentage: "+str(p_7)+"%\n\n"+now[:19]], # selling order
            ["***DIP ORDER***\n\n"+str(p_4)+"\n"+str(p_7)+" $\n"+str(p_5)+"%\n\n"+now[:19]], # dip orders
            ["***SPOT WALLET BALANCE***\n\n"+str(p_1)+"\n"+now[:19]], # spot wallet report
            ["CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19]] # error loger
        ]

        # terminal notifications
        terNot = [
            "BUYING ORDER EXECUTED ... "+now[:19], # buying order
            "SELLING ORDER EXECUTED ... "+now[:19], # selling order
            "DIP ALERT TRIGGERED "+str(p_4)+ "... "+now[:19], # dip orders
            "SPOT WALLET BALANCE HAS BEEN SENT ... "+now[:19], # spot wallet report
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

        return response


    # get ceiling value of coin/token
    def getCeilingVal(self, pair, investment):
        pairData = self.apiCall(lambda: self.client.get_symbol_ticker(symbol=pair))
        pairPrice = pairData["price"]
        ceilingVal = float(investment) / float(pairPrice)

        # round qty decimals to match a lot size
        aLotSize = self.getLotSize(pair)
        rounded_amount = round_step_size(ceilingVal, aLotSize)

        # print(rounded_amount)
        return rounded_amount
    

    # get a lot size
    def getLotSize(self, pair):
        info = self.apiCall(lambda: self.client.get_symbol_info(pair))
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
        self.sendReports(3, 3, balanceReport)

    
    # buy market order
    def buyMarket(self, pair, investment):
        # make market buy order
        orderData = self.apiCall(lambda: self.client.order_market_buy(symbol=pair, quantity=self.getCeilingVal(pair, investment)))

        # convert unix time
        unixTime = int(orderData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        filledAt = round(float(orderData['fills'][0]['price']), 2)
        invested = round(float(orderData['cummulativeQuoteQty']), 2)
        commission = float(orderData['fills'][0]['commission'])
        assetQty = float(orderData['fills'][0]['qty'])
        assetTicker = pair[:-4]
        perInfoData = self.apiCall(lambda: self.client.get_ticker(symbol=self.pair))
        currentPer = round(float(perInfoData['priceChangePercent']), 2)

        # send report
        self.sendReports(0, 0, date, filledAt, invested, commission, assetQty, assetTicker, currentPer)


    # sell market order
    def sellMarket(self, pair, sellingValue):
        orderData = self.apiCall(lambda: self.client.order_market_sell(symbol=pair, quantity=self.getCeilingVal(pair, sellingValue)))

        # convert unix time
        unixTime = int(orderData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        soldAt = round(float(orderData['fills'][0]['price']), 2)
        valueSold = round(float(orderData['cummulativeQuoteQty']), 2)
        commission = float(orderData['fills'][0]['commission'])
        assetQtySold = float(orderData['fills'][0]['qty'])
        assetTicker = pair[:-4]
        perInfoData = self.apiCall(lambda: self.client.get_ticker(symbol=self.pair))
        currentPer = round(float(perInfoData['priceChangePercent']), 2)

        # send report
        self.sendReports(1, 1, date, soldAt, valueSold, commission, assetQtySold, assetTicker, currentPer)

    
    # buy - limit sell order
    def buyLimitSell(self, pair, buySellValue, atPrice, per, lastPrice):
        # buy market order
        buyData = self.apiCall(lambda: self.client.order_market_buy(symbol=pair, quantity=self.getCeilingVal(pair, buySellValue)))

        # convert unix time
        unixTime = int(buyData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        filledAt = round(float(buyData['fills'][0]['price']), 2)
        invested = round(float(buyData['cummulativeQuoteQty']), 2)
        assetTicker = pair[:-4]
        buyOrSell = buyData['side']
        # send reports
        self.sendReports(2, 2, date, filledAt, invested, assetTicker, per, buyOrSell, lastPrice)

        # place limit sell order
        limitSellData = self.apiCall(lambda: self.client.order_limit_sell(symbol=pair, quantity=self.getCeilingVal(pair, buySellValue-1), price=atPrice))
        sellAt = round(float(limitSellData['price']), 2)
        sellValue = round(float(limitSellData['origQty']) * float(lastPrice), 2)
        buyOrSellorder = limitSellData['side']
        # send reports
        self.sendReports(2, 2, date, sellAt, sellValue, assetTicker, "N/A", "LIMIT "+buyOrSellorder)

    # dip alert
    def dipAlert(self):
        # remove history stamps from previous month
        now = str(datetime.now())
        # list of coins/token to be alerted
        pairList = ['BTCBUSD', 'ETHBUSD', 'ADABUSD', 'SOLBUSD', 'LINKBUSD']
        info = self.apiCall(lambda: self.client.get_ticker())

        # list assets below set minus precentage
        for pair in info:                    
            if pair['symbol'] in pairList and float(pair['priceChangePercent']) < self.alertPer:
                symbol, percentage, price = pair['symbol'], round(float(pair['priceChangePercent']), 2), round(float(pair['lastPrice']), 2)
                # create alert / buying / selling history
                stamp = pair['symbol'] + now[:10]
                if stamp not in self.historyStamps:
                    self.historyStamps.append(stamp)

                    # Buy coin/token on -10% and sell higher
                    sellAtPrice = round(price * (1 + self.sellLimitPer), 2)
                    self.buyLimitSell(symbol, self.dipInvestment, sellAtPrice, percentage, price)

        # remove history stamps from previous month
        if now[5:7] != self.historyStamps[0][-5:-3]:
            self.historyStamps = []


if __name__ == "__main__":
    bot = Binance()
    # FOR TESTING ONLY

    # bot.getCeilingVal()
    # bot.getPercentage()
    # bot.getLotSize()
    # bot.spotWalletBalance()
    # bot.buyMarket(bot.pair, bot.stableValue)
    # bot.sellMarket(bot.pair, bot.stableValue)
    # bot.buyLimitSell()
    # bot.dipAlert()

    #spot wallet
    schedule.every().day.at(bot.walletTime).do(bot.spotWalletBalance)
    
    # market buy order
    schedule.every().day.at(bot.buyTime).do(bot.buyMarket, bot.pair, bot.stableValue)

    # market sell order
    # schedule.every().day.at(bot.sellTime).do(bot.sellMarket, bot.pair, bot.stableValue)

    # dip alert
    schedule.every(bot.alertTime).minutes.do(bot.dipAlert)


    while True:
        schedule.run_pending()
        time.sleep(1)
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
        # spreadsheet credentials filename
        self.ssCredFile = 'sheet_credentials.json'
        # spreadsheet unique ID
        self.ssId = '1e-I7RvxlIU3SvvW4i5OD3GCVPqj5Ka5anDbyUOc93oY'

        # coin/token pair_1 to buy for DCA
        self.pair_1 = 'ADABUSD'
        # stable coin value to buy pair 1
        self.stableValue_1 = 10.2
        # time to buy pair 1
        self.buyTime_1 = '01:00'

        # coin/token pair_2 to buy for DCA
        self.pair_2 = 'BTCBUSD'
        # stable coin value to buy pair 2
        self.stableValue_2 = 10.2
        # time to buy pair 2
        self.buyTime_2 = '01:30'

        # pair to sell
        self.sellPair = 'ETHBUSD'
        # stable coin value to sell
        self.sellValueOrder = 10.1 # min 10.1
        # sell time
        self.sellTime = '01:00'

        # list of coins/token to be alerted
        self.pairList = ['BTCBUSD', 'ETHBUSD', 'SOLBUSD', 'LINKBUSD', 'DOTBUSD', 'BNBBUSD']
        # investment on dip
        self.dipInvestment = 1000
        # alert percentage
        self.alertPer = -10
        # sell limit percentage
        self.sellLimitPer = 0.03
        # buying history
        self.historyStamps = []

        # time for the wallet and the alert
        self.walletTime = '12:00'
        self.alertTime = 5 # in min


    # get response from API
    def apiCall(self, method):
        # connect on binance exchange
        self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY) #, testnet=True

        while True:
            try:
                response = method()
                break
            except BinanceAPIException as e:
                self.sendSheet(6, 2, e.status_code, e.message)
                self.sendTel(5, e.status_code, e.message)
                self.sendTerminal(5, e.status_code, e.message)

                # try every 5 min
                time.sleep(300)

        return response



    # connecting on google ss and sending sheet report
    def sendSheet(self, sheetNum, reportNum, p_1, p_2=None, p_3=None, p_4=None, p_5=None, p_6=None, p_7=None, p_8=None):
        #current date&time
        now = str(datetime.now())

        # google ss api
        spreadsheet_credentials = gspread.service_account(filename=self.ssCredFile)
        spreadsheet_id = spreadsheet_credentials.open_by_key(self.ssId)
        sheet = spreadsheet_id.get_worksheet(sheetNum)

        # sheet reports
        sheetReports =[
            [p_1, p_2, p_3, p_4, p_5, p_6, str(p_7)+"%", str(p_8)], # buying orders 1, 2, selling orders, dip buy market
            [str(p_1)+"\n"+now[:19]], # spot wallet report
            ["CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19]], # error loger
            [p_1, p_2, p_3, p_4, p_5] # limit sell order
        ]

        # append report to sheet
        sheet.append_row(sheetReports[reportNum])

    # telegram notifications
    def sendTel(self, reportNum, p_1, p_2=None, p_3=None, p_4=None, p_5=None, p_6=None):
        #current date&time
        now = str(datetime.now())
        # telegram notifications
        telegramReports = [
            ["***BUYING ORDER FULFILLED***\n\nBought at market price: "+str(p_1)+" $"+"\nCoin quantity: "+str(p_2)+" "+str(p_3)+"\nInvested: "+str(p_4)+ " $\nPercentage: "+str(p_5)+"%\n\n"+str(p_6)], # buying orders
            ["***SELLING ORDER FULFILLED***\n\nSold at market price: "+str(p_1)+" $"+"\nCoin quantity sold: "+str(p_2)+" "+str(p_3)+"\nValue sold: "+str(p_4)+ " $\nPercentage: "+str(p_5)+"%\n\n"+str(p_6)], # selling order
            ["***DIP MARKET BUY ORDER FULFILLED***\n\nBought at market price: "+str(p_1)+" $"+"\nCoin quantity: "+str(p_2)+" "+str(p_3)+"\nInvested: "+str(p_4)+ " $\nPercentage: "+str(p_5)+"%\n\n"+str(p_6)], # dip buy market order
            ["***DIP LIMIT SELL ORDER FULFILLED***\n\nCoin/Token: "+str(p_1)+"\nSell at: "+str(p_2)+"$\n"+"Selling value: "+str(p_3)+"\n\n"+str(p_4)], # dip limit sell order
            ["***SPOT WALLET BALANCE***\n\n"+str(p_1)+"\n"+now[:19]], # spot wallet report
            ["CODE: "+str(p_1)+"\n\nSERVER MESSAGE: "+str(p_2)+"\n\n"+now[:19]], # error loger
            ["***DIP ALERT TRIGGERED***\n\n"+str(p_1)+"\n"+"Price: "+str(p_2)+"$\n"+str(p_3)+"%\n\n"+now[:19]] # dip alert
        ]

        telegram_send.send(messages=telegramReports[reportNum])

    def sendTerminal(self, reportNum, p_1=None, p_2=None):
        #current date&time
        now = str(datetime.now())
        # terminal statuses
        terNot = [
            str(p_1)+" BUYING ORDER EXECUTED ... "+str(p_2), # buying pair 1 | pair 2
            str(p_1)+" SELLING ORDER EXECUTED ... "+str(p_2), # selling order
            str(p_1)+" DIP MARKET BUY ORDER EXECUTED ... "+str(p_2), # dip buy market order
            str(p_1)+" DIP LIMIT SELL ORDER EXECUTED ... "+str(p_2), # dip limit sell order
            "SPOT WALLET BALANCE HAS BEEN SENT ... "+now[:19], # spot wallet report
            "CODE: "+str(p_1)+"\nSERVER MESSAGE: "+str(p_2)+"\n"+now[:19] # error loger
        ]

        # program status
        print(terNot[reportNum])


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

    
    # buy market order
    def buyMarket(self, sheetNum, repNum, pair, investment, dipBuy=0):
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
        perInfoData = self.apiCall(lambda: self.client.get_ticker(symbol=pair))
        currentPer = round(float(perInfoData['priceChangePercent']), 2)
        buyOrSell = orderData['side']

        # send reports
        self.sendSheet(sheetNum, repNum-dipBuy, date, filledAt, invested, commission, assetQty, assetTicker, currentPer, buyOrSell)
        self.sendTel(repNum, filledAt, assetQty, assetTicker, invested, currentPer, date)
        self.sendTerminal(repNum, assetTicker, date)


    # sell market order
    def sellMarket(self, sheetNum, repNum, pair, sellingValue):
        # commission fee + spread fee
        sellingValue = sellingValue * (1 - 0.015)

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
        perInfoData = self.apiCall(lambda: self.client.get_ticker(symbol=pair))
        currentPer = round(float(perInfoData['priceChangePercent']), 2)
        buyOrSell = orderData['side']

        # send reports
        self.sendSheet(sheetNum, 0, date, soldAt, valueSold, commission, assetQtySold, assetTicker, currentPer, buyOrSell)
        self.sendTel(repNum, soldAt, assetQtySold, assetTicker, valueSold, currentPer, date)
        self.sendTerminal(repNum, assetTicker, date)

    
    # limit sell order
    def limitSell(self, sheetNum, repNum, pair, sellValue, lastPrice):
        # Buy coin/token on -% and sell higher
        sellAtPrice = round(lastPrice * (1 + self.sellLimitPer), 2)
        # commission fee + spread fee
        sellValue = sellValue * (1 - 0.015)
        limitSellData = self.apiCall(lambda: self.client.order_limit_sell(symbol=pair, quantity=self.getCeilingVal(pair, sellValue), price=sellAtPrice))

        # convert unix time
        unixTime = int(limitSellData['transactTime'] / 1000)
        norTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTime))

        # necessary info for the report
        date = norTime
        sellAt = round(float(limitSellData['price']), 2)
        sellValue = round(float(limitSellData['origQty']) * float(lastPrice), 2)
        assetTicker = pair[:-4]
        buyOrSellorder = "LIMIT "+limitSellData['side']

        # send reports
        self.sendSheet(sheetNum, repNum, date, sellAt, sellValue, assetTicker, buyOrSellorder)
        self.sendTel(repNum, assetTicker, sellAt, sellValue, date)
        self.sendTerminal(repNum, assetTicker, date)


    # get account balance
    def spotWalletBalance(self):
        spotWallet = self.apiCall(lambda: self.client.get_account())
        balance = spotWallet["balances"]
        # get only free spot wallet balance
        balanceReport = ''
        # custom format decimals for the report
        repFormat = '{0:.4f}'
        for x in balance:
            if float(x['free']) > 0:
                quantity = repFormat.format(float(x['free']))
                balanceReport += x['asset']+": "+str(quantity)+"\n"

        # send reports
        self.sendSheet(5, 1, balanceReport)
        self.sendTel(4, balanceReport)
        self.sendTerminal(4)


    # dip alert
    def dipAlert(self):
        # remove history stamps from previous month
        now = str(datetime.now())
        info = self.apiCall(lambda: self.client.get_ticker())

        # list assets below set minus precentage
        for pair in info:                    
            if pair['symbol'] in self.pairList and float(pair['priceChangePercent']) < self.alertPer:
                symbol, percentage, price = pair['symbol'], round(float(pair['priceChangePercent']), 2), round(float(pair['lastPrice']), 2)
                # create alert / buying / selling history
                stamp = pair['symbol'] + now[:10]
                if stamp not in self.historyStamps:
                    self.historyStamps.append(stamp)

                    # request orders
                    self.buyMarket(3, 2, symbol, self.dipInvestment, 2)
                    self.limitSell(4, 3, symbol, self.dipInvestment, price)

                    # # just notify on telegram about possible dip, DO NOT BUY
                    # self.sendTel(6, symbol[:-4], price, percentage)

        # remove history stamps from previous month
        if len(self.historyStamps) != 0:
            if now[5:7] != self.historyStamps[0][-5:-3]:
                self.historyStamps = []


if __name__ == "__main__":
    bot = Binance()
    # FOR TESTING ONLY

    # bot.getCeilingVal()
    # bot.getPercentage()
    # bot.getLotSize()
    # bot.spotWalletBalance()
    # bot.buyMarket(0, 0, bot.pair_1, bot.stableValue_1)
    # bot.buyMarket(1, 0, bot.pair_2, bot.stableValue_2)
    # bot.sellMarket(2, 1, bot.sellPair, bot.sellValueOrder)
    # bot.limitSell()
    # bot.dipAlert()


    # market buy order_1
    schedule.every().day.at(bot.buyTime_1).do(bot.buyMarket, 0, 0, bot.pair_1, bot.stableValue_1)

    # # market buy order_2
    # schedule.every().day.at(bot.buyTime_2).do(bot.buyMarket, 1, 0, bot.pair_2, bot.stableValue_2)

    # # market sell order
    # schedule.every().day.at(bot.sellTime).do(bot.sellMarket, 2, 1, bot.sellPair, bot.sellValueOrder)

    # dip alert
    schedule.every(bot.alertTime).minutes.do(bot.dipAlert)

    #spot wallet
    schedule.every().day.at(bot.walletTime).do(bot.spotWalletBalance)


    while True:
        schedule.run_pending()
        time.sleep(1)
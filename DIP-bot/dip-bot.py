"""
    antymijaljevic@gmail.com
    Binance DIP Bot
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import Timeout, ConnectionError
from binance.helpers import round_step_size
import config, telegram_send, schedule, gspread, json
from datetime import datetime
from time import sleep, strftime, localtime
from os import system, name


class Binance():
    def __init__(self):
        """ 
            DIP bot main setup
        """

        # clear screen and set starting time
        self.start_time = datetime.now()
        self.clear_screen(str(self.start_time))

        # spreadsheet credentials file & spreadsheet ID
        ss_cred_file = 'xxxxxxxxxxx.json'
        ss_unique_id = 'xxxxxxxxxxxxxxxxxx'

        spreadsheet_credentials = self.api_call(lambda: gspread.service_account(filename=ss_cred_file))
        self.spreadsheet_id = self.api_call(lambda:spreadsheet_credentials.open_by_key(ss_unique_id))

        # dip buying history database
        self.db_filename = 'orderDB.json'

        # script activity check
        self.check_active = 0.01

        # check for a dip, set selling percentage
        self.check_dip = 0.45 # approx every 30 sec
        self.sell_limit_percentage = 0.03 # 3 %

        # list of coins/tokens to be alerted, dip alert & dip investment, alert check counter
        self.token_list = ['BTCBUSD', 'ETHBUSD', 'SOLBUSD', 'LINKBUSD', 'DOTBUSD', 'BNBBUSD']
        self.dip_per_alert = -13
        self.dip_investment = 1000
        self.alert_counter = 0

    def clear_screen(self, start_time):
        """
            'cls' for windows and 'posix' for Linux and MacOS, 
            clears terminal depends on a OS
        """
        if name == 'nt':
            system('cls')
        else:
            system('clear')

        print("BINANCE DIP BOT: Activated ... "+start_time[:19])


    def bot_active(self, start_time):
        """
            Time elapsed since initial bot
        """
        new_time = datetime.now()
        time_elapsed = new_time - self.start_time
        seconds_passed = int(time_elapsed.seconds)

        day = seconds_passed // 86400
        seconds_passed %= 86400
        hour = seconds_passed // 3600
        seconds_passed %= 3600
        minutes = seconds_passed // 60
        # seconds_passed %= 60

        print("BINANCE DIP BOT: Time passed since activation > %s Days %s Hours %s Minutes | Dip alert counter > %s" % (day, hour, minutes, self.alert_counter))


    def api_call(self, method):
        """
            Call on Binance API and possible errors
        """
        while True:
            now = str(datetime.now())

            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, {"timeout": 5})
                response = method()
                break
            except (Timeout, BinanceAPIException) as e:
                # send to terminal, sheet and telegram
                print("Error: "+str(e.message)+" ... "+now[:19])

                self.sheet_number = self.spreadsheet_id.get_worksheet(2)
                self.sheet_number.append_row(["Error: "+str(e)+" ... "+now[:19]])

                telegram_send.send(messages=["***ERROR***\n\n"+str(e.message)+"\n\n"+now[:19]])

                sleep(20)
            except (ConnectionError, Exception) as e:
                print("Error: "+str(e)+" No internet connection ... "+now[:19])
                sleep(20)

        return response


    def get_ceiling_value(self, pair, investment):
        """
            get investment ceiling value based on a pair current price
        """
        binance = self.api_call(lambda: self.client.get_symbol_ticker(symbol=pair))
        pair_price = binance["price"]
        ceiling_val = float(investment) / float(pair_price)

        # round qty decimals to match a lot size
        a_lot_size = self.get_lot_size(pair)
        rounded_amount = round_step_size(ceiling_val, a_lot_size)

        return rounded_amount


    def get_lot_size(self, pair):
        """
            get a lot size decimal
        """
        binance = self.api_call(lambda: self.client.get_symbol_info(pair))
        a_lot_size = float(binance['filters'][2]['minQty'])

        return a_lot_size


    def request_buy_market(self, pair, investment, sheetNum):
        """
            request a buy market order
        """
        binance = self.api_call(lambda: self.client.order_market_buy(symbol=pair, quantity=self.get_ceiling_value(pair, investment)))

        # necessary info for the report
        # convert unix to normal time
        unix_time = int(binance['transactTime'] / 1000)
        date = strftime("%Y-%m-%d %H:%M:%S", localtime(unix_time))
        filled_at = round(float(binance['fills'][0]['price']), 2)
        invested = round(float(binance['cummulativeQuoteQty']), 2)
        commission = float(binance['fills'][0]['commission'])
        asset_qty = float(binance['fills'][0]['qty'])
        asset_ticker = binance['symbol'][:-4]
        binance_ticker_info = self.api_call(lambda: self.client.get_ticker(symbol=pair))
        asset_24_perc = round(float(binance_ticker_info['priceChangePercent']), 2)
        buy_or_sell = binance['side']

        # send to terminal, sheet and telegram
        print(str(asset_ticker)+" DIP BUYING ORDER EXECUTED ... "+str(date))

        self.sheet_number = self.spreadsheet_id.get_worksheet(sheetNum) 
        self.sheet_number.append_row([date, filled_at, invested, commission, asset_qty, asset_ticker, str(asset_24_perc)+"%", buy_or_sell])

        telegram_send.send(messages=["***DIP BUYING ORDER FULFILLED***\n\nFilled at market price: "+str(filled_at)+" $"+"\nCoin quantity: "+str(asset_qty)+" "+str(asset_ticker)+"\nInvested: "+str(invested)+ " $\nPercentage: "+str(asset_24_perc)+"%\n\n"+str(date)])


    def request_limit_sell(self, pair, value_to_sell, last_price, sheetNum):
        """
            request a limit sell order
        """
        # buy coin/token on set set dip percentage and sell higher, commission fee + spread fee
        sell_at_price = round(last_price * (1 + self.sell_limit_percentage), 2)
        value_to_sell = value_to_sell * (1 - 0.015)

        binance = self.api_call(lambda: self.client.order_limit_sell(symbol=pair, quantity=self.get_ceiling_value(pair, value_to_sell), price=sell_at_price))

        # necessary info for the report
        # convert unix to normal time
        unix_time = int(binance['transactTime'] / 1000)
        date = strftime("%Y-%m-%d %H:%M:%S", localtime(unix_time))
        sell_at = round(float(binance['price']), 2)
        selling_value = round(float(binance['origQty']) * float(last_price), 2)
        asset_ticker = pair[:-4]
        buy_or_sell = "LIMIT "+binance['side']

        # send to terminal, sheet and telegram
        print(str(asset_ticker)+" DIP LIMIT SELL ORDER EXECUTED ... "+str(date))

        self.sheet_number = self.spreadsheet_id.get_worksheet(sheetNum) 
        self.sheet_number.append_row([date, sell_at, selling_value, asset_ticker, buy_or_sell])

        telegram_send.send(messages=["***DIP LIMIT SELL ORDER FULFILLED***\n\nAsset: "+str(asset_ticker)+"\nSell at: "+str(sell_at)+"$\n"+"Selling value: "+str(selling_value)+"$\n\n"+str(date)])


    def dip_alert(self):
        """
            detecting possible dips below set minus percentage
            requesting buy market order and then limit sell instantly

        """
        now = str(datetime.now())
        date = now[:10]
        tel_reports = ''

        binance = self.api_call(lambda: self.client.get_ticker())

        # iterate through manually set pairs list
        for pair in binance: 
            symbol, percentage, price = pair['symbol'], round(float(pair['priceChangePercent']), 2), round(float(pair['lastPrice']), 2)                   
            if symbol in self.token_list and percentage < self.dip_per_alert:

                # open json db and add date and pairs (buy set pairs only once per day)
                with open(self.db_filename, "r+") as file:
                    db_data = json.load(file)
                    if date not in db_data:
                        db_data[date] = []
                    if symbol not in db_data[date]:
                        db_data[date].append(symbol)
                        db_data.update(db_data)
                        file.seek(0)
                        json.dump(db_data, file, indent=4, separators=(',',': '))
                        
                        tel_reports += "Pair: "+str(symbol[:-4])+"\nCurrent price: "+str(price)+"$\nPercentage: "+str(percentage)+"%\n\n"

                        # request buy market and limit sell orders
                        self.request_buy_market(symbol, self.dip_investment, 0)
                        self.request_limit_sell(symbol, self.dip_investment, price, 1)

        
        # notify on telegram about detected dip (notify only once per day), count alert checks
        self.alert_counter +=1
        if len(tel_reports) > 0:
            telegram_send.send(messages=["***DIP ALERT TRIGGERED***\n\n"+str(tel_reports)+"\n"+now[:19]])



if __name__ == "__main__":
    """
        This part is for testing purposes only
    """
    bot = Binance()

    # bot.clear_screen()
    # bot.bot_active(bot.start_time)
    # bot.api_call()
    # bot.get_ceiling_value("ETHBUSD", 10.5)
    # bot.get_lot_size("ETHBUSD")
    # bot.request_buy_market("BNBUSDT", 10.5, 0)
    # bot.request_limit_sell("ADABUSD", 10.5, 2.03, 1)
    # bot.dip_alert()


    """
        Scheduler
    """

    # script status
    schedule.every(bot.check_active).minutes.do(bot.bot_active, bot.start_time)

    # check for a dip
    schedule.every(bot.check_dip).minutes.do(bot.dip_alert)

    while True:
        schedule.run_pending()
        sleep(1)

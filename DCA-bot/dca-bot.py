# antymijaljevic@gmail.com

from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import Timeout, ConnectionError
from binance.helpers import round_step_size
import config, telegram_send, schedule, gspread
from datetime import datetime
from time import sleep, strftime, localtime
from os import system, name


class Binance():
    def __init__(self):
        """ 
            DCA bot main setup
        """

        # clear screen and set starting time
        self.start_time = datetime.now()
        self.clear_screen(str(self.start_time))

        # spreadsheet credentials file & spreadsheet ID
        ss_cred_file = 'xxx.json' # share spreadsheet with 'client_email' 
        ss_unique_id = 'xxxxxxxxxxxxxxxxxx'

        spreadsheet_credentials = self.api_call(lambda: gspread.service_account(filename=ss_cred_file))
        self.spreadsheet_id = self.api_call(lambda:spreadsheet_credentials.open_by_key(ss_unique_id))

        # DCA pair 1 setup. Pair, value to invest & when to buy
        self.pair_1 = 'ADABUSD'
        self.stable_coin_value_1 = 10.2
        self.buying_time_1 = '00:00'

        # DCA pair 2 setup. Pair, value to invest & when to buy
        self.pair_2 = 'BTCBUSD'
        self.stable_coin_value_2 = 10.5
        self.buying_time_2 = '00:00'

        # Script activity check
        self.check_active = 30 # in minutes


    def clear_screen(self, start_time):
        """
            'cls' for windows and 'posix' for Linux and MacOS, 
            clears terminal depends on a OS
        """
        if name == 'nt':
            system('cls')
        else:
            system('clear')

        print("BINANCE BOT: Activated ... "+start_time[:19])


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

        print("BINANCE BOT: Time passed since activation > %s Days %s Hours %s Minutes" % (day, hour, minutes))


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
            Get a lot size decimal
        """
        binance = self.api_call(lambda: self.client.get_symbol_info(pair))
        a_lot_size = float(binance['filters'][2]['minQty'])

        return a_lot_size


    def request_buy_market(self, pair, investment, sheetNum):
        """
            Request a buy market order
        """
        binance = self.api_call(lambda: self.client.order_market_buy(symbol=pair, quantity=self.get_ceiling_value(pair, investment)))

        # necessary info for the report
        unix_time = int(binance['transactTime'] / 1000) # unix to normal
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
        print(str(asset_ticker)+" DCA BUYING ORDER EXECUTED ... "+str(date))

        self.sheet_number = self.spreadsheet_id.get_worksheet(sheetNum) 
        self.sheet_number.append_row([date, filled_at, invested, commission, asset_qty, asset_ticker, str(asset_24_perc)+"%", buy_or_sell])

        telegram_send.send(messages=["***DCA BUYING ORDER FULFILLED***\n\nBought at market price: "+str(filled_at)+" $"+"\nCoin quantity: "+str(asset_qty)+" "+str(asset_ticker)+"\nInvested: "+str(invested)+ " $\nPercentage: "+str(asset_24_perc)+"%\n\n"+str(date)])


if __name__ == "__main__":
    """
        This part is for testing purposes only
    """
    bot = Binance()

    # bot.clear_screen()
    # bot.bot_active(bot.start_time)
    # bot.api_call()
    # bot.google_sheet()
    # bot.telegram()
    # bot.get_ceiling_value(bot.pair_1, bot.stable_coin_value_1)
    # bot.get_lot_size(bot.pair_1)
    # bot.request_buy_market(bot.pair_1, bot.stable_coin_value_1, 0)
    # bot.request_buy_market(bot.pair_2, bot.stable_coin_value_2, 1)

    """
        Scheduler
    """

    # Script status
    schedule.every(bot.check_active).minutes.do(bot.bot_active, bot.start_time)

    # DCA pair 1 
    schedule.every().day.at(bot.buying_time_1).do(bot.request_buy_market, bot.pair_1, bot.stable_coin_value_1, 0)

    # DCA pair 2
    schedule.every().day.at(bot.buying_time_2).do(bot.request_buy_market, bot.pair_2, bot.stable_coin_value_2, 1)

    while True:
        schedule.run_pending()
        sleep(1)

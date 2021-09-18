import ccxt 
# import telebot
import telegram_send

#Connecting on binance using ccxt library
exchange = ccxt.binance({
    'apiKey': 'zzz',
    'secret': 'zzz',
    'enableRateLimit': True,
})

BOT_API = '2042270458:AAEuKw14AyWgqXFZU7k54AOt2jI-QvzTLRk'

#spot wallet balance
balance = exchange.fetch_total_balance()
balancePrint = "BUSD = " + str(int(balance['BUSD'])) + "$" + "\n" + "ADA = " + str(int(balance['ADA'])) + " ADA" + "\n" "SOL = " + str(int(balance['SOL'])) + " S"

#ada last price
# currentAdaPrice = exchange.fetch_ticker('ADA/BUSD')
# print("ADA last price >>>", currentAdaPrice['last'], "$")

#telegram
#bot = telebot.TeleBot(BOT_API)

# @bot.message_handler(commands=['Greet'])
# def greet(message):
# 	bot.reply_to(message, "Hey, how's going?")

# @bot.message_handler(commands=['hi'])
# def wallet_status(message):
# 	bot.send_message(message.chat.id, "Hi! Hannah!")

# bot.polling()

telegram_send.send(messages=[balancePrint])

#making buy or sell order
def makeOrder():
    symbol = 'ADA/BUSD'  
    type = 'market'  # or 'market'
    side = 'buy'  # or 'sell'
    amount = 1 # ignore
    price = 5  # invest
    data = exchange.create_order(symbol, type, side, amount, price)
    print("Date: " + data.get('datetime')[0:10])
    print("Time: " + data.get('datetime')[11:19])
    print("Amount: " + str(data.get('amount')) + " ADA")
    print("Cost: " + str(data.get('cost')) + " $")
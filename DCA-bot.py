from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import Timeout
from requests.exceptions import ConnectionError
from binance.helpers import round_step_size
import config, telegram_send, schedule, gspread, time, json
from datetime import datetime
from os import system

system('cls')
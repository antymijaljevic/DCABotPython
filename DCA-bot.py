from binance.client import Client
from binance.exceptions import BinanceAPIException
from requests.exceptions import Timeout, ConnectionError
from binance.helpers import round_step_size
import config, telegram_send, schedule, gspread, json
from datetime import datetime
from time import time, sleep
from os import system

system('cls')
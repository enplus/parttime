import time
import sys

# exchanges
from Broker import Broker
import api_config as config

# 각 거래소별 객체
from xchg_kr.CoinONE import CoinONE
from xchg_kr.Korbit import KORBIT
from xchg_kr.Bithumb import BITHUMB

class Logger:
    if str.lower(sys.platform) != "win32":
        PURPLE = '\033[95m' # PURPLE
        BLUE = '\033[94m'   # BLUE
        GREEN = '\033[92m'  # GREEN
        YELLOW = '\033[93m' # YELLOW
        RED = '\033[91m'    # RED
        ENDC = '\033[0m'    # ??

    def warning(self, msg):
        self._write(self.YELLOW, msg)

    def error(self, msg):
        self._write(self.RED, msg)

    def ok(self, msg):
        self._write(self.GREEN, msg)

    def info(self, msg):
        self._write(self.BLUE, msg)

    def _write(self, ANSI, msg):
        t = time.strftime('%b %d, %Y %X %Z')
        print("%s%s : %s%s" % (ANSI,t,msg,self.ENDC))

def create_brokers(mode, currencies, exchangeNames):
    # returns an array of Broker objects
    brokers = []
    for name in exchangeNames:
        if (str.upper(name) == 'COINONE'):
            xchg = CoinONE(config.COINONE_API, config.COINONE_KEY)
        elif (str.upper(name) == 'KORBIT'):
            xchg = KORBIT(config.KORBIT_API, config.KORBIT_KEY)
        # elif (str.upper(name) == 'BITHUMB'):
        #     xchg = BITHUMB(config.BITHUMB_API, config.BITHUMB_KEY)
        else:
            print('Exchange ' + name + ' not supported!')
            broker = None
            continue
        print('%s initialized' % (xchg.name))

        broker = Broker(mode, xchg)

        if mode == 'BACKTEST':
#            broker.balances = config.PAPER_BALANCE
            broker.balances = broker.xchg.get_all_balances() # use real starting balances.
        brokers.append(broker)
    return brokers

def get_assets(brokers):
    # prints out total assets held across all brokers
    assets = {}
    for broker in brokers:
        for currency, balance in broker.balances.items():
            if currency in assets:
                assets[currency] += balance
            elif balance > 0.0:
                assets[currency] = balance
    return assets

def print_assets(brokers):
    print(get_assets(brokers))


highest_price = lambda arr : max([o.v for o in arr])
lowest_price = lambda arr : min([o.v for o in arr])
total_base_volume = lambda arr : sum([o.v for o in arr])
total_alt_volume = lambda arr : sum([o.p * o.v for o in arr])


import time
import sys

# exchanges
from Broker import Broker
import api_config as config

# 각 거래소별 객체
from xchg_kr.CoinONE import CoinONE
from xchg_kr.Korbit import KORBIT
from xchg_kr.Bithumb import BITHUMB

# 말이 Logger이지 걍 프린트할때 양식 지정하는 용도 \033어쩌고 이건 다
# 리눅스 상에서 색상을 표현하는 용도
class Logger:
    if str.lower(sys.platform) != "win32":
        PURPLE = '\033[95m' # PURPLE
        BLUE = '\033[94m'   # BLUE
        GREEN = '\033[92m'  # GREEN
        YELLOW = '\033[93m' # YELLOW
        RED = '\033[91m'    # RED
        ENDC = '\033[0m'    # NORMAL

    def warning(self, msg):
        self._write(self.YELLOW, msg)

    def error(self, msg):
        self._write(self.RED, msg)

    def ok(self, msg, msg_type):
        if msg_type == 'trade':
            print("%s%s)%s" % (self.GREEN, msg, self.ENDC))
        else:
            self._write(self.GREEN, msg)

    def info(self, msg):
        self._write(self.BLUE, msg)

    def tickinfo(self, msg, bot_info=None):
        t = time.strftime('%y/%m/%d %X %Z')
        print("%s%s)%s %s%s : %s :%s %s" % (self.PURPLE, config.MODE, self.ENDC, self.BLUE, t, msg, self.ENDC, bot_info))

    # def mode(self, msg):
    #     print("%s%s%s" % (self.RED, config.MODE, self.ENDC))

    def _write(self, ANSI, msg):
        # t = time.strftime('%b %d, %Y %X %Z')
        t = time.strftime('%Y/%m/%d %X %Z')
        print("%s%s)%s %s%s : %s%s" % (self.RED, config.MODE, self.ENDC, ANSI, t, msg, self.ENDC))

# create_broker(broker(거래소 객체) 생성용)
# brokers라는 List형태에 최종적으로 생성됨.
# 각 거래소객체는 싱글턴으로 구현되어서 하나뿐인 객체로 존재함
def create_brokers(mode, currencies, exchangeNames):
    # returns an array of Broker objects
    brokers = []
    for name in exchangeNames:
        if (str.upper(name) == 'COINONE'):
            xchg = CoinONE(config.COINONE_API, config.COINONE_KEY)
        elif (str.upper(name) == 'KORBIT'):
            xchg = KORBIT(config.KORBIT_API, config.KORBIT_KEY)
        elif (str.upper(name) == 'BITHUMB'):
            xchg = BITHUMB(config.BITHUMB_API, config.BITHUMB_KEY)
        else:
            print('Exchange ' + name + ' not supported!')
            broker = None
            continue
        print('%s initialized' % (xchg.name))

        broker = Broker(mode, xchg)

        if mode == 'BACKTEST':
            # 임의로 잔고를 지정해서 처리하도록 수정?
            # broker.balances = config.PAPER_BALANCE
            pass
        elif mode == 'PAPER':
            # 임의로 잔고를 지정해서 처리하도록 수정?
            pass
        elif mode == 'TRADE':
            # use real starting balances.
            broker.balances = broker.xchg.get_all_balances()
            pass

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


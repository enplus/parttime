# generic class for trading/market-watching bots

# here is where the crypto_currency arbitrage strategy is implemented
# along with the application loop for watching exchanges

import threading
import time
from common.utils import Logger
from common.ProfitCalculator import ProfitCalculator

try:
    import cPickle as pickle
except ImportError:
    import _pickle as pickle  # for 3.5
from os.path import abspath
from common.order import Order  # Order class needs to be present for de-serialization of orders
from common.utils import get_assets, print_assets

from pprint import pprint

import os

# 스레드 처리하는 클래스
# Bot클래스의 tick() 함수 내에서 UpdateDepthThread를 수행함. request 하는
# 주기를 정할수 있음
# 스레드로 Broker클래스의 Update_orderbook를 실행하는데
# 이하의 실제 처리는 각 Broker(거래소) 객체들의 get_orderbook를 수행
class UpdateDepthThread(threading.Thread):
    """
    simple class for updating the highest bid and lowest offer rates of each broker
    """
    def __init__(self, broker, currency, backtest_data=None, tick_i=0):
        self.broker = broker
        self.currency = currency
        self.backtest_data = backtest_data
        self.tick_i = tick_i
        threading.Thread.__init__(self)

    def run(self):
        if self.broker.xchg.get_validated_currency(self.currency):
            # print('%s:%s [UpdateDepthThread]' % (self.currency, self.broker))
            if self.backtest_data is not None:
                self.broker.update_orderBook(self.currency, self.backtest_data, self.tick_i)
            else:
                self.broker.update_orderBook(self.currency)
        else:
            print('validated_currency not found')


class UpdateBalanceThread(threading.Thread):
    """
    simple thread class for updating balances across
    all accounts. Originally this was a part of UpdateDepthThread
    but some exchanges serve up entire wallet and this may result in
    HTTP 429 error if too many requests are made!
    """
    def __init__(self, broker):
        self.broker = broker
        threading.Thread.__init__(self)

    def run(self):
        self.broker.update_all_balances()


# class Bot: 과 동일 (object)는 python 2.x와의 호환성을 위해 사용됨
class Bot(object):
    def __init__(self, config, brokers):
        """
        config = configuration file
        brokers = array of broker objects
        """
        super(Bot, self).__init__()
        self.config = config
        self.brokers = brokers
        self.error = False
        self.log = Logger()
        self.backtest_data = None
        self.max_ticks = 0
        self.data_path = abspath(config.TICK_DIR)
        self.trading_enabled = True
        self.tick_i = 0
        self.debug = config.DEBUG
        self.debug_cls = config.DEBUG_CLEARSCREEN
        self.debug_mktdata = config.DEBUG_MARKETDATA
        self.debug_spread = config.DEBUG_SPREAD

    def start(self, sleep=0):  # for live/paper trading
        start = time.time()
        last_tick = start - sleep
        while not self.error:
            delta = time.time() - last_tick
            if (delta < sleep):
                # sleep for the remaining seconds
                time.sleep(sleep - delta)
            self.tick()
            last_tick = time.time()

    def backtest(self, backtest_file):  # for backtesting
        print('Initial Position:')
        initial_position = get_assets(self.brokers)
        print(initial_position)
        self.backtest_data = pickle.load(open(backtest_file, "rb"))
        self.max_ticks = len(self.backtest_data['ticks'])
        self.tick_i = 0
        while self.tick_i < self.max_ticks:
            self.tick()
            self.tick_i += 1
        # print final assets
        print('Final Position:')
        final_position = get_assets(self.brokers)
        # compute total profits
        print('Total Profits:')
        for k, v in final_position.items():
            if k in initial_position:
                print('%s : %f' % (k, v - initial_position[k]))
            else:
                print('%s : %f' % (k, v))

    def gather_data(self, filepath=None, sleep=1, duration=60, maxdepth=6):  # for saving market data
        '''
        runs the bot in realtime for 60 seconds, waits 1 second between each execution, and
        write the tick data for playback in realtime. Increase the frequency if you
        are interested in larger-scale price movements rather than high-frequency trading.

        maxdepth is number of orders saved in each market. Idea being that we are unlikely
        to be interested in the order prices of anything beyond the 6th best

        what is the best way to stucture the data?
        ideally we would separate by market, then by bids/offers, then by each broker so it would be easy
        to find prices.
        but actually this would make the broker update mechanism kind of tough from the perspective of the
        actual trading bot. So we will implement it so that the exchange update tick goes as simply as possible
        namely we'll first separate by broker, then by market, then by bids/offers

        this can be quite a lot of data!
        '''
        self.trading_enabled = False
        # generate a filename if one is not provided
        if filepath is None:
            t = "%s__%s_%s.p" % (time.strftime('%b-%d-%Y_%H-%M-%S'), sleep, duration)
            filepath = self.data_path + '/' + t

        start = time.time()
        data = {'start': start, 'ticks': [], 'duration': duration, 'sleep': sleep, 'maxdepth': maxdepth}
        data['tradeable_pairs'] = {broker.xchg.name: broker.xchg.tradeable_crypt_crncy for broker in self.brokers}
        last_tick = start - sleep
        while (time.time() - start < duration and not self.error):
            delta = time.time() - last_tick
            if (delta < sleep):
                # sleep for the remaining seconds
                time.sleep(sleep - delta)

            self.tick()  # calls Bot's update functions
            marketdata = {}
            for broker in self.brokers:
                name = broker.xchg.name
                brokerdata = {}
                for market, d in broker.depth.items():
                    brokerdata[market] = {'bids'  : d['bids'][:maxdepth - 1],
                                          'offers': d['offers'][:maxdepth - 1]}
                marketdata[name] = brokerdata
            data['ticks'].append(marketdata)
            last_tick = time.time()
            pickle.dump(data, open(filepath, 'wb'))  # write to file
        self.trading_enabled = False

    def trade (self, currency):
        pass

    def tick(self):
        start = time.time()
        for broker in self.brokers:
            # clear data so that if API call fails, we don't mistakenly
            # report last tick's data
            broker.clear()
        for currency in self.config.CURRENCIES:
            # multithreaded update of the currency on each exchange

            if self.config.USE_MULTITHREADED:
                threads = []
                threadLock = threading.Lock()
                for broker in self.brokers:
                    # print('MultiThreaded self.brokers = %s' % broker.xchg.name)

                    # multithreaded update balance
                    # balance_thread = UpdateBalanceThread(broker)
                    # balance_thread.start()
                    # threads.append(balance_thread)

                    # multithreaded update depth
                    depth_thread = UpdateDepthThread(broker, currency, self.backtest_data, self.tick_i)
                    depth_thread.start()
                    threads.append(depth_thread)
                for t in threads:
                    t.join()  # wait for all update threads to complete
                    elapsed = time.time() - start
                    print('Broker update finished in %d ms' % (elapsed * 1000))

            else:
                # single threaded update
                for broker in self.brokers:
                    # print('%s:%s' % (broker.xchg.name, broker.xchg.get_currencies))
                    # broker.balances = broker.xchg.get_all_balances()
                    # print(broker.xchg.name)
                    # broker.update_all_balances()
                    if broker.xchg.get_validated_currency(currency):
                        if self.backtest_data is not None:
                            broker.update_orderBook(currency, self.backtest_data, self.tick_i)
                        else:
                            broker.update_orderBook(currency)

            if self.trading_enabled:
                self.trade(currency)

        if self.debug_mktdata and self.debug_cls:
            os.system('clear')

        # self.log.tickinfo('tick', bot_info=('[%s]' % '/'.join(self.config.CURRENCIES)))
        self.log.tickinfo('/'.join(self.config.CURRENCIES), bot_info='')

            # custom function for each trading bot to implement
            # the default implementation is to do nothing - useful in situations like
            # data gathering

# here is where the pair arbitrage strategy is implemented
# along with the application loop for watching exchanges
# For compactness, only the top 10
# DataGatherBot은 logging만 하는 용도? 인듯. Backtest를 위해 파일로 기록후
# 나중에 처리됨
# 아직 구현안됨 프린트로 처리
# Bot에서 상속되는형태 ArbitrageBot/DataGatherBot 동일
# 차이점은 실 거래되는용도와 로깅
class DataGatherBot(Bot):
    def __init__(self, config, brokers):
        super(DataGatherBot, self).__init__(config, brokers)
        self.data_path = abspath(config.TICK_DIR)

    def tick(self):
        #self.log.info('tick')
        super(DataGatherBot, self).tick()

    def start(self, filepath=None, sleep=1, duration=60, maxdepth=6):
        '''
        runs the bot in realtime for 60 seconds, waits 1 second between each execution, and
        write the tick data for playback in realtime. Increase the frequency if you
        are interested in larger-scale price movements rather than high-frequency trading.

        maxdepth is number of orders saved in each market. Idea being that we are unlikely
        to be interested in the order prices of anything beyond the 6th best

        what is the best way to stucture the data?
        ideally we would separate by market, then by bids/offers, then by each broker so it would be easy
        to find prices.
        but actually this would make the broker update mechanism kind of tough from the perspective of the
        actual trading bot. So we will implement it so that the exchange update tick goes as simply as possible
        namely we'll first separate by broker, then by market, then by bids/offers

        this can be quite a lot of data!
        '''
        # generate a filename if one is not provided
        if filepath is None:
            t =  "%s__%s_%s.p" % (time.strftime('%b-%d-%Y_%H-%M-%S'), sleep, duration)
            filepath = self.data_path + '/' + t

        start = time.time()
        data = {'start' : start, 'ticks' : [], 'duration' : duration, 'sleep' : sleep, 'maxdepth' : maxdepth}
        last_tick = start - sleep
        while (time.time() - start < duration and not self.error):
            delta = time.time() - last_tick
            if (delta < sleep):
                # sleep for the remaining seconds
                time.sleep(sleep-delta)

            self.tick() # calls Bot's update functions
            marketdata = {}

            for broker in self.brokers:
                name = broker.xchg.name
                brokerdata = {}
                for currency, d in broker.orderBook.items():
                    # quote slicing
                    brokerdata[currency] = {'bids' : d['bids'][:maxdepth-1], 'offers': d['offers'][:maxdepth-1]}
                marketdata[name] = brokerdata

                if self.debug_mktdata:
                    print('### %s ##########' % broker)
                    pprint(brokerdata)

            data['ticks'].append(marketdata)

            last_tick = time.time()
            pickle.dump(data, open(filepath, 'wb')) # write to file

    def trade(self, currency):
        # - initial test - compare high_bid and low_ask prices
        # - if spread is positive, fetch market depth and re-assess arb opportunity

        pc = ProfitCalculator(self.brokers, currency)
        if self.debug_spread:
            print('%s) %s' % (currency, self.brokers))
        if pc.check_profits():
            # self.log.ok(("%s) Found!!" % currency), msg_type='trade')
            pass
        pass


# ArbitrageBot은 실제 트레이딩을 위한 용도
# 아직 구현안됨 프린트로 처리
class ArbitrageBot(Bot):
    def __init__(self, config, brokers):
        super(ArbitrageBot, self).__init__(config, brokers)

    def trade(self, currency):
        # - initial test - compare high_bid and low_ask prices
        # - if spread is positive, fetch market depth and re-assess arb opportunity

        pc = ProfitCalculator(self.brokers, currency)
        if self.debug_spread:
            print('%s) %s' % (currency, self.brokers))
        if pc.check_profits():
            # self.log.ok(("%s) Found!!" % currency), msg_type='trade')
            pass
        pass
        #     (bidder, asker, profit_obj) = pc.get_best_trade()
        #     bidder_order = profit_obj["bidder_order"]
        #     asker_order = profit_obj["asker_order"]
        #     if self.config.MODE == 'PAPER' or self.config.MODE == 'BACKTEST':

        #         bidder_tx = 1.0 - bidder.xchg.trading_fee
        #         asker_tx = 1.0 - asker.xchg.trading_fee
        #         bidder.balances[base] -= bidder_order.v
        #         bidder.balances[alt] += bidder_order.p * bidder_order.v * bidder_tx
        #         asker.balances[base] += asker_order.v * asker_tx
        #         asker.balances[alt] -= asker_order.p * asker_order.v
        #         print('Success! Bought %f %s for %f %s from %s and sold %f %s for %f %s at %s' %
        #               (asker_order.v*asker_tx,base,asker_order.p* asker_order.v,alt,asker.xchg.name,
        #                bidder_order.v,base,bidder_order.p * bidder_order.v * bidder_tx,alt,bidder.xchg.name))
        #         print('Profit : %f %s' % (bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))
        #     else:
        #         # live trade - do this manually for now!
        #         print('Profitable Arbitrage Opportunity Detected!! Buy %f %s for %f %s from %s and sell %f %s for %f %s at %s' %
        #               (asker_order.v*asker_tx,base,asker_order.p* asker_order.v,alt,asker.xchg.name,
        #                bidder_order.v,base,bidder_order.p * bidder_order.v * bidder_tx,alt,bidder.xchg.name))
        #         print('Profit : %f %s' % (bidder_order.p * bidder_order.v * bidder_tx - asker_order.p * asker_order.v, alt))
# #                 asker.buy(pair, asker_order.p, asker_order.v)
# #                 bidder.sell(pair, bidder_order.p, bidder_order.v)


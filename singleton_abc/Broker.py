# class for Broker
# Broker(거래소 객체)
import sys

class Broker(object):
    def __init__(self, mode, xchg):
        super(Broker, self).__init__()
        self.mode = mode # TRADING mode (PAPER or LIVE)
        self.xchg = xchg
        self.__currencies = None

        # stores live balances
        self.balances = {}

        #  self. depth consists of keys = the bases that I define in config, and each lists buy/sell orders
        #  for that market. However, the exchange subclass implementation should take care of whether I
        #  flip my market slugs or not.
        self.orderBook = {}
        self.orders = [] # list of outstanding orders

    def __repr__(self):
        return "%s from Brokers.py" % (self.xchg)

    # 최우선 매수호가
    def get_highest_bid(self, currency):
        if currency in self.orderBook and len(self.orderBook[currency]['bids']) > 0:
            return self.orderBook[currency]['bids'][0].p # p=price & q=qty
        return None

    # 최우선 매도호가
    def get_lowest_ask(self, currency):
        if currency in self.orderBook and len(self.orderBook[currency]['offers']) > 0:
            return self.orderBook[currency]['offers'][0].p # p=price & q=qty
        else:
            return None

    def get_orders(self, currency, order_type):
        """
        use this function for accessing the depth info

        Note that the depth retrieval already flips the order for us based on the ordering
        that we specified during pair updates. However those pair update orders are arbitrary
        and we may end up needing both buy(A_B) and sell(B_A) orders with the samedepth info.
        (TODO - confirm whether the swapped retrieval ever gets called!)
        we could pre-compute the depth information but it would double the
        serialized data size. so it's probably easier for now just to re-compute on the
        fly when we need it again.

        order_type = 'bids' or 'offers'
        """
        if currency in self.orderBook:
            return self.orderBook[currency][order_type]
        else:
            # damn, it's flipped. do we ever actually cross this point?
            return -1

    def update_orderBook(self, currency, backtest_data=None, tick_i=0):
        # updates the highest_bid and lowest_ask for given pair
        # depths are sorted by best first
        if backtest_data is not None:
            # load in backtest data provided by the bot
            try:
                self.orderBook[currency] = backtest_data['ticks'][tick_i][self.xchg.name][currency]
            except:
                print('uh oh, missing depth data from this exchange')
                self.orderBook[currency] = {"bids":[],"offers":[]}
            """
            TODO - if backtesting, need to modify depth so that it appears as if we had
            actually moved the market with our previous orders.

            i.e. if an orderID we have acted on shows up in the depth list, modify it.
            """
        else:
            try:
                self.orderBook[currency] = self.xchg.get_orderbook(currency)
                # sort the depth by descending bid price and ascending ask price
                self.orderBook[currency]['bids'].sort(key=lambda x: x.p, reverse=True)
                self.orderBook[currency]['offers'].sort(key=lambda x: x.p, reverse=False)
            except:
                self.orderBook[currency] = {'bids':[],'offers':[]} # keep going
                e = sys.exc_info()[0]
                print('%s error: %s' % (self.xchg.name, e))


    def update_all_balances(self):
        # key method!! when running in paper/live mode, fetch data from xchg
        # when running in backtest mode, this is a SIMULATED quantity!
        if (self.mode == 'LIVE'):
            self.balances = self.xchg.get_all_balances()
        elif (self.mode == 'PAPER' or self.mode == 'BACKTEST'):
            print('%s mode - passed' % self.mode)
            pass

    def clear(self):
        # only clear balance if we are not backtesting.
        if self.mode == 'PAPER' or self.mode == 'LIVE':
            self.balances = {}
        self.orderBook = {}

    def buy(self, currency, price, volume):
        pass

    def sell(self, currency, price, volume):
        pass

    def submit_order(self, currency, ordertype, price, volume):
        # submit order via API
        pass

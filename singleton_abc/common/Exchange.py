'''
abstract exchange class
'''

from common.order import Order
import common.utils

import abc

class Exchange(abc.ABC):
    """docstring for Exchange"""
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        super(Exchange, self).__init__()
        self.name = None
        self.trading_fee = None
        self.ok = True

        # self.set_tradeable_currencies()
        # dictionary of outstanding orders.
        self.outstanding_orders = {}
        self.__currencies = self.get_currencies

    def __repr__(self):
        return "%s" % (self.name)

    @abc.abstractmethod
    def get_currencies(self):
        '''
        returns all crypto_currency list [ "etc","btc","eth", ...blah ]
        '''
        return NotImplemented

    @abc.abstractmethod
    def get_orderbook(self, currency):
        # 특정 CryptoCurrency북 요청. overloading
        '''
        returns all bids and offers (crypto_currency)
        default - all books
        '''
        return NotImplemented

    # implemented from Broker
    # @abc.abstractmethod
    # def get_highest_bid(self, currency='all'):
    #     '''
    #     return top priority bid
    #     default - all bids
    #     '''
    #     return NotImplemented

    # @abc.abstractmethod
    # def get_lowest_offer(self, currency='all'):
    #     '''
    #     return top priority offer
    #     '''
    #     return NotImplemented


    @abc.abstractmethod
    def get_balance(self, currency):
        '''
        return balance of particular currency
        NOTE: returns only AVAILABLE balance.
        there may be onhold or unconfirmed money that we get
        from deposits/trades but we can only use the available balance for
        trading anyway
        '''
        return NotImplemented

    @abc.abstractmethod
    def get_all_balances(self):
        '''
        returns dictionary of all balances
        '''
        return NotImplemented


    @abc.abstractmethod
    def submit_order(self, gc, gv, rc, rv):
        # TODO - fix this!
        '''
        at this point, not sure how to structure the api call to sell orders.
        perhaps should switch to Buy/Sell style for single markets?
        - returns some kind of standard Order data structure
        '''
        return NotImplemented

    @abc.abstractmethod
    def confirm_order(self, orderID):
        '''
        - returns True if all submitted orders have
        - been filled. Received money need not be confirmed via blockchain
        - returns False otherwise
        '''
        return NotImplemented

    # not all exchanges have the same min volumes!
    def get_min_vol(self, currency, depth):
        '''
        retrieving the minimum order volume for a pair is easy if (base_alt) is
        already a tradeable market on the exchange. However, in many situations this is
        not the case, and it is important for Triangular Arbitrage strategies to be able
        to handle flipped markets.
        In the case of a flipped market, we must infer the minimum volume based on how much of
        ALT we would end up trading, so therefore we must also convert the hardcoded min volumes
        using the current going price for the order.
        '''
        test = self.get_validated_currency(currency)
        if test is not None:
            true_pair, swapped = test
            if not swapped:
                return 0.01 # 0.011 reduces likelihood we run into rounding errors. but we miss a lot of opportun
            else:
                # we need to use the depth information to calculate
                # how much alt we need to trade to fulfill min base vol
                return self.get_clipped_alt_volume(depth, 0.011)


    def get_clipped_base_volume(self, orders, desired_base_vol):
        # it is already assumed that the orders are base_alt
        # reduces given array of orders to match specific base vol
        # borrowed from the original profit calculator

        i = 1
        while utils.total_base_volume(orders[:i]) < desired_base_vol:
            i += 1
            if i > len(orders):
                # not enough orders in the orderbook!
                print('Not enough orders in orderbook to satisfy required base volume!')
                break
        # cor
        base_remainder = utils.total_base_volume(orders[:i]) - desired_base_vol
        # convert back to units base and subtract from last order
        orders[i-1].v -= base_remainder
        return orders[:i]

    def get_clipped_alt_volume(self, orders, desired_alt_volume):
        """
        desired_alt_volume is usually 0.011, because alt in this case is a proper "base"
                           that is actually listed on the exchange.
                           we want the total alts traded to equal this.
        Example:
        suppose exchange lists A_B (min_vol = 0.1) but we want to get min_vol for B_A.
        flipped_depth = a list of orders (sorted by best price) [(P1,V1), (P2,V2), (P3,V3)]
        for B_A.
        P1 * V1 = units A (either given or received)
        hopefully P1 * V1 > min_vol(A_B)
        if not, then we have to compute the difference
        diff = min_vol(A_B) - (P1 * V1) = remaining units of A that we need to spend/give
        on the remaining orders.
        iterate through the rest of the orders as long as min vol is not satisfied!
        """

        i = 1
        while utils.total_alt_volume(orders[:i]) < desired_alt_volume:
            i += 1
            if i > len(orders):
                # not enough orders in the orderbook!
                print('Not enough orders in orderbook to satisfy required alt volume!')
                break
        # more than likely, adding on the last order tacked on a bit of overshoot.
        # the remainder MUST be spanned by last order (i.e. cannot be in the second
        # to last otherwise we would have caught it)
        alt_remainder = utils.total_alt_volume(orders[:i]) - desired_alt_volume
        # convert back to units base and subtract from last order
        orders[i-1].v -= alt_remainder/orders[i-1].p
        return sum([o.v for o in orders[:i]])


    def get_validated_currency(self, currency):
        """
        use this to check for existence of a supported
        pair for the exchagne
        returns (true_pair, swapped)
        else if pair isn't even traded, return None
        """
        if currency in self.__currencies:
            return True
        else:
            return None

    # def set_tradeable_currencies(self):
    #     """
    #     once tradeable pairs initialized, build list of all tradeable currencies.
    #     will be needed for triangular arb strategy.
    #     """
    #     # C = {}
    #     # for (base, alt) in self.tradeable_pairs:
    #     #     C[base] = ''
    #     #     C[alt] = ''
    #     # self.tradeable_currencies = list(C.keys())
    #     self.tradeable_currencies = self.tradeable_pairs



# -*- coding: utf-8 -*-
# Api Documents Url https://apidocs.korbit.co.kr

# from api_token import *

from common.Exchange import Exchange
from common.order import Order

import urllib
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import hmac
import hashlib
import json

class KORBIT(Exchange):
    """docstring for Korbit.co.kr"""
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
        self.base_api_url = "https://api.korbit.co.kr"
        self.__currencies = None
        super(KORBIT, self).__init__()
        self.name = str.upper('KORBIT')
        self.trading_fee = 0.002
        self.timestamp = 0

    # @property
    # implemented abstract functions
    @property
    def get_currencies(self):
        '''
        현재 베타 서비스중. btc_krw, eth_krw, etc_krw, xrp_krw 만 지원
        '''
        # if self.__currencies is None:
        #     tickers = self.unauthenticated_request('ticker?currency=all')
        #     self.__currencies = [m for m in tickers.keys() if type(tickers[m]) == dict]
        self.__currencies = ['btc', 'eth', 'etc', 'xrp']
        return self.__currencies


    def get_orderbook(self, currency='all'):
        marketdata = {}
        orderBook = { "bids" : [], "offers" : [] }
        if currency == 'all':
            marketdata['btc'] = self.unauthenticated_request("v1/orderbook?currency_pair=btc_krw")
            marketdata['eth'] = self.unauthenticated_request("v1/orderbook?currency_pair=eth_krw")
            marketdata['etc'] = self.unauthenticated_request("v1/orderbook?currency_pair=etc_krw")
            marketdata['xrp'] = self.unauthenticated_request("v1/orderbook?currency_pair=xrp_krw")
        else:
            marketdata[currency] = self.unauthenticated_request(("v1/orderbook?currency_pair=%s_krw" % currency))

        if int(marketdata['timestamp']) > int(self.timestamp):
            self.timestamp = int(marketdata['timestamp'])
            for bid in marketdata['bids']:
                o = Order(currency, int(bid[0]), float(bid[1]))
                orderBook['bids'].append(o)

            for ask in marketdata['asks']:
                o = Order(currency, int(ask[0]), float(ask[1]))
                orderBook['offers'].append(o)

        return orderBook

    # def get_highest_bid(self, currency='all'):
    #     return -1

    # def get_lowest_offer(self, currency='all'):
    #     return -1


    # TODO: 인증 rq 완료후 진행
    def get_balance(self, currency):
        # data = self.authenticated_request('account/balance/')
        # return float(data['wallet']['available'])
        return -1

    def get_all_balances(self):
        # data = self.authenticated_request('wallet/all/', "getwallets")
        # balances = {k:float(v["a"]) for k,v in data["wallets"].items()}
        # return balances
        return -1

    def submit_order(self, gc, gv, rc, rv):
        pass
        #order_request = self.authenticated_request('market/%s/' % (working_pair), "neworder", {'order_type':order_type, 'rate':rate, 'quantity':amount,})

    def confirm_order(self, orderID):
#        get_order_request = self.authenticated_request('market/%s/' % (working_pair),"getorder",{'order_id':new_order_request['order']['id']})
#        print get_order_request
        # TODO
        pass

    # Korbit specific methods

    # Public API / GET Method
    # 90 requests per minute
    def unauthenticated_request(self, url_suffix):
        try:
            url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix))
            response = urllib2.urlopen(url_request_object)
        except:
            url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix), headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib2.urlopen(url_request_object)

        try:
            response_content = response.read()
            response_json = {}
            response_json = json.loads(response_content)
            return response_json
        finally:
            response.close()
        return "failed"

    # Private API / POST Method
    # Account/Order/Transaction API, 6 requests per second
    def authenticated_request(self, url_suffix, method, post_args={}):
        nonce = 1000
        try:
            f = open('coins-e_nonce', 'r')
            nonce = int(f.readline())
            f.close()
        finally:
            f = open('coins-e_nonce', 'w')
            nonce += 1
            f.write(str(nonce))
            f.close()

        post_args['method'] = method
        post_args['nonce'] = nonce
        try:
            post_data = urllib.urlencode(post_args)
        except:
            post_data = urllib.parse.urlencode(post_args)

        required_sign = hmac.new(self.secret, post_data, hashlib.sha512).hexdigest()
        headers = {}
        headers['key'] = self.api_key
        headers['sign'] = required_sign
        url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix),
                                             post_data,
                                             headers)
        response = urllib2.urlopen(url_request_object)


        try:
            response_content = response.read()
            response_json = json.loads(response_content)
            if not response_json['status']:
                print(response_content)
                print("request failed")
                print(response_json['message'])

            return response_json
        finally:
            response.close()
        return "failed"



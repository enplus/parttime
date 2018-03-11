# -*- coding: utf-8 -*-
# Api Documents Url https://www.gopax.co.kr/API

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

class GOPAX(Exchange):
    """docstring for gopax.co.kr"""
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
        self.base_api_url = "https://api.gopax.co.kr"
        self.__currencies = None
        super(BITHUMB, self).__init__()
        self.name = str.upper('GOPAX')
    # temporary) event fee
        self.trading_fee = 0
        self.timestamp = 0

    # @property
    # implemented abstract functions

    # def unauthenticated_request(url_suffix):
    #     url_request_object = urllib2.Request("https://api.gopax.co.kr/%s" % (url_suffix))
    #     response = urllib2.urlopen(url_request_object)
    #     response_json = {}
    #     try:
    #         response_content = response.read()
    #         response_json = json.loads(response_content)
    #         return response_json
    #     finally:
    #         response.close()
    #     return "failed"

    @property
    def get_currencies(self):
        if self.__currencies is None:
            # tickers = self.unauthenticated_request('public/ticker/all')
            # self.__currencies = [m for m in tickers['data'].keys() if type(tickers['data'][m]) == dict]
            tickers = self.unauthenticated_request('public/ticker/all')['data']
            self.__currencies = [str.lower(m) for m in tickers.keys() if type(tickers[m]) == dict]
        return self.__currencies


    def get_orderbook(self, currency=None):
        marketdata = {}
        orderBook = { "bids" : [], "offers" : [] }
        if currency is None:
            tmpData = self.unauthenticated_request('public/orderbook/all')['data']
            self.timestamp = int(tmpData['timestamp'])

            for currency in self.get_currencies:
                marketdata[currency] = tmpData[currency]
        else:
            marketdata[currency] = self.unauthenticated_request('public/orderbook/%s' % currency)['data']
            self.timestamp = int(marketdata[currency]['timestamp'])

        for currency in marketdata.keys():
            # if int(marketdata[currency]['timestamp']) > int(self.timestamp):

            for bid in marketdata[currency]['bids']:
                o = Order(currency, int(bid['price']), float(bid['quantity']))
                orderBook['bids'].append(o)

            for ask in marketdata[currency]['asks']:
                o = Order(currency, int(ask['price']), float(ask['quantity']))
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

    # Gopax specific methods

    # Public API / GET Method
    # 90 requests per minute
    def unauthenticated_request(self, url_suffix):
        url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix))
        response = urllib2.urlopen(url_request_object)
        response_json = {}
        try:
            response_content = response.read()
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


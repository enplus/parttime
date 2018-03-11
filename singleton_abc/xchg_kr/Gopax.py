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
import base64, time

class GOPAX(Exchange):
    """docstring for gopax.co.kr"""
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = base64.b64decode(secret)
        self.base_api_url = "https://api.gopax.co.kr"
        self.__currencies = None
        super(GOPAX, self).__init__()
        self.name = str.upper('GOPAX')
        self.trading_fee = 0 # temporary) event fee
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
        return -1
        if self.__currencies is None:
            # tickers = self.unauthenticated_request('public/ticker/all')
            # self.__currencies = [m for m in tickers['data'].keys() if type(tickers['data'][m]) == dict]
            tickers = self.unauthenticated_request('assets')['data']
            self.__currencies = [str.lower(m) for m in tickers.keys() if type(tickers[m]) == dict]
        return self.__currencies


    def get_orderbook(self, currency=None):
        marketdata = {}
        orderBook = { "bids" : [], "offers" : [] }
        if currency is None:
            tmpData = self.unauthenticated_request('trading-pairs')['data']
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
        data = self.authenticated_request('balances/%s' % currency.upper(), method='GET')
        return data
        # return float(data['wallet']['available'])
        # return -1

    def get_all_balances(self):
        data = self.authenticated_request('balances', method='GET')
        # balances = {k:float(v["a"]) for k,v in data["wallets"].items()}
        return data

    def submit_order(self, gc, gv, rc, rv):
        #order_request = self.authenticated_request('market/%s/' % (working_pair), "neworder", {'order_type':order_type, 'rate':rate, 'quantity':amount,})
        pass

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
    # Private API에 인증하기 위해, REST 요청에 항상 다음의 HTTP 헤더가 포함되어야 합니다.
        # API-KEY: 발급받은 API 키
        # SIGNATURE: 메시지 서명 값 (아래에 설명)
        # NONCE: 중복되지 않고 계속 증가하는 값 (통상적으로 timestamp)

    # 같은 NONCE 값이 사용되면 서버에서 거부합니다.

    # HTTP 본문의 content-type은 application/json 으로 설정해야 합니다.
    # SIGNATURE 는 다음 과정에 따라 생성합니다.

    # 1. 다음의 내용을 순서대로 문자열로 연결합니다.
        # 헤더의 NONCE 값
        # HTTP Method(대문자로): 'GET', 'POST', 'DELETE' 등
        # API 엔드포인트 경로 (예: '/orders', '/trading-pairs/ETH-KRW/book')
        # JSON 형식의 요청 변수 본문 (없을 경우 아무 문자열도 연결하지 마십시오)
    # 2. 발급 받은 secret 을 base64 로 디코딩합니다.
    # 3. 2.의 값을 secret key 로 사용하여 sha512 HMAC 으로 서명합니다.
    # 4. 3.의 값을 base64 로 인코딩합니다.

    def authenticated_request(self, url_suffix, method, post_args={}):
        # nonce = 1000
        # try:
        #     f = open('gopax_nonce', 'r')
        #     nonce = str(f.readline())
        #     f.close()
        # finally:
        #     f = open('gopax_nonce', 'w')
        #     nonce += 1
        #     f.write(str(nonce))
        #     f.close()

        headers = {}
        headers['API-KEY'] = self.api_key

        nonce = str(time.time())
        headers['NONCE'] = nonce

        if method == 'POST':
            post_args['method'] = method
            post_args['nonce'] = nonce
            try:
                post_data = urllib.urlencode(post_args)
            except:
                post_data = urllib.parse.urlencode(post_args)
            required_sign = hmac.new(self.secret, post_data, hashlib.sha512).digest()
        elif method == 'GET':
            post_data = None
            enc_url = (nonce + method + '/' + url_suffix).encode()
            required_sign = hmac.new(self.secret, enc_url, hashlib.sha512)

        headers['SIGNATURE'] = base64.b64encode(required_sign.digest())
        url_request_object = urllib2.Request("%s/%s" % (self.base_api_url, url_suffix),
                                             headers=headers)

        response = urllib2.urlopen(url_request_object)

        try:
            response_content = response.read()
            response_json = json.loads(response_content)

            # try:
            #     if response_json['errormsg']:
            #         print("request failed [%s]" % response_json['errormsg'])
            # finally:
            #     return "failed"

            return response_json
        finally:
            response.close()
        return "failed"


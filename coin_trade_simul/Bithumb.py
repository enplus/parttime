import threading
from urllib import request
import json

class Bithumb:
    def __init__(self):
        self.API_URL = 'https://api.bithumb.com/public/orderbook/btc'
        self.timestamp = 0;
        self.highest_bid_price = 0
        self.highest_bid_qty = 0
        self.lowest_ask_price = 2000000000
        self.lowest_ask_qty = 0

    def renew_info(self):
        threading.Timer(1, self.renew_info).start()
        #   print("check_point")

        data = request.urlopen(self.API_URL).read(30000)  # 문자열 개수라고 함

        json_data = json.loads(data)  # json이 데이터베이스였죠 아마?

        self.timestamp = json_data["data"]["timestamp"]      #거래 전에 타임스탬프를 비교하게 할 생각인데, 다음 작업들과 약간 시간차가 있을 지가 걱정입니다.
        self.highest_bid_price = json_data["data"]["bids"][0]["price"]  #전부 key가 price, qty로 똑같길래 잘 봤더니 []가 있더라구요. array에서 0번째 즉 제일 비싼 매수호가입니다.
        self.highest_bid_qty = json_data["data"]["bids"][0]["quantity"]
        self.lowest_ask_price = json_data["data"]["asks"][0]["price"]
        self.lowest_ask_qty = json_data["data"]["asks"][0]["quantity"]

        print("-------- bithumb info----------")
        print("time stamp : ", self.timestamp)
        print("highest bid : " , self.highest_bid_price, ", ", self.highest_bid_qty)
        print("lowest ask : ", self.lowest_ask_price, ", ", self.lowest_ask_qty)
        print(".")

        #  API를 웹 브라우저로 보면 다음과 같습니다.
        #  {"STEEM":{"BTC":0.0003107,"USD":1.2,"KRW":1363.96},"BTC":{"BTC":1,"USD":3867.08,"KRW":4389963.13},"ETH":{"BTC":0.0814,"USD":315.68,"KRW":355953.92}}

        # 제가 따라한 소스 코드는 이렇게 썼는데요  - print(json_data["STEEM"]["KRW"])
        # 즉 "STEEM"의 "KRW" 부분을 출력하라는 문법입니다.
        # 그러므로 사이트 별로 API 켜본 다음에 우리가 원하는 부분을  json_data["원하는 부분"]  에 넣어주기만 하면 파싱이 다 됩니다.

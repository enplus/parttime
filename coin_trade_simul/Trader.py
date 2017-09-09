import threading

class Trader:

    def buy(self, object, qty):
        print("buy")

    def sell(self,object, qty):
        print("sell")


    def trade(self, object_1, object_2):
        threading.Timer(1, self.trade, args=(object_1, object_2)).start()
        print("trade func is working...")
        print(object_1.lowest_ask_price)

        if object_1.timestamp==object_2.timestamp:      #시간이 똑같은지 체크
            if object_1.highest_bid_price > object_2.lowest_ask_price:  #거래소 1의 매수가가 거래소 2의 매도가보다 크면
                if object_1.highest_bid_qty >= object_2.lowest_ask_qty:  #거래소 1의 매수물량이나 거래소 2의 매도물량 중 작은 것만큼
                    self.buy(object_1, object_2.lowest_ask_qty)         #사고
                    self.sell(object_2, object_2.lowest_ask_qty)        #팜
                else:
                    self.buy(object_1, object_1.highest_bid_qty)
                    self.sell(object_2, object_1.highest_bid_qty)

            if object_2.highest_bid_price > object_1.lowest_ask_price:   #거래소 2의 매수가가 거래소 1의 매도가보다 크면면
                if object_1.highest_bid_qty >= object_2.lowest_ask_qty:  #거래소 1의 매수물량이나 거래소 2의 매도물량 중 작은 것만큼
                    self.buy(object_2, object_2.lowest_ask_qty)         #사고
                    self.sell(object_1, object_2.lowest_ask_qty)        #팜
                else:
                    self.buy(object_2, object_2.highest_bid_qty)
                    self.sell(object_2, object_2.highest_bid_qty)
        else:
            print("************ \n Time samp is not matched \n *************")     #시간이 다르다면 이와 같이 출력


#일단 간단하게 위와 같이 짰지만, 딜레이가 있을 수 밖에 없으므로 매도 매수를 가능한 물량 전부에 거는 것은 위험하지 않을까 싶습니다.
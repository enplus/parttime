
from Bithumb import Bithumb
from Coinone import Coinone
from Trader import Trader

# from Bithumb import Bithumb

API_URL = 'https://api.bithumb.com/public/ticker/all'


def main():
    print("******************* \n --Program start--- \n ******************* ")

    bithumb=Bithumb()   #bithumb 객체를 선언하고
    coinone=Coinone()
    bithumb.renew_info()    #renew_info()함수를 돌리면 쓰레드가 시작되어 api의 값을 받아오는데,
    coinone.renew_info()

    trader=Trader()
    trader.trade(bithumb, coinone)
    print("테스트용으로 메인에서 한 번만 뽑아보는 bithumb.lowest_ask_price 값입니다. : ", bithumb.lowest_ask_price)
    #여기서 bithumb객체의 lowest_ask_price를 뽑아보면 초기값인 2000000000이 나옵니다.
    #물론 메써드 내부의 쓰레드에서 값을 출력하면  잘 나오고요.
    

main()

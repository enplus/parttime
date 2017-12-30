# COINONE_MKT = ["btc", "bch", "eth", "etc", "xrp", "qtum"]
# BITHUMB_MKT = ["btc", "bch", "eth", "etc", "xrp", "qtum"]

#gmail = 'doublebind96'
COINONE_NM  = "DoubleCat"
COINONE_API = "99782586-cd66-41d8-8969-9255b7b3a045"
COINONE_KEY = "c84ff8be-e32c-4f50-8795-38e73e5582f9"
COINONE_VER = "v2" # url에 사용

#gmail = 'dbx?'
BITHUMB_NM  = ""
BITHUMB_API = "Null"
BITHUMB_KEY = "Null"

#gmail = 'doublebind96'
KORBIT_NM  = ""
KORBIT_API = "2Cv2W7x3SO9IrBbaZbbCJf2AbIWc9XuHKXqIw8BzqNbV7MTh4x7sf2CwjxSRE"
KORBIT_KEY = "ObahmRRmJK36ve99j4Ckg7xHxsIgUzkKv60BINvcImV1tA2lhp6c4g5Sa4GzD"

#gmail = 'doublebind96'
COINNEST_NM  = ""
COINNEST_API = "Null"
COINNEST_KEY = "Null"

#gmail = 'goog_acc@doublebind96'
CEXIO_NM  = ""
CEXIO_API = "Null"
CEXIO_KEY = "Null"

BINANCE_NM  = ""
BINANCE_API = "Null"
BINANCE_KEY = "Null"

# 실 거래할 거래소 List, CryptoCurrency
EXCHANGES = ["COINONE", "KORBIT", "BITHUMB"]

# currency is lowercase!!!
CURRENCIES = [ "btc", "eth", "etc" ]

TICK_DIR = './backtest_data'
USE_MULTITHREADED = False  # or True
MODE = 'BACKTEST'

# Quote
# Spread
DEBUG = False
# DEBUG = True
DEBUG_MARKETDATA = False
DEBUG_CLEARSCREEN = False
DEBUG_SPREAD = False

VALUE_REF = {
             'BTC':500.0,   # bitcoin
             'LTC':15.0,    # litecoin
             'DOGE':0.0015, # dogecoin
             'PPC':4.00,    # peercoin
             'NMC':3.90,    # namecoin
             'QRK':0.07,    # quarkcoin
             'NXT':0.056,   # nxt
             'WDC':0.18     # worldcon
             }

# PROFIT_THRESH = { k:0.01/v for k,v in VALUE_REF.items() }
# CryptoCurrency LowerCase!
MIN_SPREAD = {
        'btc': 5000,  # cf) 4,500,000 KRW
        'etc': 0.01,  # cf) 17,000 KRW
        'eth': 0.01,  # cf) 350,000 KRW
        'xrp': 0.01   # cf) 250 KRW
        }


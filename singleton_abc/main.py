from common.utils import create_brokers
from ArbitrageBot import ArbitrageBot
from Bot import DataGatherBot

import api_config as config

# brokers = create_brokers('PAPER', config.CURRENCIES, config.EXCHANGES)
# bot = ArbitrageBot(config, brokers)

# brokers = create_brokers('BACKTEST', config.CURRENCIES, config.EXCHANGES)
# bot = ArbitrageBot(config, brokers) # this automatically loads the data path file.
# backtest_data = '/Users/ericjang/Desktop/LiClipse_Workspace/btc_arbitrage/data/Mar-29-2014_19-00-35__20_14400.p'
# bot.backtest(backtest_data) # start should probably be modified to also allow time ranges (i.e. if i want to run my live trader for 2 hours)
# print('done!')

brokers = create_brokers('PAPER', config.CURRENCIES, config.EXCHANGES)
bot = DataGatherBot(config, brokers)
bot.start(sleep=1, duration=60 * 60 * 4, maxdepth=6) # 5 hours of data, one minute intervals
print('Done!')


from common.utils import create_brokers
from Bot import DataGatherBot, ArbitrageBot

import api_config as config

# QuoteMontoring - 거래소별 프리미엄 체크를 위한 봇. 기본 주기는 1분으로
brokers = create_brokers('PAPER', config.CURRENCIES, config.EXCHANGES)
Quote_bot = QuoteBot(config, brokers)
Quote_bot.start(sleep=60)
print('Done!')

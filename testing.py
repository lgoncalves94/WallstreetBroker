from utils import *

interval_mapping = {
    '1d': '1m',
    '1wk': '30m',
    '1mo': '1d',
    '1y': '1wk',
    'max': '1wk'
}

broker = WallstreetBroker()

data= broker.fetch_stock_data('AAPL','1d',interval_mapping['1d'])

print(broker.process_data(data))

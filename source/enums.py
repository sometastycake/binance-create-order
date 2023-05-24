import enum


class OrderSide(enum.Enum):
    SELL = 'SELL'
    BUY = 'BUY'


class OrderType(enum.Enum):
    LIMIT = 'LIMIT'
    MARKET = 'MARKET'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    LIMIT_MAKER = 'LIMIT_MAKER'


class SymbolStatus(enum.Enum):
    PRE_TRADING = 'PRE_TRADING'
    TRADING = 'TRADING'
    POST_TRADING = 'POST_TRADING'
    END_OF_DAY = 'END_OF_DAY'
    HALT = 'HALT'
    AUCTION_MATCH = 'AUCTION_MATCH'
    BREAK = 'BREAK'

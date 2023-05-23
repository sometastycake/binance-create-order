class BinanceHttpError(Exception):

    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return f'<Binance status={self.code} msg={self.msg}>'

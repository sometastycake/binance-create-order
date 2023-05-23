import pydantic
from yarl import URL


class Config(pydantic.BaseSettings):

    BINANCE_API_KEY: str
    BINANCE_SECRET_KEY: str
    BINANCE_API_URL: str
    BINANCE_API_TIMEOUT: int

    def get_binance_api(self, path: str) -> str:
        return str(URL(self.BINANCE_API_URL).with_path(path))

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Config()

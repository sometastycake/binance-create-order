import pydantic



class Config(pydantic.BaseSettings):

    BINANCE_API_KEY: str
    BINANCE_SECREY_KEY: str
    BINANCE_API_URL: str
    BINANCE_API_TIMEOUT: int

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Config()

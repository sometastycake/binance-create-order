import pytest
from faker import Faker

from source.clients.binance.client import BinanceClient


@pytest.fixture(scope='session')
def faker():
    return Faker()


@pytest.fixture
def binance_client():
    return BinanceClient(raise_if_error=True)

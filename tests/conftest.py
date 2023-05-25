import pytest

from source.clients.binance.client import BinanceClient


@pytest.fixture
def binance_client():
    return BinanceClient(raise_if_error=True)
import pytest
from fastapi.testclient import TestClient

from source.api.app import app
from source.clients.binance.client import BinanceClient


@pytest.fixture
def binance_client():
    return BinanceClient()


@pytest.fixture
def fast_api_app():
    return TestClient(app)

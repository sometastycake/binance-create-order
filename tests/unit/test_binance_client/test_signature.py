import datetime

import freezegun

from source.clients.binance.signature import BaseSignature
from source.config import config


class Data(BaseSignature):
    value: int
    data: str


@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
def test_signature(monkeypatch):
    monkeypatch.setattr(config, 'BINANCE_SECRET_KEY', 'SECRET')
    data = Data(
        value=10,
        data='data',
    )
    data.sign()
    assert data.signature == '224d668a41816e46fc69ab92ea570262e507d623001dda2a6013523972b2903d'


@freezegun.freeze_time(datetime.datetime(2023, 1, 1, 10, 0, 0, 0))
def test_to_query(monkeypatch):
    data = Data(
        value=10,
        data='data',
    )
    assert data.to_query() == 'recvWindow=5000&timestamp=1672567200000&value=10&data=data'

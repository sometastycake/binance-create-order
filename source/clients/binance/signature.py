import hashlib
import hmac
import time
import urllib.parse
from typing import Optional
from urllib.parse import urlencode

from pydantic import BaseModel, Field

from source.config import config


def _timestamp() -> int:
    return int(time.time() * 1000)


class BaseSignature(BaseModel):
    recvWindow: int = Field(default=5000, ge=5000, le=60000)
    timestamp: int = Field(default_factory=_timestamp)
    signature: Optional[str]

    def sign(self) -> None:
        data = self.dict(exclude_none=True)
        self.signature = hmac.new(
            key=bytes(config.BINANCE_SECRET_KEY, 'UTF-8'),
            msg=urlencode(data).encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def to_query(self) -> str:
        return urllib.parse.urlencode(self.dict(exclude_none=True))

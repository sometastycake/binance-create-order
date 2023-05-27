import abc
from typing import Any, Dict, Literal, Optional, Type, TypeVar

import aiohttp
from pydantic import BaseModel

from source.clients.binance.errors import BinanceHttpError
from source.config import config

ResponseModel = TypeVar('ResponseModel', bound=BaseModel)

HTTP_METHOD_TYPE = Literal['GET', 'POST', 'PUT']
RESPONSE_MODEL_TYPE = Optional[Type[ResponseModel]]
PARAMS_TYPE = Optional[Dict[str, Any]]
BODY_TYPE = Optional[str]


class BinanceConnectorAbstract(abc.ABC):

    @abc.abstractmethod
    async def close(self) -> None:
        ...

    @abc.abstractmethod
    async def request(
            self,
            path: str,
            method: HTTP_METHOD_TYPE,
            response_model: RESPONSE_MODEL_TYPE = None,
            body: BODY_TYPE = None,
            params: PARAMS_TYPE = None,
            **kwargs: Any,
    ) -> ResponseModel:
        ...


class DefaultBinanceConnector(BinanceConnectorAbstract):

    def __init__(self, **aiohttp_kwargs):
        self._aiohttp_kwargs = aiohttp_kwargs
        self._session: Optional[aiohttp.ClientSession] = None

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def _create_session(self) -> aiohttp.ClientSession:
        """
        Create aiohttp session.
        """
        kwargs = self._aiohttp_kwargs.copy()
        if 'timeout' not in kwargs:
            kwargs['timeout'] = aiohttp.ClientTimeout(
                total=config.BINANCE_API_TIMEOUT,
            )
        if 'connector' not in kwargs:
            kwargs['connector'] = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(**kwargs)

    async def request(
            self,
            path: str,
            method: HTTP_METHOD_TYPE,
            response_model: RESPONSE_MODEL_TYPE = None,
            body: BODY_TYPE = None,
            params: PARAMS_TYPE = None,
            **kwargs: Any,
    ) -> ResponseModel:
        """
        Send request to Binance API.
        """
        if self._session is None:
            self._session = self._create_session()
        response = await self._session.request(
            url=config.get_binance_api(path),
            method=method,
            params=params,
            data=body,
            headers={
                'X-MBX-APIKEY': config.BINANCE_API_KEY,
            },
            **kwargs,
        )
        content = await response.json()
        # TODO нужно более гибко резолвить 40х, 50х так как могут быть ошибки
        if not response.ok:
            raise BinanceHttpError(**content)
        if response_model is not None:
            return response_model.parse_obj(content)
        return content

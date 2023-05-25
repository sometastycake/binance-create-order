from pydantic import BaseModel


class APITradingStatus(BaseModel):
    isLocked: bool


class APITradingStatusResponse(BaseModel):
    data: APITradingStatus

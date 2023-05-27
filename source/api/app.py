from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from source.api.orders import orders_router

app = FastAPI(
    docs_url='/swagger',
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):  # noqa
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):  # noqa
    return PlainTextResponse(str(exc), status_code=400)


app.include_router(orders_router)

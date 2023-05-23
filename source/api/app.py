from fastapi import FastAPI
from source.api.orders import orders_router

app = FastAPI(docs_url='/swagger')

app.include_router(orders_router)
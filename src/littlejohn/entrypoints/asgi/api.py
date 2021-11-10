from typing import List

import pydantic
from fastapi import FastAPI

from littlejohn.domain.entities import StockPrice
from littlejohn.domain.service import StockService


class Healthcheck(pydantic.BaseModel):
    ok: bool


def create(service: StockService) -> FastAPI:

    api = FastAPI()

    @api.get("/health")
    def healthcheck() -> Healthcheck:
        return Healthcheck(ok=True)

    @api.get("/tickers")
    def get_portfolio() -> List[StockPrice]:
        return service.get_portfolio()

    return api

import logging
import uuid
from typing import List

import pydantic
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from littlejohn.domain.entities import (
    PriceAtDate,
    StockPrice,
    StockSymbol,
    SymbolNotFound,
)
from littlejohn.domain.service import StockService

logger = logging.getLogger(__name__)


class Healthcheck(pydantic.BaseModel):
    ok: bool


def create(service: StockService) -> FastAPI:

    api = FastAPI()
    auth = HTTPBasic()

    def get_username(credentials: HTTPBasicCredentials = Depends(auth)) -> str:
        unauthorized = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

        try:
            username = uuid.UUID(credentials.username, version=4).hex
        except Exception:
            logger.info("Invalid username")
            raise unauthorized

        if credentials.password != "":
            logger.info("Wrong password")
            raise unauthorized

        return username

    @api.get("/health")
    def healthcheck() -> Healthcheck:
        return Healthcheck(ok=True)

    @api.get("/tickers")
    def get_portfolio_current_prices(
        username: str = Depends(get_username),
    ) -> List[StockPrice]:
        return service.get_portfolio_current_prices(username=username)

    @api.get("/tickers/{symbol}/history")
    def get_historical_prices(
        symbol: StockSymbol,
        _: str = Depends(get_username),
    ) -> List[PriceAtDate]:
        result = service.get_historical_prices(symbol=symbol)
        if isinstance(result, SymbolNotFound):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result,
            )
        return result

    return api

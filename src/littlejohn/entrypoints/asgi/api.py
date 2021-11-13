import base64
import logging
import uuid
from typing import List, Optional

import pydantic
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from littlejohn.domain.entities import (
    PriceAtDate,
    StockPrice,
    StockPriceHistoryCursor,
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
            detail="Incorrect username or password",
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
        response: Response,
        symbol: StockSymbol,
        cursor: Optional[str] = None,
        _: str = Depends(get_username),
    ) -> List[PriceAtDate]:
        decoded_cursor: Optional[StockPriceHistoryCursor]
        if cursor is not None:
            try:
                decoded_cursor = StockPriceHistoryCursor.parse_raw(
                    base64.urlsafe_b64decode(cursor)
                )
            except Exception:
                logger.info("Cursor parsing failed")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid cursor",
                )
        else:
            decoded_cursor = None

        result = service.get_historical_prices(symbol=symbol, cursor=decoded_cursor)
        if isinstance(result, SymbolNotFound):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.dict(),
            )

        if result.next is not None:
            next_cursor = base64.urlsafe_b64encode(
                result.next.json().encode("utf-8")
            ).decode("utf-8")
            next_href = f"/tickers/{symbol}/history?cursor={next_cursor}"
            response.headers["Link"] = f'{next_href}; rel="next"'

        return result.data

    return api

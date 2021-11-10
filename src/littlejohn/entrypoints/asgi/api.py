import logging
import uuid
from typing import List

import pydantic
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from littlejohn.domain.entities import StockPrice
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
    def get_portfolio(username: str = Depends(get_username)) -> List[StockPrice]:
        return service.get_portfolio()

    return api

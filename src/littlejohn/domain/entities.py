import datetime
from decimal import Decimal
from typing import Mapping

from pydantic import BaseModel

__all__ = [
    "HistoricalPrices",
    "PriceAtDate",
    "StockSymbol",
    "StockPrice",
]

StockSymbol = str


def encode_price(price: Decimal) -> str:
    return str(price.quantize(Decimal(".01")))


class SymbolNotFound(BaseModel):
    symbol: StockSymbol


class StockPrice(BaseModel):
    symbol: StockSymbol
    price: Decimal

    class Config:
        json_encoders = {Decimal: encode_price}


class PriceAtDate(BaseModel):
    date: datetime.date
    price: Decimal

    class Config:
        json_encoders = {Decimal: encode_price}


HistoricalPrices = Mapping[datetime.date, Mapping[StockSymbol, Decimal]]

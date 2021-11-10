from decimal import Decimal

from pydantic import BaseModel


class StockPrice(BaseModel):
    symbol: str
    price: Decimal

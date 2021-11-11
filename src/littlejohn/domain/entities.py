from decimal import Decimal

from pydantic import BaseModel

StockSymbol = str


class StockPrice(BaseModel):
    symbol: StockSymbol
    price: Decimal

    class Config:
        json_encoders = {Decimal: lambda d: str(d.quantize(Decimal(".01")))}

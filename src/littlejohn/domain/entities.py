from decimal import Decimal

from pydantic import BaseModel


class StockPrice(BaseModel):
    symbol: str
    price: Decimal

    class Config:
        json_encoders = {Decimal: lambda d: str(d.quantize(Decimal(".01")))}

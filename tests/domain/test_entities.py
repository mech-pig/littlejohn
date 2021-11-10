import json
from decimal import Decimal

from littlejohn.domain.entities import StockPrice


def describe_stock_price():
    def json_serialization():
        stock_price = StockPrice(
            symbol="OUCH",
            price=Decimal(176.347),
        )
        expected_json = json.dumps(
            {
                "symbol": stock_price.symbol,
                "price": "176.35",
            }
        )
        assert expected_json == stock_price.json()

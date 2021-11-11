import datetime
from typing import List

from littlejohn.domain.entities import HistoricalPrices, StockSymbol
from littlejohn.domain.service import StockPriceService


class StockPriceServiceStub(StockPriceService):
    def __init__(self, historical_prices: HistoricalPrices):
        self.historical_prices = historical_prices

    def get_history(
        self,
        symbols: List[StockSymbol],
        start_from: datetime.date,
        days_in_the_past: int,
    ) -> HistoricalPrices:
        dates = (
            start_from - datetime.timedelta(days=d) for d in range(days_in_the_past)
        )
        return {
            date: {symbol: self.historical_prices[date][symbol] for symbol in symbols}
            for date in dates
        }

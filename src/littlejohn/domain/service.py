import datetime
import logging
from decimal import Decimal
from typing import Callable, List, Protocol, Union

from .entities import (
    HistoricalPrices,
    PriceAtDate,
    StockPrice,
    StockSymbol,
    SymbolNotFound,
)

logger = logging.getLogger(__name__)


class PortfolioRepository(Protocol):
    def get_user_portfolio(self, username: str) -> List[StockSymbol]:
        ...


class StockPriceService(Protocol):
    def get_history(
        self,
        symbols: List[StockSymbol],
        start_from: datetime.date,
        days_in_the_past: int,
    ) -> HistoricalPrices:
        ...


GetTodayUtc = Callable[[], datetime.date]


class StockService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        stock_price_service: StockPriceService,
        get_today_utc: GetTodayUtc,
    ) -> None:
        self.portfolio_repository = portfolio_repository
        self.get_today_utc = get_today_utc
        self.stock_price_service = stock_price_service

    def get_portfolio_current_prices(self, username: str) -> List[StockPrice]:
        logger.info(f"Returning portfolio of user {username}")
        portfolio = self.portfolio_repository.get_user_portfolio(username=username)
        return [
            StockPrice(
                symbol=symbol,
                price=Decimal(150.57),
            )
            for symbol in portfolio
        ]

    def get_historical_prices(
        self,
        symbol: StockSymbol,
    ) -> Union[List[PriceAtDate], SymbolNotFound]:
        start_from = self.get_today_utc()
        period_in_days = 90
        logger.info(
            "Get historical prices",
            f" for the last {period_in_days}",
            f" starting from {start_from}",
        )
        price_history = self.stock_price_service.get_history(
            symbols=[symbol],
            start_from=start_from,
            days_in_the_past=period_in_days,
        )
        return [
            PriceAtDate(price=price_history[date][symbol], date=date)
            for date in sorted(price_history.keys(), reverse=True)
        ]

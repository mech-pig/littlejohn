import datetime
import logging
from typing import Callable, List, Optional, Protocol, Set, Union

from .entities import (
    HistoricalPrices,
    PriceAtDate,
    StockPrice,
    StockPriceHistory,
    StockPriceHistoryCursor,
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
        length: int,
    ) -> HistoricalPrices:
        ...


GetTodayUtc = Callable[[], datetime.date]


class StockService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        stock_price_service: StockPriceService,
        get_today_utc: GetTodayUtc,
        allowed_stock_symbols: Set[StockSymbol],
    ) -> None:
        self.portfolio_repository = portfolio_repository
        self.get_today_utc = get_today_utc
        self.stock_price_service = stock_price_service
        self.allowed_stock_symbols = allowed_stock_symbols

    def get_portfolio_current_prices(self, username: str) -> List[StockPrice]:
        today = self.get_today_utc()
        logger.info(f"Returning portfolio of user {username}")
        portfolio = self.portfolio_repository.get_user_portfolio(username=username)

        logger.info(f"Retrieving stock prices of {today}")
        price_history = self.stock_price_service.get_history(
            symbols=portfolio,
            start_from=today,
            length=1,
        )
        current_prices = price_history[today]

        return [
            StockPrice(symbol=symbol, price=current_prices[symbol])
            for symbol in portfolio
        ]

    def get_historical_prices(
        self,
        symbol: StockSymbol,
        cursor: Optional[StockPriceHistoryCursor] = None,
    ) -> Union[StockPriceHistory, SymbolNotFound]:
        if symbol not in self.allowed_stock_symbols:
            logger.info(f"Symbol not found: {symbol}")
            return SymbolNotFound(symbol=symbol)

        history_length_in_days = 90
        start_from = cursor.start_from if cursor is not None else self.get_today_utc()
        next_cursor = StockPriceHistoryCursor(
            start_from=start_from - datetime.timedelta(days=history_length_in_days)
        )

        logger.info(
            "Get historical prices",
            f" for the last {history_length_in_days}",
            f" starting from {start_from}",
        )
        price_history = self.stock_price_service.get_history(
            symbols=[symbol],
            start_from=start_from,
            length=history_length_in_days,
        )
        data = [
            PriceAtDate(price=price_history[date][symbol], date=date)
            for date in sorted(price_history.keys(), reverse=True)
        ]

        return StockPriceHistory(data=data, next=next_cursor)

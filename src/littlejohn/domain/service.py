import logging
from decimal import Decimal
from typing import List, Protocol

from .entities import StockPrice, StockSymbol

logger = logging.getLogger(__name__)


class PortfolioRepository(Protocol):
    def get_user_portfolio(self, username: str) -> List[StockSymbol]:
        ...


class StockService:
    def __init__(self, portfolio_repository: PortfolioRepository) -> None:
        self.portfolio_repository = portfolio_repository

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

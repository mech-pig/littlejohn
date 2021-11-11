from typing import List, Mapping

from littlejohn.domain.entities import StockSymbol
from littlejohn.domain.service import PortfolioRepository


class PortfolioRepositoryDeterministicGenerator(PortfolioRepository):
    def __init__(self, portfolios: Mapping[str, List[StockSymbol]]):
        self.portfolios = portfolios

    def get_user_portfolio(self, username: str) -> List[StockSymbol]:
        return self.portfolios.get(username, [])

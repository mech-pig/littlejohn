from typing import List, Set

from littlejohn.domain.entities import StockSymbol
from littlejohn.domain.service import PortfolioRepository
from littlejohn.libs.random import xorshift_32_randint


class PortfolioRepositoryGenerator(PortfolioRepository):
    def __init__(
        self,
        stocks: Set[StockSymbol],
        min_stocks_in_portfolio: int,
        max_stocks_in_portfolio: int,
    ):
        if min_stocks_in_portfolio < 0:
            raise ValueError("min_stocks_in_portfolio can't be negative")

        if max_stocks_in_portfolio < 0:
            raise ValueError("max_stocks_in_portfolio can't be negative")

        if max_stocks_in_portfolio - min_stocks_in_portfolio < 0:
            raise ValueError(
                "max_stocks_in_portfolio can't be smaller than min_stocks_in_portfolio"
            )

        if max_stocks_in_portfolio > len(stocks):
            raise ValueError(
                "max_stocks_in_portfolio can't be smaller than the number of stocks available"  # noqa: E501
            )

        self.stocks = sorted(list(stocks))
        self.min_stocks_in_portfolio = min_stocks_in_portfolio
        self.max_stocks_in_portfolio = max_stocks_in_portfolio

    def get_user_portfolio(self, username: str) -> List[StockSymbol]:
        seed = sum(list(username.encode("utf-8")))
        randint = xorshift_32_randint(seed)
        available_stocks = self.stocks.copy()
        number_of_optional_stocks = (
            self.max_stocks_in_portfolio - self.min_stocks_in_portfolio
        )
        number_of_stocks_to_choose = (
            next(randint) % number_of_optional_stocks
        ) + self.min_stocks_in_portfolio

        portfolio: List[StockSymbol] = []
        for _ in range(number_of_stocks_to_choose):
            chosen_stock_index = next(randint) % len(available_stocks)
            portfolio = [*portfolio, available_stocks[chosen_stock_index]]
            available_stocks = [
                *available_stocks[:chosen_stock_index],
                *available_stocks[chosen_stock_index + 1 :],
            ]

        return sorted(portfolio)

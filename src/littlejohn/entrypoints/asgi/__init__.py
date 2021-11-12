import random
from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import FastAPI

from littlejohn.adapters.portfolio_repository import (
    PortfolioRepositoryDeterministicGenerator,
)
from littlejohn.adapters.stock_price_service import StockPriceServiceRandomWalker
from littlejohn.domain.service import StockService

from . import api


def create_app() -> FastAPI:
    random.seed(123)
    allowed_stock_symbols = {
        "AAPL",
        "MSFT",
        "GOOG",
        "AMZN",
        "FB",
        "TSLA",
        "NVDA",
        "JPM",
        "BABA",
        "JNJ",
        "WMT",
        "PG",
        "PYPL",
        "DIS",
        "ADBE",
        "PFE",
        "V",
        "MA",
        "CRM",
        "NFLX",
    }
    portfolio_repository = PortfolioRepositoryDeterministicGenerator(
        portfolios={
            "416076429e6f437c8b7dcdbc18d608ac": list(allowed_stock_symbols),
        }
    )
    stock_price_service = StockPriceServiceRandomWalker(
        zero_date=date(2021, 11, 12),
        seeds=[
            {
                "symbol": symbol,
                "price": Decimal(random.randrange(100, 150)),
                "forward_rand_seed": random.randrange(2 ** 31, 2 ** 32),
                "backward_rand_seed": random.randrange(2 ** 31, 2 ** 32),
            }
            for symbol in allowed_stock_symbols
        ],
        gain=Decimal("0.05"),
    )
    service = StockService(
        portfolio_repository=portfolio_repository,
        stock_price_service=stock_price_service,
        get_today_utc=lambda: datetime.now(tz=timezone.utc).date(),
        allowed_stock_symbols=allowed_stock_symbols,
    )
    return api.create(service=service)

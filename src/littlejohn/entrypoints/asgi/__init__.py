import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import FastAPI

from littlejohn.adapters.portfolio_repository import (
    PortfolioRepositoryDeterministicGenerator,
)
from littlejohn.adapters.stock_price_service import StockPriceServiceStub
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
    today = datetime.now(tz=timezone.utc).date()
    portfolio_repository = PortfolioRepositoryDeterministicGenerator(
        portfolios={
            "416076429e6f437c8b7dcdbc18d608ac": list(allowed_stock_symbols),
        }
    )
    stock_price_service = StockPriceServiceStub(
        historical_prices={
            date: {
                symbol: Decimal(random.randint(10, 150))
                for symbol in allowed_stock_symbols
            }
            for date in (today - timedelta(days=days) for days in range(90))
        }
    )
    service = StockService(
        portfolio_repository=portfolio_repository,
        stock_price_service=stock_price_service,
        get_today_utc=lambda: today,
        allowed_stock_symbols=allowed_stock_symbols,
    )
    return api.create(service=service)

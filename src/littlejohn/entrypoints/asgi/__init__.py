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
    available_symbols = ["TEST", "TEST2"]
    today = datetime.now(tz=timezone.utc).date()
    portfolio_repository = PortfolioRepositoryDeterministicGenerator(
        portfolios={
            "416076429e6f437c8b7dcdbc18d608ac": available_symbols,
        }
    )
    stock_price_service = StockPriceServiceStub(
        historical_prices={
            date: {
                symbol: Decimal(random.randint(10, 150)) for symbol in available_symbols
            }
            for date in (today - timedelta(days=days) for days in range(90))
        }
    )
    service = StockService(
        portfolio_repository=portfolio_repository,
        stock_price_service=stock_price_service,
        get_today_utc=lambda: today,
    )
    return api.create(service=service)

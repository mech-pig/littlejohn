from fastapi import FastAPI

from littlejohn.adapters.portfolio_repository import (
    PortfolioRepositoryDeterministicGenerator,
)
from littlejohn.domain.service import StockService

from . import api


def create_app() -> FastAPI:
    portfolio_repository = PortfolioRepositoryDeterministicGenerator(
        portfolios={
            "416076429e6f437c8b7dcdbc18d608ac": ["TEST", "TEST2"],
        }
    )
    service = StockService(portfolio_repository=portfolio_repository)
    return api.create(service=service)

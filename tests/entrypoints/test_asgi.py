import datetime
import random
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from littlejohn.adapters.portfolio_repository import (
    PortfolioRepositoryDeterministicGenerator,
)
from littlejohn.domain.entities import (
    HistoricalPrices,
    PriceAtDate,
    StockPrice,
    StockSymbol,
)
from littlejohn.domain.service import (
    PortfolioRepository,
    StockPriceService,
    StockService,
)
from littlejohn.entrypoints.asgi import api


@pytest.fixture
def today():
    return datetime.datetime.now(tz=datetime.timezone.utc).date()


ALLOWED_STOCK_SYMBOLS = [f"TEST-{n}" for n in range(23)]


class StockPriceServiceStub(StockPriceService):
    def __init__(self, historical_prices: HistoricalPrices):
        self.historical_prices = historical_prices

    def get_history(
        self,
        symbols: List[StockSymbol],
        start_from: datetime.date,
        length: int,
    ) -> HistoricalPrices:
        dates = (start_from - datetime.timedelta(days=d) for d in range(length))
        return {
            date: {symbol: self.historical_prices[date][symbol] for symbol in symbols}
            for date in dates
        }


@pytest.fixture
def make_service(today):
    def make(
        portfolio_repository: PortfolioRepository = None,
        historical_prices: Optional[HistoricalPrices] = None,
    ) -> StockService:
        return StockService(
            portfolio_repository=(
                portfolio_repository
                or PortfolioRepositoryDeterministicGenerator(portfolios={})
            ),
            stock_price_service=StockPriceServiceStub(
                historical_prices=historical_prices
                if historical_prices is not None
                else {}
            ),
            get_today_utc=lambda: today,
            allowed_stock_symbols=set(ALLOWED_STOCK_SYMBOLS),
        )

    return make


@pytest.fixture
def make_auth():
    def make(username: Optional[str] = None, password: Optional[str] = None):
        return (
            username if username is not None else uuid4().hex,
            password if password is not None else "",
        )

    return make


@pytest.fixture
def make_client(make_service):
    def make(service: StockService = None):
        app = api.create(service=service or make_service())
        return TestClient(app)

    return make


def test_healthcheck(make_client):
    response = make_client().get("/health")
    assert 200 == response.status_code
    assert {"ok": True} == response.json()


def serialize_stock_price(stock_price: StockPrice):
    return {
        "symbol": stock_price.symbol,
        "price": str(stock_price.price.quantize(Decimal(".01"))),
    }


def serialize_price_at_date(price_at_date: PriceAtDate):
    return {
        "date": price_at_date.date.isoformat(),
        "price": str(price_at_date.price.quantize(Decimal(".01"))),
    }


def describe_get_portfolio_current_prices():
    def returns_unauthorized_if_no_credentials_are_submitted(make_client):
        response = make_client().get("/tickers")
        assert 401 == response.status_code

    def returns_unauthorized_if_username_is_not_uuid4(make_client, make_auth):
        auth = make_auth(username="invalid")
        response = make_client().get("/tickers", auth=auth)
        assert 401 == response.status_code

    def returns_unauthorized_if_password_is_not_empty(make_client, make_auth):
        auth = make_auth(password="invalid")
        response = make_client().get("/tickers", auth=auth)
        assert 401 == response.status_code

    @pytest.mark.parametrize(
        "portfolio",
        [
            pytest.param(
                random.sample(ALLOWED_STOCK_SYMBOLS, k=2),
                id="multiple stocks",
            ),
            pytest.param(
                [],
                id="no stocks",
            ),
            pytest.param(
                random.sample(ALLOWED_STOCK_SYMBOLS, k=1),
                id="single stock",
            ),
        ],
    )
    def returns_current_price_of_stocks_in_user_portfolio(
        portfolio,
        make_client,
        make_service,
        make_auth,
        today,
    ):
        auth = make_auth()
        username = auth[0]
        date_range = [today - datetime.timedelta(days=d) for d in range(180)]

        historical_prices = {
            date: {
                symbol: Decimal(random.randint(10, 150))
                for symbol in ALLOWED_STOCK_SYMBOLS
            }
            for date in random.sample(date_range, len(date_range))
        }

        portfolio_current_prices = [
            StockPrice(symbol=symbol, price=price)
            for symbol, price in historical_prices[today].items()
            if symbol in portfolio
        ]
        expected_reponse = [
            serialize_stock_price(p)
            for p in sorted(portfolio_current_prices, key=lambda p: p.symbol)
        ]

        portfolio_repository = PortfolioRepositoryDeterministicGenerator(
            portfolios={
                username: portfolio,
                "other-user": random.sample(ALLOWED_STOCK_SYMBOLS, k=2),
            },
        )
        service = make_service(
            portfolio_repository=portfolio_repository,
            historical_prices=historical_prices,
        )
        response = make_client(service=service).get("/tickers", auth=auth)
        assert 200 == response.status_code
        assert expected_reponse == sorted(response.json(), key=lambda d: d["symbol"])


def describe_get_historical_prices():
    def returns_unauthorized_if_no_credentials_are_submitted(make_client):
        symbol = random.choice(ALLOWED_STOCK_SYMBOLS)
        response = make_client().get(f"/tickers/{symbol}/history")
        assert 401 == response.status_code

    def returns_unauthorized_if_username_is_not_uuid4(make_client, make_auth):
        auth = make_auth(username="invalid")
        symbol = random.choice(ALLOWED_STOCK_SYMBOLS)
        response = make_client().get(f"/tickers/{symbol}/history", auth=auth)
        assert 401 == response.status_code

    def returns_unauthorized_if_password_is_not_empty(make_client, make_auth):
        auth = make_auth(password="invalid")
        symbol = random.choice(ALLOWED_STOCK_SYMBOLS)
        response = make_client().get(f"/tickers/{symbol}/history", auth=auth)
        assert 401 == response.status_code

    def returns_historical_prices_of_requested_symbol(
        make_client,
        make_service,
        make_auth,
        today,
    ):
        date_range = [today - datetime.timedelta(days=d) for d in range(180)]
        expected_symbol, *other_symbols = random.sample(
            ALLOWED_STOCK_SYMBOLS,
            k=len(ALLOWED_STOCK_SYMBOLS),
        )
        expected_symbol_history = [
            PriceAtDate(date=date, price=Decimal(random.randint(10, 150)))
            for date in date_range
        ]
        expected_reponse = [
            serialize_price_at_date(d) for d in expected_symbol_history[:90]
        ]

        historical_prices = {
            date: {
                **{
                    symbol: Decimal(random.randint(10, 150)) for symbol in other_symbols
                },
                expected_symbol: (
                    [p.price for p in expected_symbol_history if p.date == date][0]
                ),
            }
            for date in random.sample(date_range, len(date_range))
        }
        service = make_service(historical_prices=historical_prices)
        response = make_client(service=service).get(
            f"/tickers/{expected_symbol}/history",
            auth=make_auth(),
        )
        assert 200 == response.status_code
        assert expected_reponse == response.json()

    def returns_not_found_if_requested_symbol_is_not_among_allowed_ones(
        make_client,
        make_auth,
    ):
        invalid_symbol = "invalid"
        assert invalid_symbol not in ALLOWED_STOCK_SYMBOLS
        response = make_client().get(
            f"/tickers/{invalid_symbol}/history",
            auth=make_auth(),
        )
        assert 404 == response.status_code

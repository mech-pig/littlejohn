from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from littlejohn.adapters.portfolio_repository import (
    PortfolioRepositoryDeterministicGenerator,
)
from littlejohn.domain.entities import StockPrice
from littlejohn.domain.service import PortfolioRepository, StockService
from littlejohn.entrypoints.asgi import api


@pytest.fixture
def make_service():
    def make(portfolio_repository: PortfolioRepository = None) -> StockService:
        return StockService(
            portfolio_repository=(
                portfolio_repository
                or PortfolioRepositoryDeterministicGenerator(portfolios={})
            )
        )

    return make


@pytest.fixture
def make_auth():
    def make():
        return (uuid4().hex, "")

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


def describe_get_portfolio():
    def returns_unauthorized_if_no_credentials_are_submitted(make_client):
        response = make_client().get("/tickers")
        assert 401 == response.status_code

    def returns_unauthorized_if_username_is_not_uuid4(make_client, make_auth):
        auth = make_auth()
        username = "invalid"
        password = auth[1]
        response = make_client().get("/tickers", auth=(username, password))
        assert 401 == response.status_code

    def returns_unauthorized_if_password_is_not_empty(make_client, make_auth):
        auth = make_auth()
        username = auth[0]
        password = "invalid"
        response = make_client().get("/tickers", auth=(username, password))
        assert 401 == response.status_code

    @pytest.mark.parametrize(
        "portfolio",
        [
            pytest.param(["test1", "test2"], id="multiple stocks"),
            pytest.param([], id="no stocks"),
            pytest.param(["test"], id="single stock"),
        ],
    )
    def returns_stocks_in_user_portfolio(
        portfolio,
        make_client,
        make_service,
        make_auth,
    ):
        auth = make_auth()
        username = auth[0]

        portfolio_repository = PortfolioRepositoryDeterministicGenerator(
            portfolios={
                username: portfolio,
                "other-user": ["other1", "other2", "other3"],
            },
        )
        service = make_service(portfolio_repository=portfolio_repository)
        response = make_client(service=service).get("/tickers", auth=auth)
        assert 200 == response.status_code
        assert portfolio == [data["symbol"] for data in response.json()]

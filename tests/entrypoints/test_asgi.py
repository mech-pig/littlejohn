from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from littlejohn.domain.entities import StockPrice
from littlejohn.domain.service import StockService
from littlejohn.entrypoints.asgi import api


@pytest.fixture
def make_service():
    def make() -> StockService:
        return StockService()

    return make


@pytest.fixture
def auth():
    return (uuid4().hex, "")


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

    def returns_unauthorized_if_username_is_not_uuid4(make_client, auth):
        username = "invalid"
        password = auth[1]
        response = make_client().get("/tickers", auth=(username, password))
        assert 401 == response.status_code

    def returns_unauthorized_if_password_is_not_empty(make_client, auth):
        username = auth[0]
        password = "invalid"
        response = make_client().get("/tickers", auth=(username, password))
        assert 401 == response.status_code

    def returns_portfolio_of_user(make_client, make_service, auth):
        service = make_service()
        expected_response_body = [
            serialize_stock_price(stock_price)
            for stock_price in service.get_portfolio()
        ]
        response = make_client(service=service).get("/tickers", auth=auth)
        assert 200 == response.status_code
        assert expected_response_body == response.json()

from typing import Optional

import pytest
from fastapi.testclient import TestClient

from littlejohn.domain.service import StockService
from littlejohn.entrypoints.asgi import api


@pytest.fixture()
def make_client():
    def make(service: Optional[StockService] = None) -> TestClient:
        if service is None:
            service = StockService()
        app = api.create(service=service)
        return TestClient(app)

    return make


def test_healthcheck(make_client):
    response = make_client().get("/health")
    assert 200 == response.status_code
    assert {"ok": True} == response.json()


def describe_get_portfolio():
    def returns_portfolio_of_user(make_client):
        response = make_client().get("/tickers")
        assert 200 == response.status_code

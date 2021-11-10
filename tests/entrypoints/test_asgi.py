import pytest
from fastapi.testclient import TestClient

from littlejohn.entrypoints.asgi import api


@pytest.fixture()
def client():
    app = api.create()
    return TestClient(app)


def test_healthcheck(client):
    response = client.get("/health")
    assert 200 == response.status_code
    assert {"ok": True} == response.json()

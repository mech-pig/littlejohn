from typing import Optional, Set

import pytest

from littlejohn.adapters.portfolio_repository import PortfolioRepositoryGenerator
from littlejohn.domain.entities import StockSymbol


@pytest.fixture
def make_repository():
    def make(
        max_stocks_in_portfolio: Optional[int] = None,
        min_stocks_in_portfolio: Optional[int] = None,
        stocks: Optional[Set[StockSymbol]] = None,
    ):
        stocks = stocks if stocks is not None else {f"TEST-{i}" for i in range(23)}
        return PortfolioRepositoryGenerator(
            stocks=stocks,
            min_stocks_in_portfolio=min_stocks_in_portfolio
            if min_stocks_in_portfolio is not None
            else 0,
            max_stocks_in_portfolio=max_stocks_in_portfolio
            if max_stocks_in_portfolio is not None
            else len(stocks),
        )

    return make


@pytest.mark.parametrize(
    "snapshot",
    [
        pytest.param(
            {
                "username": "",
                "portfolio": [],
            },
            id="empty",
        ),
        pytest.param(
            {
                "username": " ",
                "portfolio": [
                    "TEST-1",
                    "TEST-11",
                    "TEST-12",
                    "TEST-13",
                    "TEST-15",
                    "TEST-2",
                    "TEST-20",
                    "TEST-6",
                    "TEST-8",
                    "TEST-9",
                ],
            },
            id="space",
        ),
        pytest.param(
            {
                "username": "    ",
                "portfolio": [
                    "TEST-1",
                    "TEST-10",
                    "TEST-11",
                    "TEST-12",
                    "TEST-13",
                    "TEST-14",
                    "TEST-15",
                    "TEST-16",
                    "TEST-17",
                    "TEST-18",
                    "TEST-19",
                    "TEST-2",
                    "TEST-20",
                    "TEST-5",
                    "TEST-6",
                    "TEST-8",
                    "TEST-9",
                ],
            },
            id="multiple spaces",
        ),
        pytest.param(
            {
                "username": "\t",
                "portfolio": [
                    "TEST-0",
                    "TEST-10",
                    "TEST-11",
                    "TEST-13",
                    "TEST-16",
                    "TEST-17",
                    "TEST-18",
                    "TEST-2",
                    "TEST-22",
                    "TEST-3",
                    "TEST-4",
                    "TEST-6",
                    "TEST-7",
                ],
            },
            id="tab",
        ),
        pytest.param(
            {
                "username": "\n",
                "portfolio": [
                    "TEST-0",
                    "TEST-10",
                    "TEST-11",
                    "TEST-12",
                    "TEST-14",
                    "TEST-15",
                    "TEST-16",
                    "TEST-18",
                    "TEST-19",
                    "TEST-2",
                    "TEST-21",
                    "TEST-22",
                    "TEST-3",
                    "TEST-6",
                    "TEST-7",
                    "TEST-8",
                    "TEST-9",
                ],
            },
            id="newline",
        ),
        pytest.param(
            {
                "username": "😀👩‍🌾🙋‍♀️🏊‍♂️",
                "portfolio": ["TEST-10", "TEST-19", "TEST-4"],
            },
            id="non-asci",
        ),
        pytest.param(
            {
                "username": "1",
                "portfolio": [
                    "TEST-0",
                    "TEST-10",
                    "TEST-11",
                    "TEST-12",
                    "TEST-13",
                    "TEST-14",
                    "TEST-16",
                    "TEST-17",
                    "TEST-18",
                    "TEST-2",
                    "TEST-20",
                    "TEST-21",
                    "TEST-22",
                    "TEST-3",
                    "TEST-4",
                    "TEST-5",
                    "TEST-6",
                    "TEST-7",
                    "TEST-9",
                ],
            },
            id="single digit",
        ),
        pytest.param({"username": "11784", "portfolio": []}, id="multiple digits"),
        pytest.param(
            {
                "username": "👾s1%%s`-02=3!lcm1784",
                "portfolio": [
                    "TEST-0",
                    "TEST-1",
                    "TEST-11",
                    "TEST-12",
                    "TEST-13",
                    "TEST-14",
                    "TEST-15",
                    "TEST-16",
                    "TEST-17",
                    "TEST-18",
                    "TEST-19",
                    "TEST-2",
                    "TEST-20",
                    "TEST-21",
                    "TEST-22",
                    "TEST-3",
                    "TEST-4",
                    "TEST-5",
                    "TEST-7",
                    "TEST-9",
                ],
            },
            id="mixed",
        ),
    ],
)
def test_generator_get_portfolio(make_repository, snapshot):
    portfolio = make_repository().get_user_portfolio(username=snapshot["username"])
    assert snapshot["portfolio"] == portfolio


@pytest.mark.parametrize(
    "params, err_msg",
    [
        pytest.param(
            {"min_stocks_in_portfolio": -1},
            "min_stocks_in_portfolio can't be negative",
        ),
        pytest.param(
            {"max_stocks_in_portfolio": -1},
            "max_stocks_in_portfolio can't be negative",
        ),
        pytest.param(
            {"min_stocks_in_portfolio": 2, "max_stocks_in_portfolio": 1},
            "max_stocks_in_portfolio can't be smaller than min_stocks_in_portfolio",
        ),
        pytest.param(
            {"stocks": ["TEST"], "max_stocks_in_portfolio": 2},
            "max_stocks_in_portfolio can't be smaller than the number of stocks available",  # noqa: E501
        ),
    ],
)
def test_params_validation(make_repository, params, err_msg):
    with pytest.raises(ValueError, match=err_msg):
        make_repository(**params)

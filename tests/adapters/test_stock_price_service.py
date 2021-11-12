import datetime
import random
from decimal import Decimal
from typing import List, Optional

import pytest

from littlejohn.adapters.stock_price_service import (
    StockPriceGeneratorSeeds,
    StockPriceServiceRandomWalker,
)

ZERO_DATE = datetime.date.today()
SEEDS = [
    {
        "symbol": f"TEST-{i}",
        "price": Decimal(random.randrange(100, 150)),
        "forward_rand_seed": random.randrange(2 ** 31, 2 ** 32),
        "backward_rand_seed": random.randrange(2 ** 31, 2 ** 32),
    }
    for i in range(random.randrange(5, 10))
]


@pytest.fixture
def make_service():
    def make(
        zero_date: Optional[datetime.date] = None,
        seeds: Optional[List[StockPriceGeneratorSeeds]] = None,
        gain: Optional[Decimal] = None,
    ) -> StockPriceServiceRandomWalker:
        return StockPriceServiceRandomWalker(
            zero_date=zero_date if zero_date is not None else ZERO_DATE,
            seeds=seeds if seeds is not None else SEEDS,
            gain=gain if gain is not None else Decimal("0.1"),
        )

    return make


def describe_random_walk_generator_get_history():

    SYMBOLS_TEST_PARAMS = [
        pytest.param([], id="no symbol"),
        pytest.param([s["symbol"] for s in SEEDS], id="all symbols"),
        pytest.param(
            [s["symbol"] for s in random.sample(SEEDS, k=1)],
            id="single symbol",
        ),
        pytest.param(
            [
                s["symbol"]
                for s in random.sample(SEEDS, k=random.randrange(2, len(SEEDS) - 1))
            ],
            id="multiple symbols",
        ),
    ]

    LENGTH_PARAMS = [0, 1, 90, 180]

    START_DATE_TEST_PARAMS = [
        pytest.param(
            ZERO_DATE,
            id="zero date",
        ),
        pytest.param(
            ZERO_DATE + datetime.timedelta(days=1),
            id="one day after zero date",
        ),
        pytest.param(
            ZERO_DATE - datetime.timedelta(days=1),
            id="one day before zero date",
        ),
        pytest.param(
            ZERO_DATE + datetime.timedelta(days=365 * 11),
            id="~11 years after zero date",
        ),
        pytest.param(
            ZERO_DATE - datetime.timedelta(days=365 * 11),
            id="~11 years before zero date",
        ),
    ]

    @pytest.mark.parametrize("symbols", SYMBOLS_TEST_PARAMS)
    @pytest.mark.parametrize("start_date", START_DATE_TEST_PARAMS)
    @pytest.mark.parametrize("length", LENGTH_PARAMS)
    def only_request_symbols_are_returned(make_service, symbols, start_date, length):
        history = make_service().get_history(
            symbols=symbols,
            start_from=start_date,
            length=length,
        )
        for date, prices in history.items():
            assert set(symbols) == set(prices.keys())

    @pytest.mark.parametrize("symbols", SYMBOLS_TEST_PARAMS)
    @pytest.mark.parametrize("start_date", START_DATE_TEST_PARAMS)
    @pytest.mark.parametrize("length", LENGTH_PARAMS)
    def only_requested_period_is_returned(make_service, symbols, start_date, length):
        history = make_service().get_history(
            symbols=symbols,
            start_from=start_date,
            length=length,
        )
        expected_dates = {
            start_date - datetime.timedelta(days=i) for i in range(length)
        }
        assert expected_dates == set(history.keys())

    @pytest.mark.parametrize("symbols", SYMBOLS_TEST_PARAMS)
    def price_at_given_date_remains_the_same_even_if_generate_from_different_instances(
        make_service,
        symbols,
    ):
        period_after_zero_date = datetime.timedelta(days=random.randrange(10, 101))
        period_before_zero_date = datetime.timedelta(days=random.randrange(10, 101))

        date_after_zero_date = ZERO_DATE + period_after_zero_date

        all_history = make_service().get_history(
            symbols=symbols,
            start_from=date_after_zero_date,
            length=period_after_zero_date.days + period_before_zero_date.days,
        )

        history_after_zero_date = make_service().get_history(
            symbols=symbols,
            start_from=date_after_zero_date,
            length=period_after_zero_date.days,
        )

        for date, prices in history_after_zero_date.items():
            assert prices == all_history[date]

        history_before_zero_date = make_service().get_history(
            symbols=symbols,
            start_from=ZERO_DATE,
            length=period_before_zero_date.days,
        )

        for date, prices in history_before_zero_date.items():
            assert prices == all_history[date]

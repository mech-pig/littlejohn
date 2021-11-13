import datetime
from decimal import Decimal
from typing import Generator, List, TypedDict

from littlejohn.domain.entities import HistoricalPrices, StockSymbol
from littlejohn.domain.service import StockPriceService
from littlejohn.libs.random import xorshift_32_rand

__all__ = [
    "StockPriceServiceRandomWalker",
    "StockPriceGeneratorSeeds",
]


class Iterations(TypedDict):
    forward: int
    backward: int


def determine_iterations(
    zero_date: datetime.date,
    start_date: datetime.date,
    length: int,
) -> Iterations:
    end_date = start_date - datetime.timedelta(days=length)
    return {
        "forward": (start_date - zero_date).days if start_date > zero_date else 0,
        "backward": (zero_date - end_date).days if end_date < zero_date else 0,
    }


def random_walk(
    rand: Generator[float, None, None],
    initial_value: Decimal,
    gain: Decimal,
    iterations: int,
) -> List[Decimal]:
    walk: List[Decimal] = []
    current_value = initial_value
    for _ in range(iterations):
        sign = Decimal("-1") if next(rand) < 0.5 else Decimal("1")
        current_value = current_value + sign * gain * current_value
        walk = [*walk, current_value]
    return walk


class StockPriceGeneratorSeeds(TypedDict):
    symbol: StockSymbol
    price: Decimal
    backward_rand_seed: int
    forward_rand_seed: int


class StockPriceServiceRandomWalker(StockPriceService):
    def __init__(
        self,
        zero_date: datetime.date,
        seeds: List[StockPriceGeneratorSeeds],
        gain: Decimal,
    ):
        self.zero_date = zero_date
        self.seeds = seeds
        self.gain = gain

    def get_history(
        self,
        symbols: List[StockSymbol],
        start_from: datetime.date,
        length: int,
    ) -> HistoricalPrices:
        required_seeds = [seed for seed in self.seeds if seed["symbol"] in symbols]
        iterations = determine_iterations(
            zero_date=self.zero_date,
            start_date=start_from,
            length=length,
        )
        forward_walks = {
            s["symbol"]: random_walk(
                rand=xorshift_32_rand(s["forward_rand_seed"]),
                initial_value=s["price"],
                gain=self.gain,
                iterations=iterations["forward"],
            )
            for s in required_seeds
        }
        historical_prices_after_zero_date = {
            (self.zero_date + datetime.timedelta(days=i + 1)): {
                symbol: walk[i] for symbol, walk in forward_walks.items()
            }
            for i in range(iterations["forward"])
        }

        backward_walks = {
            s["symbol"]: random_walk(
                rand=xorshift_32_rand(s["backward_rand_seed"]),
                initial_value=s["price"],
                gain=self.gain,
                iterations=iterations["backward"],
            )
            for s in required_seeds
        }
        historical_prices_before_zero_date = {
            (self.zero_date - datetime.timedelta(days=i + 1)): {
                symbol: walk[i] for symbol, walk in backward_walks.items()
            }
            for i in range(iterations["backward"])
        }

        generated_historical_prices = {
            **historical_prices_after_zero_date,
            self.zero_date: {s["symbol"]: s["price"] for s in required_seeds},
            **historical_prices_before_zero_date,
        }

        # this must include the start_from
        required_dates = [
            start_from - datetime.timedelta(days=i) for i in range(length)
        ]

        return {date: generated_historical_prices[date] for date in required_dates}

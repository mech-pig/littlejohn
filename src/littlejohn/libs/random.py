from typing import Generator


def xorshift_32_rand(seed: int) -> Generator[float, None, None]:
    max_value = 2 ** 32
    for value in xorshift_32_randint(seed):
        yield value / max_value


def xorshift_32_randint(seed: int) -> Generator[int, None, None]:
    current_seed = seed
    max_value = 2 ** 32
    while True:
        current_seed ^= current_seed << 13
        current_seed ^= current_seed >> 17
        current_seed ^= current_seed << 5
        current_seed %= max_value
        yield current_seed

import logging
from decimal import Decimal
from typing import List

from .entities import StockPrice

logger = logging.getLogger(__name__)


class StockService:
    def __init__(self) -> None:
        pass

    def get_portfolio(self) -> List[StockPrice]:
        logger.info("Returning portfolio")
        return [StockPrice(symbol="OUCH", price=Decimal(150.57))]

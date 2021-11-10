from fastapi import FastAPI

from littlejohn.domain.service import StockService

from . import api


def create_app() -> FastAPI:
    service = StockService()
    return api.create(service=service)

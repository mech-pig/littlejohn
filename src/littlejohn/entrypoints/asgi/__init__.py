from fastapi import FastAPI

from . import api


def create_app() -> FastAPI:
    return api.create()

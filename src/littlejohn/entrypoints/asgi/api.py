import pydantic
from fastapi import FastAPI


class Healthcheck(pydantic.BaseModel):
    ok: bool


def create() -> FastAPI:

    api = FastAPI()

    @api.get("/health")
    def healthcheck() -> Healthcheck:
        return Healthcheck(ok=True)

    return api

FROM python:3.9-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR="/var/cache/pypoetry"

WORKDIR /home/littlejohn


RUN pip install --no-cache poetry && poetry --version

COPY ./poetry.lock ./pyproject.toml /home/littlejohn/

# install production dependencies
RUN poetry install --no-interaction --no-dev --no-ansi --no-root \
    && rm -rf ${POETRY_CACHE_DIR}

COPY ./src/ /home/littlejohn/src/
COPY ./gunicorn.conf.py /home/littlejohn/gunicorn.conf.py

# install root package
RUN poetry install --no-interaction --no-dev --no-ansi \
    && rm -rf ${POETRY_CACHE_DIR}

# run as non-root user
RUN groupadd -r web \
    && useradd -d /home/littlejohn -r -g web littlejohn \
    && chown littlejohn:web -R /home/littlejohn

USER littlejohn

EXPOSE 8080

ENV HTTP_PORT=8080

ENTRYPOINT [ "poetry", "run", "gunicorn", "littlejohn.entrypoints.asgi:create_app()" ]

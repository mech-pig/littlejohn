## Run with docker

The easiest way to run `LittleJohn` is via docker.
Build the image with

```sh
docker build -t littlejohn .
```

and then start the server

```sh
docker run -p 8080:8080 littlejohn
```

## API

Use [httpie](https://httpie.io/) to try the examples. Users can authenticate using basic authentication. Username must be a valid UUIDv4 token, while the password is empty.

### Get portfolio
Returns a list of stocks in the user's portfolio with today's price.

```sh
http -a 416076429e6f437c8b7dcdbc18d608a4: GET :8080/tickers 

HTTP/1.1 200 OK
content-length: 170
content-type: application/json
date: Sat, 13 Nov 2021 23:29:18 GMT
server: uvicorn

[
    {
        "price": "118.75",
        "symbol": "DIS"
    },
    {
        "price": "156.45",
        "symbol": "FB"
    },
    {
        "price": "102.60",
        "symbol": "JNJ"
    },
    {
        "price": "127.30",
        "symbol": "MA"
    },
    {
        "price": "125.40",
        "symbol": "NVDA"
    }
]
```

### Get historical prices

Returns a list of prices for a given ticker in the last 90 days, in descending order.

```sh
http -a 416076429e6f437c8b7dcdbc18d608a4: GET :8080/tickers/AAPL/history

HTTP/1.1 200 OK
content-length: 3439
content-type: application/json
date: Sat, 13 Nov 2021 23:32:56 GMT
link: /tickers/AAPL/history?cursor=eyJzdGFydF9mcm9tIjogIjIwMjEtMDgtMTUifQ==; rel="next"
server: uvicorn

[
    {
        "date": "2021-11-13",
        "price": "96.90"
    },
    {
        "date": "2021-11-12",
        "price": "102.00"
    },
    ...
    {
        "date": "2021-08-16",
        "price": "50.12"
    }
]
```

As you can see from the `link` header in the response, this api supports pagination.
Follow the `next` url to retrieve the prices for the next 90 days:

```sh
http -a 416076429e6f437c8b7dcdbc18d608a4: GET ':8080/tickers/AAPL/history?cursor=eyJzdGFydF9mcm9tIjogIjIwMjEtMDgtMTUifQ=='

HTTP/1.1 200 OK
content-length: 3421
content-type: application/json
date: Sat, 13 Nov 2021 23:35:32 GMT
link: /tickers/AAPL/history?cursor=eyJzdGFydF9mcm9tIjogIjIwMjEtMDUtMTcifQ==; rel="next"
server: uvicorn

[
    {
        "date": "2021-08-15",
        "price": "52.62"
    },
    {
        "date": "2021-08-14",
        "price": "55.25"
    },
    ...
    {
        "date": "2021-05-18",
        "price": "40.51"
    }
]
```

If a specific stock is not found, a 404 error is returned.

```sh
http -a 416076429e6f437c8b7dcdbc18d608a4: GET :8080/tickers/unkown/history

HTTP/1.1 404 Not Found
content-length: 30
content-type: application/json
date: Sat, 13 Nov 2021 23:39:17 GMT
server: uvicorn

{
    "detail": {
        "symbol": "unkown"
    }
}
```

## Local development

### Dependencies
- python 3.9
- [poetry](https://python-poetry.org/)
- `make` (not strictly required, see `Makefile` if you want to run the commands without it) 

### Install dependencies

```
make install-dev
```

### Start development server
```sh
make dev
```

By default, the server will be listenning on port `8080`.

### Run static analisys
```sh
make check
```

### Run tests
```sh
make test
```
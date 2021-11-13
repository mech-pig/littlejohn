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
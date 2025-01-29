# WEBASH

## Prerequisite
Make sure the following tools are installed in your machine:
- `python3.13` (or greater) programming language
- `Docker` containerization platform
- `poetry` package manager

## Docker configuration
Configure Docker daemon for TCP connection by following this [GIST](https://gist.github.com/styblope/dc55e0ad2a9848f2cc3307d4819d819f)

## Set Up

1. Clone project:
```shell
git clone git@github.com:mirzomumin/webash.git
```

2. Move to **webash** directory:
```shell
cd webash
```

3. Create virtual environment with *poetry*:
```shell
poetry shell
```

4. Install packages

```shell
poetry install --no-root
```

5. Create *.env* file and define your project variables as showen in *.env.example* one.

## Launch

1. Make database in docker container

```shell
make db
```

2. Make database migration

```shell
make migrate
```

3. Launch main(fastapi) app

```shell
make app
```

4. Launch bot app

```shell
make bot
```

5. Go to local address `http://127.0.0.1:8000` and start using webash terminal

###################################################

## Extra commands

Make migration file

```shell
make migration message="<migration message>"
```

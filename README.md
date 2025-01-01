# WEBASH

## Set Up

## Commands

1. Launch main(fastapi) app

```shell
fastapi dev ./src/main.py
```

2. Launch bot app

```shell
python3 -m src.bot.app
```

3. Make migration file

```shell
alembic revision --autogenerate -m "migration message"
```

4. Make database migration

```shell
alembic upgrade head
```

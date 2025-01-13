app:
	fastapi dev ./src/main.py

bot:
	python3 -m src.bot.app

db:
	docker compose up -d

migration:
	alembic revision --autogenerate -m "$(message)"

migrate:
	alembic upgrade head

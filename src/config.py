import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_URL = os.environ["DB_URL"]
    BOT_TOKEN = os.environ["BOT_TOKEN"]


settings = Settings()
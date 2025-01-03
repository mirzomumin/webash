import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DB_URL: str = os.environ["DB_URL"]
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ALGORITHM: str = os.environ["ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.environ["ACCESS_TOKEN_EXPIRE_SECONDS"])
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(os.environ["REFRESH_TOKEN_EXPIRE_SECONDS"])


settings = Settings()

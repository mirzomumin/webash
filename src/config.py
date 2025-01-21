import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings:
    DB_URL: str = os.environ["DB_URL"]
    BOT_TOKEN: str = os.environ["BOT_TOKEN"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    ALGORITHM: str = os.environ["ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.environ["ACCESS_TOKEN_EXPIRE_SECONDS"])
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(os.environ["REFRESH_TOKEN_EXPIRE_SECONDS"])
    DOCKER_SOCKET_PATH: str = os.environ["DOCKER_SOCKET_PATH"]
    TEST_DB_URL: str = os.environ["TEST_DB_URL"]


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "webashapp"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


settings = Settings()

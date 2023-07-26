import os
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):

    DEBUG: Optional[bool] = None

    VERSION = "1.7.0"

    PROJECT_NAME: Optional[str] = "Betfair application"

    X_APPLICATION_ID: Optional[str]
    NAME: Optional[str]
    PASSWORD: Optional[str]
    CERTNAME: Optional[str]
    REDIS_BROKER_URL: Optional[str]
    REDIS_URL: Optional[str]

    # @classmethod
    # def db_fields(cls):
    #     user = os.getenv("MARIADB_USER")
    #     password = os.getenv("MARIADB_PASSWORD")
    #     host = os.getenv("MARIADB_HOST")
    #     db = os.getenv('MARIADB_DB')
    #     port = os.getenv('MARIADB_PORT', 3306)
    #     return user, password, host, db, port

    # @validator("DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str]) -> str:
    #     if isinstance(v, str):
    #         return v

    #     user, password, host, db, port = cls.db_fields()
    #     return f"mariadb+mariadbconnector://{user}:{password}@{host}:{port}/{db}"

    class Config:
        env_file = ".env"


config = Settings()

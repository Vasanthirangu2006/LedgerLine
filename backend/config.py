
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Use Neon PostgreSQL with psycopg 3.
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )
        elif DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # Keep the existing local PostgreSQL configuration.
        SQLALCHEMY_DATABASE_URI = URL.create(
            drivername="postgresql+psycopg",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

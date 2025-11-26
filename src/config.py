import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1@localhost/population_db")
    DATA_SOURCE = os.getenv("DATA_SOURCE", "WIKIPEDIA").upper()

config = Config()
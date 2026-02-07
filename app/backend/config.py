from os import getenv


class Config:
    SECRET_KEY: str | None = getenv("SECRET_KEY")
    MINDEE_API_KEY: str | None = getenv("MINDEE_API_KEY")
    MINDEE_MODEL_ID: str | None = getenv("MINDEE_MODEL_ID")

from os import getenv


class Config:
    SECRET_KEY = getenv("SECRET_KEY")
    EXPLAIN_TEMPLATE_LOADING = False
    TEMPLATES_AUTO_RELOAD = True
    MINDEE_API_KEY = getenv("MINDEE_API_KEY")

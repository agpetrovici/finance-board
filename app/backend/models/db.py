from os import getenv

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(engine_options={"url": getenv("SQLALCHEMY_DATABASE_URI")})

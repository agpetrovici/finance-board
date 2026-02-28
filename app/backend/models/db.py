from os import getenv
from typing import Generator

from shapely.geometry import Point
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import UserDefinedType

engine = create_engine(getenv("SQLALCHEMY_DATABASE_URI", ""))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PointType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self):
        return "POINT"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            if isinstance(value, Point):
                return f"({value.x},{value.y})"
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            x, y = value.strip("()").split(",")
            return Point(float(x), float(y))
        return process


class PolygonType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self):
        return "POLYGON"

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            if isinstance(value, list):
                points = ",".join(f"({x},{y})" for x, y in value)
                return f"({points})"
            return value
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            inner = value.strip("()")
            points = []
            for pair in inner.split("),("):
                x, y = pair.strip("()").split(",")
                points.append([float(x), float(y)])
            return points
        return process


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

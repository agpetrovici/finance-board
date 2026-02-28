from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.backend.models.db import Base, PointType


class RealEstateLandPlotComparable(Base):
    __tablename__ = "e_real_estate_land_plot_comparable"

    pk_real_estate_land_plot_comparable: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    re_type: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    surface: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_square_meter: Mapped[float] = mapped_column(Float, nullable=False)

    reference: Mapped[str] = mapped_column(String(255), nullable=False)

    coordinates: Mapped[object] = mapped_column(PointType, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    seller_type: Mapped[str] = mapped_column(String(255), nullable=False)

    date_created: Mapped[str] = mapped_column(DateTime, nullable=False)
    date_updated: Mapped[str] = mapped_column(DateTime, nullable=False)
    date_deleted: Mapped[str | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<RealEstateLandPlotComparable {self.title} {self.price} {self.surface} {self.price_per_square_meter}>"

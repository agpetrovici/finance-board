from sqlalchemy import DateTime, ForeignKey, Integer, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.backend.models.db import Base, PointType


class RealEstateLandPlot(Base):
    __tablename__ = "e_real_estate_land_plot"

    pk_real_estate_land_plot: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    fk_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_fiat_account.account_pk"), nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    re_type: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    surface: Mapped[float] = mapped_column(Float, nullable=False)

    reference: Mapped[str] = mapped_column(String(255), nullable=False)

    coordinates: Mapped[object] = mapped_column(PointType, nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<RealEstateLandPlot {self.title} {self.price} {self.surface} {self.price_per_square_meter}>"

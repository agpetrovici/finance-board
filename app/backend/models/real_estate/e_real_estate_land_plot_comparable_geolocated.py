from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.backend.models.db import Base, PointType


class RealEstateLandPlotComparableGeolocated(Base):
    __tablename__ = "e_real_estate_land_plot_comparable_geolocated"

    pk_reference20: Mapped[str] = mapped_column(String(20), primary_key=True)

    surface: Mapped[float] = mapped_column(Float, nullable=False)
    coordinates: Mapped[object] = mapped_column(PointType, nullable=False)

    address: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<RealEstateLandPlotComparableGeolocated {self.surface} {self.coordinates}>"

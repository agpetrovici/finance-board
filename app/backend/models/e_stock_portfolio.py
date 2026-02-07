from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockPortfolio(Base):
    __tablename__ = "e_stock_portfolio"

    pk_stock_portfolio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    fk_stock_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_stock_account.pk_stock_account"), nullable=False)
    fk_isin: Mapped[str] = mapped_column(String(12), ForeignKey("m_isin.pk_isin"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<StockPortfolio {self.fk_isin} {self.quantity}>"

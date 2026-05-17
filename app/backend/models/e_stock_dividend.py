from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockDividend(Base):
    __tablename__ = "e_stock_dividend"

    pk_stock_dividend: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_stock_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_stock_account.pk_stock_account"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    execution_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    fk_isin: Mapped[str] = mapped_column(String(12), ForeignKey("m_isin.pk_isin"), nullable=False)
    asset_name: Mapped[str | None] = mapped_column(String(200))
    shares: Mapped[float] = mapped_column(Numeric(18, 10), nullable=False)

    # Net amount credited to the account in user's base currency (after tax)
    amount: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=False)

    # Original values when a currency conversion took place
    original_amount: Mapped[float | None] = mapped_column(Numeric(10, 4))
    original_currency: Mapped[str | None] = mapped_column(String(3), ForeignKey("m_currency.code"))
    fx_rate: Mapped[float | None] = mapped_column(Numeric(10, 6))

    # Withheld tax (negative in the CSV, stored as-is)
    tax: Mapped[float | None] = mapped_column(Numeric(10, 4))

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<StockDividend {self.fk_isin} {self.execution_date} {self.amount}>"

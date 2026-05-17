from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockCashTransfer(Base):
    __tablename__ = "e_stock_cash_transfer"

    pk_stock_cash_transfer: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_stock_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_stock_account.pk_stock_account"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=False)
    execution_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    transfer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    counterparty_name: Mapped[str | None] = mapped_column(String(200))
    counterparty_iban: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<StockCashTransfer {self.transfer_type} {self.execution_date} {self.amount}>"

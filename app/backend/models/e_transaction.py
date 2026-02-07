from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class FiatTransaction(Base):
    __tablename__ = "e_fiat_transaction"

    transaction_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[str] = mapped_column(DateTime, nullable=False)
    account_fk: Mapped[int] = mapped_column(Integer, ForeignKey("m_fiat_account.account_pk"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100))
    subcategory: Mapped[str | None] = mapped_column(String(100))

    name: Mapped[str | None] = mapped_column(String(100))
    concept: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    bank_id: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Transaction {self.date} {self.description} {self.amount}>"

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class Deposit(Base):
    __tablename__ = "e_deposit"

    pk_movement: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_fiat_account.account_pk"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    interest_maturity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date_start: Mapped[str] = mapped_column(DateTime, nullable=False)
    date_end: Mapped[str] = mapped_column(DateTime, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    name: Mapped[str | None] = mapped_column(String(100))
    concept: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    bank_id: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Deposit {self.date_start} {self.description} {self.amount}>"

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class Account(Base):
    __tablename__ = "m_fiat_account"

    account_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100))
    currency: Mapped[str | None] = mapped_column(String(10))
    description: Mapped[str | None] = mapped_column(String(255))
    # Bank account identification
    bank_name: Mapped[str | None] = mapped_column(String(100))
    bank_code: Mapped[str | None] = mapped_column(String(8))
    branch_code: Mapped[str | None] = mapped_column(String(8))
    control_digits: Mapped[str | None] = mapped_column(String(10))
    account_number: Mapped[str | None] = mapped_column(String(100))
    bank_id: Mapped[str | None] = mapped_column(String(50))  # unique and internal identifier that the bank provides for the account
    # Timestamps
    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Account {self.name}>"

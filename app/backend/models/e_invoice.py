from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class Invoice(Base):
    __tablename__ = "e_invoice"

    pk_invoice: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    gross_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    net_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[str] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[str | None] = mapped_column(DateTime)
    fk_payment: Mapped[int | None] = mapped_column(Integer, ForeignKey("e_fiat_transaction.transaction_pk"))

    # Invoice details
    description: Mapped[str | None] = mapped_column(Text)
    fk_client: Mapped[int | None] = mapped_column(Integer, ForeignKey("m_client.pk_client"))

    # Tax information
    retention_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), default=0)
    retention_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), default=0)
    vat_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), default=0)
    vat_rate: Mapped[float | None] = mapped_column(Numeric(5, 2), default=0)

    # Metadata
    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} {self.date} {self.gross_amount}>"

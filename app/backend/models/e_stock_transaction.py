from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockTransaction(Base):
    __tablename__ = "e_stock_transaction"

    pk_stock_transaction: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fk_stock_account: Mapped[int] = mapped_column(Integer, ForeignKey("m_stock_account.pk_stock_account"), nullable=False)

    order_id: Mapped[str] = mapped_column(String(100), nullable=False)  # id stored by the broker
    execution_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    fk_isin: Mapped[str] = mapped_column(String(12), ForeignKey("m_isin.pk_isin"), nullable=False)
    fk_order_type: Mapped[int] = mapped_column(Integer, ForeignKey("m_order_type.pk_order_type"), nullable=False)
    fk_order_class: Mapped[int] = mapped_column(Integer, ForeignKey("m_order_class.pk_order_class"), nullable=False)
    fk_reference_exchange: Mapped[str | None] = mapped_column(String(3), ForeignKey("m_reference_exchange.pk_reference_exchange"), nullable=True)
    fk_execution_venue: Mapped[str | None] = mapped_column(String(10), ForeignKey("m_execution_venue.pk_execution_venue"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Broker price per share
    price_per_share_value: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    price_per_share_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    value_broker: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    value_broker_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)

    # User value
    value_user: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    value_user_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    cost_autofx_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    cost_autofx_currency: Mapped[str | None] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=True)
    external_costs_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    external_costs_currency: Mapped[str | None] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=True)
    total_costs_value: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_costs_currency: Mapped[str | None] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=True)

    # Final total charged to the user in their currency (value_user_currency + total_costs_eur)
    total_user_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_user_currency: Mapped[str] = mapped_column(String(3), ForeignKey("m_currency.code"), nullable=False)

    created_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<StockTransaction {self.execution_date} {self.fk_order_type} {self.total_user_currency}>"

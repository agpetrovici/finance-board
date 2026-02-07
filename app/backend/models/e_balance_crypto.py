from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class BalanceCrypto(Base):
    __tablename__ = "e_crypto_balance"

    fk_account_crypto: Mapped[int] = mapped_column(Integer, ForeignKey("m_crypto_account.pk_account_crypto"), nullable=False)
    timestamp: Mapped[str] = mapped_column(DateTime, nullable=False)
    asset: Mapped[str] = mapped_column(String(100), nullable=False)

    free: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    locked: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("fk_account_crypto", "timestamp", "asset"),)

    def __repr__(self) -> str:
        return f"<BalanceCrypto {self.timestamp} {self.asset} {self.free}>"

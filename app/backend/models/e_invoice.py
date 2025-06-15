from app.backend.models.db import db


class Invoice(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "e_invoice"

    pk_invoice = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    gross_amount = db.Column(db.Numeric(10, 2), nullable=False)
    net_amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime)
    fk_payment = db.Column(db.Integer, db.ForeignKey("e_fiat_transaction.transaction_pk"))

    # Invoice details
    description = db.Column(db.Text)
    fk_client = db.Column(db.Integer, db.ForeignKey("m_client.pk_client"))

    # Tax information
    retention_amount = db.Column(db.Numeric(10, 2), default=0)
    retention_rate = db.Column(db.Numeric(5, 2), default=0)
    vat_amount = db.Column(db.Numeric(10, 2), default=0)
    vat_rate = db.Column(db.Numeric(5, 2), default=0)

    # Metadata
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} {self.date} {self.amount}>"

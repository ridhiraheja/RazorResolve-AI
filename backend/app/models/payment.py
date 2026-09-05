from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    TIMEOUT = "timeout"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CARD = "card"
    NETBANKING = "netbanking"
    WALLET = "wallet"
    EMI = "emi"
    COD = "cod"


class FailureReason(str, enum.Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    TECHNICAL_ERROR = "technical_error"
    TIMEOUT = "timeout"
    BANK_DECLINE = "bank_decline"
    FRAUD_SUSPECTED = "fraud_suspected"
    INVALID_CARD = "invalid_card"
    UPI_FAILURE = "upi_failure"
    NETWORK_ERROR = "network_error"
    NONE = "none"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    method = Column(SAEnum(PaymentMethod))
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.CREATED)
    failure_reason = Column(SAEnum(FailureReason), default=FailureReason.NONE)
    failure_message = Column(Text)
    gateway_payment_id = Column(String(100))
    attempt_count = Column(Integer, default=1)
    is_webhook_delivered = Column(Boolean, default=False)
    webhook_attempts = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    captured_at = Column(DateTime)
    failed_at = Column(DateTime)

    order = relationship("Order", back_populates="payments")
    events = relationship("PaymentEvent", back_populates="payment")


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="events")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), ForeignKey("payments.id"))
    event_type = Column(String(100))
    status = Column(String(50))  # delivered, failed, pending
    payload = Column(JSON)
    delivery_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

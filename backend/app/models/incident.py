from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class IncidentType(str, enum.Enum):
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_TIMEOUT = "payment_timeout"
    CHECKOUT_ABANDONED = "checkout_abandoned"
    MULTIPLE_ATTEMPTS = "multiple_attempts"
    WEBHOOK_FAILURE = "webhook_failure"
    DUPLICATE_PAYMENT = "duplicate_payment"
    HIGH_VALUE_AT_RISK = "high_value_at_risk"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    ACTION_REQUIRED = "action_required"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True)
    type = Column(SAEnum(IncidentType), nullable=False)
    severity = Column(SAEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM)
    status = Column(SAEnum(IncidentStatus), default=IncidentStatus.NEW)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    order_id = Column(String(36), ForeignKey("orders.id"))
    payment_id = Column(String(36))
    amount_at_risk = Column(Float, default=0.0)
    root_cause = Column(Text)
    confidence_score = Column(Float, default=0.0)
    evidence = Column(JSON)
    recommended_action = Column(Text)
    expected_recovery = Column(Float, default=0.0)
    risk_level = Column(String(20))
    auto_executable = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    policy_result = Column(String(20))  # ALLOW / REVIEW / BLOCK
    ai_explanation = Column(Text)
    resolved_at = Column(DateTime)
    recovered_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="incidents")
    ai_decisions = relationship("AIDecision", back_populates="incident")

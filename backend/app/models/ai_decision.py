from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class DecisionType(str, enum.Enum):
    PAYMENT_DIAGNOSIS = "payment_diagnosis"
    RECOVERY_ACTION = "recovery_action"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    INTENT_ANALYSIS = "intent_analysis"
    SAFETY_EVALUATION = "safety_evaluation"
    INCIDENT_CREATION = "incident_creation"


class AIDecision(Base):
    __tablename__ = "ai_decisions"

    id = Column(String(36), primary_key=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"))
    agent_name = Column(String(100), nullable=False)
    decision_type = Column(SAEnum(DecisionType))
    observation = Column(Text)
    reasoning = Column(Text)
    decision = Column(Text)
    action_taken = Column(Text)
    policy_result = Column(String(20))
    confidence_score = Column(Float, default=0.0)
    expected_impact = Column(Float, default=0.0)
    actual_result = Column(Text)
    evidence = Column(JSON)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="ai_decisions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent = Column(String(100))
    incident_id = Column(String(36))
    observation = Column(Text)
    decision = Column(Text)
    action = Column(Text)
    policy_result = Column(String(20))
    result = Column(Text)
    confidence = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSON)

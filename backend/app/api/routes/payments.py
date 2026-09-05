from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models import Payment, PaymentStatus, PaymentMethod, Customer, Order
from app.agents.payment_agent import diagnose_payment
from typing import Optional

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("")
async def list_payments(
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Payment).order_by(desc(Payment.created_at))
    if status:
        try:
            q = q.where(Payment.status == PaymentStatus(status))
        except ValueError:
            pass
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    payments = result.scalars().all()

    out = []
    for p in payments:
        customer_name = None
        if p.customer_id:
            c_r = await db.execute(select(Customer).where(Customer.id == p.customer_id))
            cust = c_r.scalar_one_or_none()
            customer_name = cust.name if cust else None
        out.append({
            "id": p.id,
            "order_id": p.order_id,
            "customer_id": p.customer_id,
            "customer_name": customer_name,
            "amount": p.amount,
            "currency": p.currency,
            "method": p.method,
            "status": p.status,
            "failure_reason": p.failure_reason,
            "failure_message": p.failure_message,
            "attempt_count": p.attempt_count,
            "is_webhook_delivered": p.is_webhook_delivered,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "captured_at": p.captured_at.isoformat() if p.captured_at else None,
            "failed_at": p.failed_at.isoformat() if p.failed_at else None,
        })
    return {"payments": out, "total": len(out)}


@router.get("/{payment_id}")
async def get_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")

    customer_name = None
    if p.customer_id:
        c_r = await db.execute(select(Customer).where(Customer.id == p.customer_id))
        cust = c_r.scalar_one_or_none()
        customer_name = cust.name if cust else None

    # Run AI diagnosis
    minutes_since = 0
    if p.failed_at:
        import datetime
        minutes_since = int((datetime.datetime.utcnow() - p.failed_at).total_seconds() / 60)

    diagnosis = diagnose_payment(
        payment_status=str(p.status.value) if p.status else "unknown",
        failure_reason=str(p.failure_reason.value) if p.failure_reason else "none",
        amount=p.amount,
        attempt_count=p.attempt_count or 1,
        webhook_delivered=p.is_webhook_delivered,
        webhook_attempts=p.webhook_attempts or 0,
        minutes_since_failure=minutes_since,
    )

    return {
        "id": p.id,
        "order_id": p.order_id,
        "customer_id": p.customer_id,
        "customer_name": customer_name,
        "amount": p.amount,
        "currency": p.currency,
        "method": p.method,
        "status": p.status,
        "failure_reason": p.failure_reason,
        "failure_message": p.failure_message,
        "attempt_count": p.attempt_count,
        "is_webhook_delivered": p.is_webhook_delivered,
        "webhook_attempts": p.webhook_attempts,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "captured_at": p.captured_at.isoformat() if p.captured_at else None,
        "failed_at": p.failed_at.isoformat() if p.failed_at else None,
        "ai_diagnosis": {
            "incident_type": diagnosis.incident_type,
            "severity": diagnosis.severity,
            "root_cause": diagnosis.root_cause,
            "confidence_score": diagnosis.confidence_score,
            "evidence": diagnosis.evidence,
            "recommended_action": diagnosis.recommended_action,
            "expected_recovery": diagnosis.expected_recovery,
            "risk_level": diagnosis.risk_level,
            "policy_result": diagnosis.policy_result,
            "auto_executable": diagnosis.auto_executable,
            "requires_approval": diagnosis.requires_approval,
            "ai_explanation": diagnosis.ai_explanation,
        },
    }

"""
Webhook replay + payment timeline endpoints.
"""
import uuid
import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models import (
    Payment, PaymentEvent, WebhookEvent,
    Order, Customer, Incident, IncidentStatus,
    AIDecision, AuditLog,
)
from app.agents.payment_agent import diagnose_payment
from app.agents.policy_agent import evaluate_policy
from app.models import Cart, CartStatus, DecisionType

router = APIRouter(tags=["payments-extended"])


def _uid():
    return str(uuid.uuid4())

def _now():
    return datetime.datetime.utcnow()


# ── GET /api/v1/payments/{payment_id}/timeline ────────────────────────────────

@router.get("/payments/{payment_id}/timeline")
async def get_payment_timeline(payment_id: str, db: AsyncSession = Depends(get_db)):
    """Full event timeline + AI diagnosis for a payment."""
    r = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = r.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")

    # Events
    ev_r = await db.execute(
        select(PaymentEvent).where(PaymentEvent.payment_id == payment_id).order_by(PaymentEvent.created_at)
    )
    events = ev_r.scalars().all()

    # Webhook events
    wh_r = await db.execute(select(WebhookEvent).where(WebhookEvent.payment_id == payment_id))
    webhooks = wh_r.scalars().all()

    # Order
    ord_r = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = ord_r.scalar_one_or_none()

    # Customer
    customer = None
    if payment.customer_id:
        c_r = await db.execute(select(Customer).where(Customer.id == payment.customer_id))
        customer = c_r.scalar_one_or_none()

    # Incident
    inc_r = await db.execute(
        select(Incident).where(Incident.payment_id == payment_id).order_by(Incident.created_at.desc())
    )
    incident = inc_r.scalar_one_or_none()

    # AI Decisions
    decisions = []
    if incident:
        dec_r = await db.execute(
            select(AIDecision).where(AIDecision.incident_id == incident.id).order_by(AIDecision.created_at)
        )
        decisions = dec_r.scalars().all()

    # Audit logs for this incident
    audit_logs = []
    if incident:
        al_r = await db.execute(
            select(AuditLog).where(AuditLog.incident_id == incident.id).order_by(AuditLog.timestamp)
        )
        audit_logs = al_r.scalars().all()

    # Run AI diagnosis
    minutes_since = 0
    if payment.failed_at:
        minutes_since = int((_now() - payment.failed_at).total_seconds() / 60)

    diagnosis = diagnose_payment(
        payment_status=str(payment.status.value) if payment.status else "unknown",
        failure_reason=str(payment.failure_reason.value) if payment.failure_reason else "none",
        amount=payment.amount,
        attempt_count=payment.attempt_count or 1,
        webhook_delivered=payment.is_webhook_delivered,
        webhook_attempts=payment.webhook_attempts or 0,
        minutes_since_failure=minutes_since,
    )

    # Build timeline
    timeline = []

    if order:
        timeline.append({"time": order.created_at.isoformat() if order.created_at else None,
                         "event": "order_created", "label": "Order Created",
                         "detail": f"Order ₹{order.total_amount:,.0f}", "status": "done"})

    for ev in events:
        label_map = {
            "payment.created":   ("Payment Initiated",  "done"),
            "payment.attempted": ("Payment Attempted",  "done"),
            "payment.captured":  ("Payment Captured",   "success"),
            "payment.failed":    ("Payment Failed",     "error"),
            "payment.recovered": ("Payment Recovered",  "success"),
            "webhook.replayed":  ("Webhook Replayed",   "success"),
        }
        lbl, st = label_map.get(ev.event_type, (ev.event_type, "done"))
        timeline.append({"time": ev.created_at.isoformat() if ev.created_at else None,
                         "event": ev.event_type, "label": lbl,
                         "detail": str(ev.payload or ""), "status": st})

    for wh in webhooks:
        timeline.append({"time": wh.created_at.isoformat() if wh.created_at else None,
                         "event": "webhook_event", "label": f"Webhook {wh.status.upper()}",
                         "detail": f"{wh.delivery_attempts} attempts", "status": "error" if wh.status == "failed" else "success"})

    if incident:
        timeline.append({"time": incident.created_at.isoformat() if incident.created_at else None,
                         "event": "incident_created", "label": "AI Incident Created",
                         "detail": incident.type, "status": "ai"})

    for dec in decisions:
        timeline.append({"time": dec.created_at.isoformat() if dec.created_at else None,
                         "event": "ai_decision", "label": f"AI: {dec.decision}",
                         "detail": f"{dec.agent_name} — confidence {int(dec.confidence_score*100)}%",
                         "status": "ai"})

    if incident and incident.resolved_at:
        timeline.append({"time": incident.resolved_at.isoformat(),
                         "event": "resolved", "label": "Incident Resolved",
                         "detail": f"Recovered ₹{incident.recovered_amount:,.0f}", "status": "success"})

    timeline.sort(key=lambda x: x["time"] or "")

    return {
        "payment": {
            "id": payment.id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "method": payment.method,
            "status": payment.status,
            "failure_reason": payment.failure_reason,
            "failure_message": payment.failure_message,
            "attempt_count": payment.attempt_count,
            "is_webhook_delivered": payment.is_webhook_delivered,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "captured_at": payment.captured_at.isoformat() if payment.captured_at else None,
            "failed_at": payment.failed_at.isoformat() if payment.failed_at else None,
        },
        "order": {
            "id": order.id, "status": order.status,
            "total_amount": order.total_amount, "items": order.items or [],
        } if order else None,
        "customer": {
            "id": customer.id, "name": customer.name, "email": customer.email, "tier": customer.tier,
        } if customer else None,
        "incident": {
            "id": incident.id, "type": incident.type, "severity": incident.severity,
            "status": incident.status, "root_cause": incident.root_cause,
            "confidence_score": incident.confidence_score,
            "recommended_action": incident.recommended_action,
            "policy_result": incident.policy_result,
            "ai_explanation": incident.ai_explanation,
            "evidence": incident.evidence,
            "requires_approval": incident.requires_approval,
            "recovered_amount": incident.recovered_amount,
        } if incident else None,
        "ai_diagnosis": {
            "incident_type": diagnosis.incident_type,
            "severity": diagnosis.severity,
            "root_cause": diagnosis.root_cause,
            "confidence_score": diagnosis.confidence_score,
            "evidence": diagnosis.evidence,
            "recommended_action": diagnosis.recommended_action,
            "policy_result": diagnosis.policy_result,
            "auto_executable": diagnosis.auto_executable,
            "ai_explanation": diagnosis.ai_explanation,
        },
        "timeline": timeline,
        "audit_logs": [
            {"timestamp": a.timestamp.isoformat() if a.timestamp else None,
             "agent": a.agent, "decision": a.decision, "action": a.action,
             "policy_result": a.policy_result, "result": a.result, "confidence": a.confidence}
            for a in audit_logs
        ],
    }


# ── POST /api/v1/webhooks/{payment_id}/replay ─────────────────────────────────

@router.post("/webhooks/{payment_id}/replay")
async def replay_webhook(payment_id: str, db: AsyncSession = Depends(get_db)):
    """Replay a failed webhook delivery (simulated)."""
    r = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = r.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")

    if payment.is_webhook_delivered:
        raise HTTPException(400, "Webhook already delivered for this payment")

    now = _now()

    payment.is_webhook_delivered = True
    payment.webhook_attempts = (payment.webhook_attempts or 0) + 1

    wh_r = await db.execute(select(WebhookEvent).where(WebhookEvent.payment_id == payment_id))
    wh = wh_r.scalar_one_or_none()
    if wh:
        wh.status = "delivered"
        wh.delivered_at = now
        wh.delivery_attempts = (wh.delivery_attempts or 0) + 1

    # Update order
    ord_r = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = ord_r.scalar_one_or_none()
    if order:
        from app.models import OrderStatus
        order.status = OrderStatus.COMPLETED

    db.add(PaymentEvent(id=_uid(), payment_id=payment_id,
                        event_type="webhook.replayed", payload={"replayed_at": now.isoformat()}, created_at=now))

    # Resolve incident
    inc_r = await db.execute(
        select(Incident).where(Incident.payment_id == payment_id).order_by(Incident.created_at.desc())
    )
    incident = inc_r.scalar_one_or_none()
    if incident:
        incident.status = IncidentStatus.RESOLVED
        incident.recovered_amount = payment.amount
        incident.resolved_at = now

    db.add(AuditLog(
        id=_uid(), timestamp=now,
        agent="RecoveryAgent",
        incident_id=incident.id if incident else None,
        observation=f"Webhook replay requested for payment {payment_id[:8]}",
        decision="REPLAY_WEBHOOK",
        action="Webhook replayed, order state updated (simulated)",
        policy_result="ALLOW",
        result="Success",
        confidence=0.97,
    ))

    await db.commit()
    return {
        "payment_id": payment_id,
        "webhook_replayed": True,
        "order_status": "completed",
        "incident_resolved": incident.id if incident else None,
        "timestamp": now.isoformat(),
    }


# ── POST /api/v1/recovery/{incident_id}/execute ───────────────────────────────

@router.post("/recovery/{incident_id}/execute")
async def execute_incident_recovery(incident_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    """Execute recovery for an abandoned cart incident."""
    r = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = r.scalar_one_or_none()
    if not incident:
        raise HTTPException(404, "Incident not found")

    if incident.status == IncidentStatus.RESOLVED:
        raise HTTPException(400, "Incident already resolved")

    action = body.get("action", "SEND_RECOVERY_MESSAGE")
    policy = evaluate_policy("send_recovery_message", incident.amount_at_risk)

    now = _now()

    if policy.verdict == "BLOCK":
        raise HTTPException(403, f"Policy BLOCK: {policy.reason}")

    # Simulate recovery
    recovered = incident.expected_recovery or incident.amount_at_risk * 0.7
    incident.status = IncidentStatus.RESOLVED
    incident.recovered_amount = recovered
    incident.resolved_at = now
    incident.requires_approval = False

    # If linked to a cart, mark it recovered
    if incident.order_id:
        cart_r = await db.execute(
            select(Cart).where(Cart.customer_id == incident.customer_id).order_by(Cart.created_at.desc())
        )
        cart = cart_r.scalar_one_or_none()
        if cart and cart.status == CartStatus.ABANDONED:
            cart.status = CartStatus.RECOVERED
            cart.recovered_at = now

    db.add(AIDecision(
        id=_uid(), incident_id=incident_id,
        agent_name="RecoveryAgent",
        decision_type=DecisionType.RECOVERY_ACTION,
        observation=f"Abandoned cart recovery — ₹{incident.amount_at_risk:,.0f}",
        reasoning=f"Action {action} selected. Intent score justifies intervention.",
        decision=action,
        action_taken=f"Recovery message sent, customer redirected to checkout (simulated)",
        policy_result=policy.verdict,
        confidence_score=0.88,
        expected_impact=recovered,
        actual_result="success",
        created_at=now,
    ))

    db.add(AuditLog(
        id=_uid(), timestamp=now,
        agent="RecoveryAgent",
        incident_id=incident_id,
        observation=f"Recovery executed for incident {incident_id[:8]}",
        decision=action,
        action="Customer recovery message sent, checkout completed (simulated)",
        policy_result=policy.verdict,
        result="Success",
        confidence=0.88,
    ))

    await db.commit()
    return {
        "incident_id": incident_id,
        "action": action,
        "policy_verdict": policy.verdict,
        "status": "resolved",
        "recovered_amount": recovered,
        "timestamp": now.isoformat(),
        "agent_steps": [
            {"step": "OBSERVE",    "label": "Abandoned cart detected",         "done": True},
            {"step": "UNDERSTAND", "label": "Customer intent scored",          "done": True},
            {"step": "DECIDE",     "label": "Best intervention selected",      "done": True},
            {"step": "POLICY",     "label": f"Policy: {policy.verdict}",       "done": True},
            {"step": "ACT",        "label": "Recovery message sent",           "done": True},
            {"step": "VERIFY",     "label": "Customer returned to checkout",   "done": True},
            {"step": "LEARN",      "label": f"Recovered ₹{recovered:,.0f}",    "done": True},
        ],
    }

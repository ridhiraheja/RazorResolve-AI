"""
Checkout simulation router.
All payment processing is SIMULATED — no real Razorpay API calls.
"""
import uuid
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models import (
    Customer, Order, OrderStatus,
    Payment, PaymentStatus, PaymentMethod, FailureReason, PaymentEvent, WebhookEvent,
    Incident, IncidentType, IncidentSeverity, IncidentStatus,
    AIDecision, AuditLog, DecisionType,
    Cart, CartStatus,
)
from app.agents.payment_agent import diagnose_payment
from app.agents.policy_agent import evaluate_policy

router = APIRouter(prefix="/checkout", tags=["checkout"])


# ── Request / Response models ─────────────────────────────────────────────────

class PayRequest(BaseModel):
    order_id: Optional[str] = None          # existing order or None → auto-create
    customer_id: Optional[str] = None
    amount: float
    payment_method: str                      # upi | card | netbanking | wallet
    items: Optional[list] = None             # [{product_id, name, qty, price}]
    simulation_scenario: str = "SUCCESS"     # SUCCESS|TEMPORARY_FAILURE|TIMEOUT|INSUFFICIENT_FUNDS|WEBHOOK_FAILURE|DUPLICATE_PAYMENT


class RecoverRequest(BaseModel):
    payment_id: str
    recovery_action: str   # RETRY_ALTERNATE | REPLAY_WEBHOOK | APPLY_DISCOUNT | MANUAL_REVIEW


class ExecuteRecoveryRequest(BaseModel):
    action: str
    notes: Optional[str] = None


# ── Scenario maps ─────────────────────────────────────────────────────────────

SCENARIO_CONFIG = {
    "SUCCESS": {
        "status": PaymentStatus.CAPTURED,
        "failure_reason": FailureReason.NONE,
        "failure_message": None,
        "is_webhook_delivered": True,
    },
    "TEMPORARY_FAILURE": {
        "status": PaymentStatus.FAILED,
        "failure_reason": FailureReason.TECHNICAL_ERROR,
        "failure_message": "Payment gateway returned TECH_FAILURE_503. Temporary processing outage.",
        "is_webhook_delivered": False,
    },
    "TIMEOUT": {
        "status": PaymentStatus.TIMEOUT,
        "failure_reason": FailureReason.TIMEOUT,
        "failure_message": "Payment request timed out after 30 seconds.",
        "is_webhook_delivered": False,
    },
    "INSUFFICIENT_FUNDS": {
        "status": PaymentStatus.FAILED,
        "failure_reason": FailureReason.INSUFFICIENT_FUNDS,
        "failure_message": "Bank returned INSUFFICIENT_BALANCE. Transaction declined.",
        "is_webhook_delivered": False,
    },
    "WEBHOOK_FAILURE": {
        "status": PaymentStatus.CAPTURED,
        "failure_reason": FailureReason.NONE,
        "failure_message": None,
        "is_webhook_delivered": False,   # payment OK but webhook fails
    },
    "DUPLICATE_PAYMENT": {
        "status": PaymentStatus.CAPTURED,
        "failure_reason": FailureReason.NONE,
        "failure_message": None,
        "is_webhook_delivered": True,
    },
}

SCENARIO_INCIDENT_TYPE = {
    "TEMPORARY_FAILURE": IncidentType.PAYMENT_FAILED,
    "TIMEOUT": IncidentType.PAYMENT_TIMEOUT,
    "INSUFFICIENT_FUNDS": IncidentType.PAYMENT_FAILED,
    "WEBHOOK_FAILURE": IncidentType.WEBHOOK_FAILURE,
    "DUPLICATE_PAYMENT": IncidentType.DUPLICATE_PAYMENT,
}


# ── Helper ────────────────────────────────────────────────────────────────────

def _now():
    return datetime.datetime.utcnow()

def _uid():
    return str(uuid.uuid4())

def _method_enum(method: str) -> PaymentMethod:
    try:
        return PaymentMethod(method.lower())
    except ValueError:
        return PaymentMethod.UPI


async def _write_audit(db, agent, incident_id, observation, decision, action, policy, result, confidence):
    db.add(AuditLog(
        id=_uid(),
        timestamp=_now(),
        agent=agent,
        incident_id=incident_id,
        observation=observation,
        decision=decision,
        action=action,
        policy_result=policy,
        result=result,
        confidence=confidence,
    ))


# ── POST /api/v1/checkout/pay ─────────────────────────────────────────────────

@router.post("/pay")
async def simulate_payment(req: PayRequest, db: AsyncSession = Depends(get_db)):
    """
    Simulate a payment transaction with the chosen scenario.
    Creates order (if needed), payment, events, and triggers AI investigation for failures.
    """
    scenario = req.simulation_scenario.upper()
    if scenario not in SCENARIO_CONFIG:
        raise HTTPException(400, f"Unknown scenario: {scenario}. Valid: {list(SCENARIO_CONFIG.keys())}")

    cfg = SCENARIO_CONFIG[scenario]
    now = _now()

    # ── Resolve or create order ────────────────────────────────────────────────
    order_id = req.order_id
    customer_id = req.customer_id

    if not customer_id:
        c_res = await db.execute(select(Customer.id).limit(1))
        customer_id = c_res.scalar() or _uid()

    if not order_id:
        order_id = _uid()
        items = req.items or [{"product_id": "demo", "name": "Demo Product", "qty": 1, "price": req.amount}]
        db.add(Order(
            id=order_id,
            customer_id=customer_id,
            status=OrderStatus.PROCESSING,
            total_amount=req.amount,
            items=items,
            created_at=now,
        ))
    else:
        r = await db.execute(select(Order).where(Order.id == order_id))
        existing_order = r.scalar_one_or_none()
        if not existing_order:
            raise HTTPException(404, f"Order {order_id} not found")
        customer_id = customer_id or existing_order.customer_id

    # ── Create payment ─────────────────────────────────────────────────────────
    payment_id = _uid()
    gateway_id = f"rzp_sim_{payment_id[:8]}"

    is_captured = cfg["status"] == PaymentStatus.CAPTURED
    is_failed   = cfg["status"] in (PaymentStatus.FAILED, PaymentStatus.TIMEOUT)

    payment = Payment(
        id=payment_id,
        order_id=order_id,
        customer_id=customer_id,
        amount=req.amount,
        method=_method_enum(req.payment_method),
        status=cfg["status"],
        failure_reason=cfg["failure_reason"],
        failure_message=cfg["failure_message"],
        gateway_payment_id=gateway_id,
        attempt_count=1,
        is_webhook_delivered=cfg["is_webhook_delivered"],
        webhook_attempts=0 if cfg["is_webhook_delivered"] else 3,
        created_at=now,
        captured_at=now if is_captured else None,
        failed_at=now if is_failed else None,
    )
    db.add(payment)

    # ── Update order status ────────────────────────────────────────────────────
    r2 = await db.execute(select(Order).where(Order.id == order_id))
    order = r2.scalar_one_or_none()
    if order:
        if is_captured and scenario not in ("WEBHOOK_FAILURE", "DUPLICATE_PAYMENT"):
            order.status = OrderStatus.COMPLETED
        elif is_failed:
            order.status = OrderStatus.FAILED

    # ── Payment events ─────────────────────────────────────────────────────────
    db.add(PaymentEvent(id=_uid(), payment_id=payment_id,
                        event_type="payment.created", payload={"amount": req.amount, "method": req.payment_method}, created_at=now))
    db.add(PaymentEvent(id=_uid(), payment_id=payment_id,
                        event_type="payment.attempted", payload={"scenario": scenario}, created_at=now))

    if is_captured:
        db.add(PaymentEvent(id=_uid(), payment_id=payment_id,
                            event_type="payment.captured", payload={"gateway_id": gateway_id}, created_at=now))
    elif is_failed:
        db.add(PaymentEvent(id=_uid(), payment_id=payment_id,
                            event_type="payment.failed", payload={"reason": str(cfg["failure_reason"]), "message": cfg["failure_message"]}, created_at=now))

    # ── Webhook event for WEBHOOK_FAILURE scenario ─────────────────────────────
    if scenario == "WEBHOOK_FAILURE":
        db.add(WebhookEvent(
            id=_uid(), payment_id=payment_id,
            event_type="payment.captured",
            status="failed",
            payload={"payment_id": payment_id, "amount": req.amount},
            delivery_attempts=3,
            last_attempt_at=now,
            created_at=now,
        ))

    # ── Duplicate payment: create second capture ───────────────────────────────
    dup_payment_id = None
    if scenario == "DUPLICATE_PAYMENT":
        dup_payment_id = _uid()
        db.add(Payment(
            id=dup_payment_id,
            order_id=order_id,
            customer_id=customer_id,
            amount=req.amount,
            method=_method_enum(req.payment_method),
            status=PaymentStatus.CAPTURED,
            failure_reason=FailureReason.NONE,
            gateway_payment_id=f"rzp_sim_{dup_payment_id[:8]}",
            attempt_count=1,
            is_webhook_delivered=True,
            webhook_attempts=1,
            created_at=now,
            captured_at=now,
        ))
        db.add(PaymentEvent(id=_uid(), payment_id=dup_payment_id,
                            event_type="payment.captured", payload={"duplicate": True}, created_at=now))

    await db.flush()  # get IDs without committing

    # ── AI Investigation for non-SUCCESS scenarios ─────────────────────────────
    incident_id = None
    diagnosis = None
    agent_steps = []

    if scenario != "SUCCESS":
        # Run Payment Investigation Agent
        diagnosis = diagnose_payment(
            payment_status=str(cfg["status"].value),
            failure_reason=str(cfg["failure_reason"].value),
            amount=req.amount,
            attempt_count=1,
            webhook_delivered=cfg["is_webhook_delivered"],
            webhook_attempts=0 if cfg["is_webhook_delivered"] else 3,
            has_duplicate=(scenario == "DUPLICATE_PAYMENT"),
        )

        agent_steps = [
            {"step": "OBSERVE",    "label": "Payment failure detected",        "done": True},
            {"step": "UNDERSTAND", "label": "Payment history analyzed",        "done": True},
            {"step": "DIAGNOSE",   "label": f"{diagnosis.root_cause[:60]}...", "done": True},
            {"step": "DECIDE",     "label": diagnosis.recommended_action,      "done": True},
            {"step": "POLICY",     "label": f"Policy: {diagnosis.policy_result}", "done": True},
            {"step": "ACT",        "label": "Awaiting execution",              "done": False},
            {"step": "VERIFY",     "label": "Pending",                         "done": False},
        ]

        # Create incident
        incident_id = _uid()
        inc_type = SCENARIO_INCIDENT_TYPE.get(scenario, IncidentType.PAYMENT_FAILED)
        severity_map = {"critical": IncidentSeverity.CRITICAL, "high": IncidentSeverity.HIGH,
                        "medium": IncidentSeverity.MEDIUM, "low": IncidentSeverity.LOW}
        db.add(Incident(
            id=incident_id,
            type=inc_type,
            severity=severity_map.get(diagnosis.severity, IncidentSeverity.MEDIUM),
            status=IncidentStatus.ACTION_REQUIRED if diagnosis.auto_executable else IncidentStatus.ESCALATED,
            customer_id=customer_id,
            order_id=order_id,
            payment_id=payment_id,
            amount_at_risk=req.amount,
            root_cause=diagnosis.root_cause,
            confidence_score=diagnosis.confidence_score,
            evidence=diagnosis.evidence,
            recommended_action=diagnosis.recommended_action,
            expected_recovery=diagnosis.expected_recovery,
            risk_level=diagnosis.risk_level,
            auto_executable=diagnosis.auto_executable,
            requires_approval=diagnosis.requires_approval,
            policy_result=diagnosis.policy_result,
            ai_explanation=diagnosis.ai_explanation,
            created_at=now,
        ))

        # AI Decision record
        db.add(AIDecision(
            id=_uid(),
            incident_id=incident_id,
            agent_name="PaymentInvestigationAgent",
            decision_type=DecisionType.PAYMENT_DIAGNOSIS,
            observation=f"Payment {payment_id[:8]} {scenario} — amount ₹{req.amount:,.0f}",
            reasoning=diagnosis.ai_explanation,
            decision=diagnosis.recommended_action,
            action_taken="Incident created, recovery options prepared",
            policy_result=diagnosis.policy_result,
            confidence_score=diagnosis.confidence_score,
            expected_impact=req.amount,
            evidence={"scenario": scenario, "failure_reason": str(cfg["failure_reason"].value)},
            created_at=now,
        ))

        # Audit log
        await _write_audit(
            db, "PaymentInvestigationAgent", incident_id,
            f"Detected {scenario} for payment {payment_id[:8]} — ₹{req.amount:,.0f}",
            diagnosis.recommended_action,
            "Created incident and recovery recommendation",
            diagnosis.policy_result, "Pending", diagnosis.confidence_score,
        )

    await db.commit()

    # Build response
    base = {
        "payment_id": payment_id,
        "order_id": order_id,
        "status": str(cfg["status"].value),
        "scenario": scenario,
        "amount": req.amount,
        "gateway_payment_id": gateway_id,
        "timestamp": now.isoformat(),
        "is_webhook_delivered": cfg["is_webhook_delivered"],
    }

    if scenario == "SUCCESS":
        base["message"] = "Payment captured successfully."
    elif diagnosis:
        base.update({
            "error_code": str(cfg["failure_reason"].value),
            "error_description": cfg["failure_message"] or diagnosis.root_cause,
            "incident_id": incident_id,
            "ai_investigation": {
                "root_cause": diagnosis.root_cause,
                "confidence_score": diagnosis.confidence_score,
                "recommended_action": diagnosis.recommended_action,
                "policy_result": diagnosis.policy_result,
                "auto_executable": diagnosis.auto_executable,
                "requires_approval": diagnosis.requires_approval,
                "ai_explanation": diagnosis.ai_explanation,
                "evidence": diagnosis.evidence,
                "risk_level": diagnosis.risk_level,
                "expected_recovery": diagnosis.expected_recovery,
            },
            "agent_steps": agent_steps,
        })
        if scenario == "DUPLICATE_PAYMENT":
            base["duplicate_payment_id"] = dup_payment_id

    return base


# ── POST /api/v1/checkout/recover ─────────────────────────────────────────────

@router.post("/recover")
async def execute_recovery(req: RecoverRequest, db: AsyncSession = Depends(get_db)):
    """
    Execute a recovery action for a failed payment.
    Policy engine is always consulted first.
    """
    r = await db.execute(select(Payment).where(Payment.id == req.payment_id))
    payment = r.scalar_one_or_none()
    if not payment:
        raise HTTPException(404, "Payment not found")

    action = req.recovery_action.upper()

    # Policy check
    action_map = {
        "RETRY_ALTERNATE":  "retry_simulated_payment",
        "REPLAY_WEBHOOK":   "replay_webhook_demo",
        "APPLY_DISCOUNT":   "send_recovery_message",
        "MANUAL_REVIEW":    "large_refund",
    }
    policy_action = action_map.get(action, "suggest_retry")
    policy = evaluate_policy(policy_action, payment.amount)

    if policy.verdict == "BLOCK":
        raise HTTPException(403, f"Policy BLOCK: {policy.reason}")

    now = _now()
    recovery_id = _uid()

    # Fetch associated incident
    inc_r = await db.execute(
        select(Incident).where(Incident.payment_id == req.payment_id).order_by(Incident.created_at.desc())
    )
    incident = inc_r.scalar_one_or_none()
    incident_id = incident.id if incident else None

    result_status = "success"
    result_message = ""
    recovered_amount = 0.0

    if policy.verdict == "REVIEW":
        result_status = "pending_approval"
        result_message = f"Action requires human approval: {policy.reason}"
        if incident:
            incident.status = IncidentStatus.ESCALATED
            incident.requires_approval = True

    elif action == "RETRY_ALTERNATE":
        # Simulate successful retry via alternate method
        payment.status = PaymentStatus.CAPTURED
        payment.captured_at = now
        payment.is_webhook_delivered = True
        payment.webhook_attempts = 1

        # Update order
        ord_r = await db.execute(select(Order).where(Order.id == payment.order_id))
        order = ord_r.scalar_one_or_none()
        if order:
            order.status = OrderStatus.COMPLETED

        recovered_amount = payment.amount
        result_message = "Payment retried via alternate method. Captured successfully (simulated)."
        db.add(PaymentEvent(id=_uid(), payment_id=payment.id,
                            event_type="payment.recovered", payload={"action": action, "method": "alternate"}, created_at=now))
        if incident:
            incident.status = IncidentStatus.RESOLVED
            incident.recovered_amount = payment.amount
            incident.resolved_at = now

    elif action == "REPLAY_WEBHOOK":
        payment.is_webhook_delivered = True
        payment.webhook_attempts = (payment.webhook_attempts or 0) + 1

        # Find and update webhook event
        wh_r = await db.execute(select(WebhookEvent).where(WebhookEvent.payment_id == payment.id))
        wh = wh_r.scalar_one_or_none()
        if wh:
            wh.status = "delivered"
            wh.delivered_at = now
            wh.delivery_attempts = (wh.delivery_attempts or 0) + 1

        # Update order if it was stuck in processing
        ord_r = await db.execute(select(Order).where(Order.id == payment.order_id))
        order = ord_r.scalar_one_or_none()
        if order and order.status == OrderStatus.PROCESSING:
            order.status = OrderStatus.COMPLETED

        recovered_amount = payment.amount
        result_message = "Webhook replayed successfully. Order state updated (simulated)."
        db.add(PaymentEvent(id=_uid(), payment_id=payment.id,
                            event_type="webhook.replayed", payload={"action": action}, created_at=now))
        if incident:
            incident.status = IncidentStatus.RESOLVED
            incident.recovered_amount = payment.amount
            incident.resolved_at = now

    elif action == "APPLY_DISCOUNT":
        # Simulate recovery message sent
        result_message = "Recovery message with discount offer sent to customer (simulated)."
        recovered_amount = 0.0
        if incident:
            incident.status = IncidentStatus.RECOVERING

    # AI Decision log
    db.add(AIDecision(
        id=recovery_id,
        incident_id=incident_id,
        agent_name="RecoveryAgent",
        decision_type=DecisionType.RECOVERY_ACTION,
        observation=f"Recovery requested for payment {req.payment_id[:8]}",
        reasoning=f"Action {action} selected. Policy: {policy.verdict}",
        decision=action,
        action_taken=result_message,
        policy_result=policy.verdict,
        confidence_score=0.92,
        expected_impact=recovered_amount,
        actual_result=result_status,
        created_at=now,
    ))

    await _write_audit(
        db, "RecoveryAgent", incident_id,
        f"Recovery action {action} for payment {req.payment_id[:8]}",
        action, result_message, policy.verdict,
        "Success" if result_status == "success" else result_status,
        0.92,
    )

    await db.commit()

    return {
        "recovery_id": recovery_id,
        "payment_id": req.payment_id,
        "action": action,
        "policy_verdict": policy.verdict,
        "policy_reason": policy.reason,
        "status": result_status,
        "message": result_message,
        "recovered_amount": recovered_amount,
        "incident_id": incident_id,
        "timestamp": now.isoformat(),
    }


# ── GET /api/v1/checkout/{order_id} ──────────────────────────────────────────

@router.get("/{order_id}")
async def get_checkout(order_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Order).where(Order.id == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    pay_r = await db.execute(select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at.desc()))
    payments = pay_r.scalars().all()

    customer = None
    if order.customer_id:
        c_r = await db.execute(select(Customer).where(Customer.id == order.customer_id))
        customer = c_r.scalar_one_or_none()

    return {
        "order": {
            "id": order.id,
            "status": order.status,
            "total_amount": order.total_amount,
            "items": order.items or [],
            "created_at": order.created_at.isoformat() if order.created_at else None,
        },
        "customer": {"id": customer.id, "name": customer.name, "email": customer.email} if customer else None,
        "payments": [
            {
                "id": p.id,
                "status": p.status,
                "amount": p.amount,
                "method": p.method,
                "failure_reason": p.failure_reason,
                "is_webhook_delivered": p.is_webhook_delivered,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in payments
        ],
    }

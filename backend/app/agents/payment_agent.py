"""
Payment Investigation Agent — analyzes payment events, diagnoses failures,
and identifies inconsistent states. Uses deterministic rule-based logic
with confidence scoring. Falls back gracefully if ML models are absent.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.agents.policy_agent import evaluate_policy, PolicyResult


@dataclass
class PaymentDiagnosis:
    incident_type: str
    severity: str
    root_cause: str
    confidence_score: float
    evidence: List[str]
    recommended_action: str
    expected_recovery: float
    risk_level: str
    policy_result: str
    auto_executable: bool
    requires_approval: bool
    ai_explanation: str


def diagnose_payment(
    payment_status: str,
    failure_reason: str,
    amount: float,
    attempt_count: int = 1,
    webhook_delivered: bool = True,
    webhook_attempts: int = 0,
    has_duplicate: bool = False,
    minutes_since_failure: int = 0,
) -> PaymentDiagnosis:
    """
    Rule-based payment diagnosis engine.
    Produces a structured diagnosis used by the Recovery Agent.
    """
    evidence: List[str] = []
    
    # ── Duplicate payment ─────────────────────────────────────────────────────
    if has_duplicate:
        policy = evaluate_policy("duplicate_payment_resolution", amount)
        return PaymentDiagnosis(
            incident_type="duplicate_payment",
            severity="critical",
            root_cause="Two successful captures detected for same order within a short window.",
            confidence_score=0.89,
            evidence=[
                "Two CAPTURED payments found for same order",
                f"Amount ₹{amount:,.0f} charged twice",
                "Possible double-click or network retry issue",
            ],
            recommended_action="Hold second payment and initiate refund review",
            expected_recovery=amount,
            risk_level="high",
            policy_result=policy.verdict,
            auto_executable=False,
            requires_approval=True,
            ai_explanation=f"Duplicate payment detected. ₹{amount:,.0f} may have been charged twice. Requires human compliance review before any refund action.",
        )

    # ── Webhook failure (payment succeeded but delivery failed) ───────────────
    if payment_status == "captured" and not webhook_delivered:
        confidence = min(0.97, 0.90 + (webhook_attempts * 0.01))
        policy = evaluate_policy("replay_webhook_demo", amount)
        return PaymentDiagnosis(
            incident_type="webhook_failure",
            severity="high",
            root_cause="Payment captured successfully but webhook delivery failed. Order state not updated.",
            confidence_score=confidence,
            evidence=[
                f"Payment status: CAPTURED (confirmed)",
                f"Webhook delivery: FAILED ({webhook_attempts} attempts)",
                "Order remains in PROCESSING state",
                "Customer has not received confirmation",
            ],
            recommended_action="Replay webhook event to update order state",
            expected_recovery=amount,
            risk_level="low",
            policy_result=policy.verdict,
            auto_executable=policy.verdict == "ALLOW",
            requires_approval=policy.verdict != "ALLOW",
            ai_explanation="Payment confirmed captured. Webhook replay will update order and trigger confirmation. No financial risk — safe to auto-execute.",
        )

    # ── Failed payment diagnosis ───────────────────────────────────────────────
    if payment_status == "failed":
        severity = "high" if amount > 50_000 else "medium" if amount > 10_000 else "low"
        
        if failure_reason == "technical_error":
            confidence = 0.94
            root_cause = "Temporary payment gateway failure. No customer-side issue detected."
            action = "Retry payment via alternate method (Card / NetBanking)"
            risk = "low"
            explanation = f"All {attempt_count} attempt(s) failed with gateway errors. Alternate method retry is safe."
            policy = evaluate_policy("suggest_retry", amount)
            evidence = [
                f"{attempt_count} payment attempt(s) with TECH_FAILURE errors",
                "No successful capture recorded",
                "Gateway error pattern indicates temporary outage",
            ]
        elif failure_reason == "timeout":
            confidence = 0.91
            root_cause = "Payment request timed out. Session expired before authorization."
            action = "Re-initiate payment with fresh session"
            risk = "low"
            explanation = "Timeout during payment authorization. No charge occurred. Safe to retry."
            policy = evaluate_policy("suggest_retry", amount)
            evidence = [
                f"Payment timed out after {minutes_since_failure} minutes",
                "No authorization event recorded",
                f"Attempt count: {attempt_count}",
            ]
        elif failure_reason == "insufficient_funds":
            confidence = 0.89
            root_cause = "Insufficient balance in customer's account/card."
            action = "Offer EMI or part-payment options"
            risk = "low"
            explanation = "Customer's payment method lacks sufficient funds. EMI/part-payment may enable completion."
            policy = evaluate_policy("recommend_payment_method", amount)
            evidence = [
                "Bank returned INSUFFICIENT_FUNDS",
                f"Order amount ₹{amount:,.0f}",
                "EMI option may reduce barrier to completion",
            ]
        elif failure_reason == "bank_decline":
            if amount > 50_000:
                confidence = 0.86
                root_cause = "Bank declined high-value transaction due to risk rules."
                action = "Offer EMI with 0% interest or split payment"
                risk = "high"
                policy = evaluate_policy("high_value_intervention", amount)
            else:
                confidence = 0.84
                root_cause = "Bank declined transaction. May be temporary risk rule."
                action = "Suggest alternate bank or payment method"
                risk = "medium"
                policy = evaluate_policy("recommend_payment_method", amount)
            explanation = f"Bank decline on ₹{amount:,.0f}. Recovery probability improves with alternate payment method."
            evidence = [
                "Bank response: DECLINE",
                f"Transaction amount: ₹{amount:,.0f}",
                f"Attempts: {attempt_count}",
            ]
        elif failure_reason == "fraud_suspected":
            confidence = 0.78
            root_cause = "Transaction flagged by fraud detection system."
            action = "Route for manual compliance review"
            risk = "high"
            policy = evaluate_policy("fraud_flagged_action", amount)
            explanation = "Fraud flag requires manual review before any recovery action."
            evidence = [
                "Fraud detection flag raised",
                "Cannot auto-execute recovery",
                "Compliance team review required",
            ]
        elif failure_reason == "upi_failure":
            confidence = 0.88
            root_cause = "UPI VPA not responding or UPI service temporarily unavailable."
            action = "Switch to card or netbanking payment"
            risk = "low"
            policy = evaluate_policy("recommend_payment_method", amount)
            explanation = "UPI failure is typically transient. Alternate method will succeed."
            evidence = [
                "UPI VPA timeout detected",
                "No debit from customer account",
                "Card/NetBanking available as alternate",
            ]
        else:
            confidence = 0.75
            root_cause = f"Payment failed: {failure_reason}"
            action = "Recommend alternate payment method and contact support"
            risk = "medium"
            policy = evaluate_policy("recommend_payment_method", amount)
            explanation = "Payment failed with unclassified reason. Alternate method suggested."
            evidence = [f"Failure reason: {failure_reason}", f"Amount: ₹{amount:,.0f}"]

        if attempt_count >= 3:
            evidence.append(f"⚠️ {attempt_count} failed attempts — high urgency")
            confidence = min(confidence + 0.02, 0.99)

        return PaymentDiagnosis(
            incident_type="payment_failed",
            severity=severity,
            root_cause=root_cause,
            confidence_score=confidence,
            evidence=evidence,
            recommended_action=action,
            expected_recovery=amount,
            risk_level=risk,
            policy_result=policy.verdict,
            auto_executable=policy.verdict == "ALLOW",
            requires_approval=policy.verdict != "ALLOW",
            ai_explanation=explanation,
        )

    # ── Timeout ───────────────────────────────────────────────────────────────
    if payment_status == "timeout":
        policy = evaluate_policy("suggest_retry", amount)
        return PaymentDiagnosis(
            incident_type="payment_timeout",
            severity="medium",
            root_cause="Payment session expired before completion.",
            confidence_score=0.91,
            evidence=["Payment status: TIMEOUT", "No capture recorded", "Session expired"],
            recommended_action="Re-initiate payment with fresh session",
            expected_recovery=amount,
            risk_level="low",
            policy_result=policy.verdict,
            auto_executable=True,
            requires_approval=False,
            ai_explanation="Timeout with no charge. Safe to retry.",
        )

    # Default — authorized but not captured
    policy = evaluate_policy("suggest_retry", amount)
    return PaymentDiagnosis(
        incident_type="payment_incomplete",
        severity="low",
        root_cause="Payment authorized but not yet captured.",
        confidence_score=0.80,
        evidence=["Payment status: AUTHORIZED", "Awaiting capture"],
        recommended_action="Confirm capture or wait for completion",
        expected_recovery=amount,
        risk_level="low",
        policy_result=policy.verdict,
        auto_executable=True,
        requires_approval=False,
        ai_explanation="Payment in progress — no action required yet.",
    )


def score_cart_intent(
    cart_value: float,
    customer_tier: str,
    items_count: int,
    hours_since_abandonment: float,
    previous_orders: int,
) -> Dict[str, Any]:
    """Score purchase intent for an abandoned cart."""
    score = 0.5

    # Value signal
    if cart_value > 50_000: score += 0.15
    elif cart_value > 10_000: score += 0.10
    elif cart_value > 2_000: score += 0.05

    # Loyalty signal
    tier_boost = {"platinum": 0.20, "gold": 0.15, "silver": 0.08, "bronze": 0.02}
    score += tier_boost.get(customer_tier, 0.0)

    # Previous order signal
    if previous_orders > 10: score += 0.15
    elif previous_orders > 5: score += 0.10
    elif previous_orders > 1: score += 0.05

    # Recency — longer ago = lower intent
    if hours_since_abandonment < 1: score += 0.10
    elif hours_since_abandonment < 6: score += 0.05
    elif hours_since_abandonment > 24: score -= 0.10
    elif hours_since_abandonment > 48: score -= 0.20

    # Items signal
    if items_count >= 3: score += 0.05

    score = max(0.05, min(0.98, score))
    conversion_prob = round(score * 0.92, 2)

    interventions = [
        "Send personalized discount (10% off) with 6-hour expiry",
        "Trigger urgency: only 2 units left in stock",
        "Offer free express shipping for next 3 hours",
        "Show social proof notification",
        "Recommend complementary product bundle",
    ]

    expected_recovery = round(cart_value * conversion_prob)

    return {
        "intent_score": round(score, 2),
        "conversion_probability": conversion_prob,
        "recommended_intervention": interventions[int(score * 4) % len(interventions)],
        "expected_recovery": expected_recovery,
    }

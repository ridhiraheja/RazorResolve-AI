"""
Policy Agent — evaluates every proposed AI action before execution.
Returns ALLOW / REVIEW / BLOCK with reasoning.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PolicyResult:
    verdict: str  # ALLOW | REVIEW | BLOCK
    reason: str
    requires_human: bool


# Thresholds
HIGH_VALUE_THRESHOLD = 50_000  # INR — actions above this need review
CRITICAL_VALUE_THRESHOLD = 1_00_000  # INR — always block auto-execution

BLOCKED_ACTIONS = {
    "change_kyc",
    "release_blocked_funds",
    "modify_settlement",
    "unauthorized_transaction",
    "change_bank_account",
    "delete_payment_record",
}

REVIEW_REQUIRED_ACTIONS = {
    "large_refund",
    "duplicate_payment_resolution",
    "high_value_intervention",
    "multiple_recovery_attempts",
    "fraud_flagged_action",
}

ALWAYS_ALLOWED_ACTIONS = {
    "recommend_product",
    "suggest_upsell",
    "suggest_retry",
    "retry_simulated_payment",
    "send_recovery_message",
    "replay_webhook_demo",
    "recommend_payment_method",
    "calculate_intent_score",
    "create_incident",
    "update_incident_status",
    "generate_audit_log",
}


def evaluate_policy(action_type: str, amount: float = 0.0, metadata: Optional[Dict[str, Any]] = None) -> PolicyResult:
    """Evaluate whether the agent is allowed to perform an action."""
    metadata = metadata or {}
    action_lower = action_type.lower().replace(" ", "_")

    # Hard blocks — never execute automatically
    for blocked in BLOCKED_ACTIONS:
        if blocked in action_lower:
            return PolicyResult(
                verdict="BLOCK",
                reason=f"Action '{action_type}' is categorically prohibited. Not within AI agent permissions.",
                requires_human=True,
            )

    # Always allowed — no value check needed
    for allowed in ALWAYS_ALLOWED_ACTIONS:
        if allowed in action_lower:
            return PolicyResult(
                verdict="ALLOW",
                reason=f"Action '{action_type}' is within safe auto-execute permissions.",
                requires_human=False,
            )

    # Check for review-required actions
    for review_action in REVIEW_REQUIRED_ACTIONS:
        if review_action in action_lower:
            return PolicyResult(
                verdict="REVIEW",
                reason=f"Action '{action_type}' requires human approval before execution.",
                requires_human=True,
            )

    # Value-based thresholds
    if amount >= CRITICAL_VALUE_THRESHOLD:
        return PolicyResult(
            verdict="REVIEW",
            reason=f"Amount ₹{amount:,.0f} exceeds critical threshold (₹{CRITICAL_VALUE_THRESHOLD:,}). Human approval mandatory.",
            requires_human=True,
        )

    if amount >= HIGH_VALUE_THRESHOLD:
        return PolicyResult(
            verdict="REVIEW",
            reason=f"Amount ₹{amount:,.0f} exceeds high-value threshold (₹{HIGH_VALUE_THRESHOLD:,}). Review recommended.",
            requires_human=True,
        )

    # Default: allow with note
    return PolicyResult(
        verdict="ALLOW",
        reason=f"Action '{action_type}' passed all policy checks. Amount ₹{amount:,.0f} within safe limits.",
        requires_human=False,
    )

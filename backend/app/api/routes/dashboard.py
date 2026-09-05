from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.db.database import get_db
from app.models import (
    Payment, PaymentStatus, Order, OrderStatus, Customer,
    Incident, IncidentStatus, Cart, CartStatus, AuditLog
)
from typing import Optional
import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Return all key metrics for the overview dashboard."""

    # Total revenue (captured payments)
    rev_result = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.CAPTURED)
    )
    total_revenue = rev_result.scalar() or 0.0

    # Failed payments
    failed_result = await db.execute(
        select(func.count(Payment.id), func.sum(Payment.amount))
        .where(Payment.status == PaymentStatus.FAILED)
    )
    failed_row = failed_result.one()
    failed_count = failed_row[0] or 0
    revenue_at_risk = failed_row[1] or 0.0

    # Abandoned carts
    abandoned_result = await db.execute(
        select(func.count(Cart.id), func.sum(Cart.total_value))
        .where(Cart.status == CartStatus.ABANDONED)
    )
    ab_row = abandoned_result.one()
    abandoned_count = ab_row[0] or 0
    cart_value_at_risk = ab_row[1] or 0.0

    # Recovered carts
    recovered_result = await db.execute(
        select(func.count(Cart.id), func.sum(Cart.total_value))
        .where(Cart.status == CartStatus.RECOVERED)
    )
    rec_row = recovered_result.one()
    recovered_carts = rec_row[0] or 0
    recovered_cart_revenue = rec_row[1] or 0.0

    # Active incidents
    active_incidents_result = await db.execute(
        select(func.count(Incident.id))
        .where(Incident.status.not_in([IncidentStatus.RESOLVED]))
    )
    active_incidents = active_incidents_result.scalar() or 0

    # Resolved incidents (recovered revenue)
    resolved_result = await db.execute(
        select(func.sum(Incident.recovered_amount))
        .where(Incident.status == IncidentStatus.RESOLVED)
    )
    recovered_revenue = resolved_result.scalar() or 0.0

    # Total orders
    total_orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = total_orders_result.scalar() or 0

    # Completed orders
    completed_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.COMPLETED)
    )
    completed_orders = completed_orders_result.scalar() or 0

    conversion_rate = round((completed_orders / total_orders * 100), 1) if total_orders > 0 else 0.0

    # All payments for success rate
    total_payments_result = await db.execute(select(func.count(Payment.id)))
    total_payments = total_payments_result.scalar() or 0
    payment_success_rate = round(((total_payments - failed_count) / total_payments * 100), 1) if total_payments > 0 else 0.0

    # AI recovery success
    total_incidents_result = await db.execute(select(func.count(Incident.id)))
    total_incidents = total_incidents_result.scalar() or 0
    resolved_count_result = await db.execute(
        select(func.count(Incident.id)).where(Incident.status == IncidentStatus.RESOLVED)
    )
    resolved_count = resolved_count_result.scalar() or 0
    ai_recovery_rate = round((resolved_count / total_incidents * 100), 1) if total_incidents > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "conversion_rate": conversion_rate,
        "failed_payments": failed_count,
        "abandoned_checkouts": abandoned_count,
        "revenue_at_risk": round(revenue_at_risk + cart_value_at_risk, 2),
        "revenue_recovered": round(recovered_revenue + recovered_cart_revenue, 2),
        "ai_recovery_success_rate": ai_recovery_rate,
        "active_incidents": active_incidents,
        "total_orders": total_orders,
        "payment_success_rate": payment_success_rate,
        "total_incidents": total_incidents,
    }


@router.get("/revenue-trend")
async def get_revenue_trend(days: int = 30, db: AsyncSession = Depends(get_db)):
    """Return daily revenue for sparkline/chart."""
    since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    result = await db.execute(
        select(Payment)
        .where(Payment.status == PaymentStatus.CAPTURED, Payment.captured_at >= since)
        .order_by(Payment.captured_at)
    )
    payments = result.scalars().all()

    # Group by date
    daily: dict = {}
    for p in payments:
        d = p.captured_at.strftime("%Y-%m-%d") if p.captured_at else "unknown"
        daily[d] = daily.get(d, 0) + p.amount

    return {"trend": [{"date": k, "revenue": round(v, 2)} for k, v in sorted(daily.items())]}


@router.get("/failure-breakdown")
async def get_failure_breakdown(db: AsyncSession = Depends(get_db)):
    """Return payment failure reasons breakdown."""
    result = await db.execute(
        select(Payment.failure_reason, func.count(Payment.id), func.sum(Payment.amount))
        .where(Payment.status == PaymentStatus.FAILED)
        .group_by(Payment.failure_reason)
    )
    rows = result.all()
    return {
        "breakdown": [
            {"reason": str(r[0]).replace("_", " ").title(), "count": r[1], "amount": round(r[2] or 0, 2)}
            for r in rows if r[0] is not None
        ]
    }

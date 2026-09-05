from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models import Cart, CartStatus, Customer
from typing import Optional

router = APIRouter(prefix="/carts", tags=["carts"])


@router.get("")
async def list_carts(
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Cart).order_by(desc(Cart.abandoned_at))
    if status:
        try:
            q = q.where(Cart.status == CartStatus(status))
        except ValueError:
            pass
    q = q.limit(limit)
    result = await db.execute(q)
    carts = result.scalars().all()

    out = []
    for c in carts:
        customer_name = None
        if c.customer_id:
            c_r = await db.execute(select(Customer).where(Customer.id == c.customer_id))
            cust = c_r.scalar_one_or_none()
            customer_name = cust.name if cust else None

        hours_abandoned = None
        if c.abandoned_at:
            import datetime
            hours_abandoned = round((datetime.datetime.utcnow() - c.abandoned_at).total_seconds() / 3600, 1)

        out.append({
            "id": c.id,
            "customer_id": c.customer_id,
            "customer_name": customer_name,
            "status": c.status,
            "items": c.items or [],
            "total_value": c.total_value,
            "item_count": c.item_count,
            "intent_score": c.intent_score,
            "conversion_probability": c.conversion_probability,
            "recommended_intervention": c.recommended_intervention,
            "expected_recovery": c.expected_recovery,
            "hours_since_abandonment": hours_abandoned,
            "abandoned_at": c.abandoned_at.isoformat() if c.abandoned_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {"carts": out, "total": len(out)}

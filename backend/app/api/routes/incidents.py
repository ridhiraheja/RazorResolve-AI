from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models import Incident, IncidentStatus, IncidentSeverity, IncidentType, Customer, Order
from typing import Optional

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("")
async def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Incident).order_by(desc(Incident.created_at))
    if status:
        try:
            q = q.where(Incident.status == IncidentStatus(status))
        except ValueError:
            pass
    if severity:
        try:
            q = q.where(Incident.severity == IncidentSeverity(severity))
        except ValueError:
            pass
    q = q.offset(offset).limit(limit)
    result = await db.execute(q)
    incidents = result.scalars().all()

    enriched = []
    for inc in incidents:
        # fetch customer name
        customer_name = None
        if inc.customer_id:
            c_result = await db.execute(select(Customer).where(Customer.id == inc.customer_id))
            cust = c_result.scalar_one_or_none()
            customer_name = cust.name if cust else None
        enriched.append({
            "id": inc.id,
            "type": inc.type,
            "severity": inc.severity,
            "status": inc.status,
            "customer_id": inc.customer_id,
            "customer_name": customer_name,
            "order_id": inc.order_id,
            "payment_id": inc.payment_id,
            "amount_at_risk": inc.amount_at_risk,
            "root_cause": inc.root_cause,
            "confidence_score": inc.confidence_score,
            "recommended_action": inc.recommended_action,
            "expected_recovery": inc.expected_recovery,
            "risk_level": inc.risk_level,
            "policy_result": inc.policy_result,
            "auto_executable": inc.auto_executable,
            "requires_approval": inc.requires_approval,
            "ai_explanation": inc.ai_explanation,
            "evidence": inc.evidence,
            "recovered_amount": inc.recovered_amount,
            "created_at": inc.created_at.isoformat() if inc.created_at else None,
            "updated_at": inc.updated_at.isoformat() if inc.updated_at else None,
            "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
        })
    return {"incidents": enriched, "total": len(enriched)}


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    customer_name = None
    if inc.customer_id:
        c_result = await db.execute(select(Customer).where(Customer.id == inc.customer_id))
        cust = c_result.scalar_one_or_none()
        customer_name = cust.name if cust else None

    return {
        "id": inc.id,
        "type": inc.type,
        "severity": inc.severity,
        "status": inc.status,
        "customer_id": inc.customer_id,
        "customer_name": customer_name,
        "order_id": inc.order_id,
        "payment_id": inc.payment_id,
        "amount_at_risk": inc.amount_at_risk,
        "root_cause": inc.root_cause,
        "confidence_score": inc.confidence_score,
        "recommended_action": inc.recommended_action,
        "expected_recovery": inc.expected_recovery,
        "risk_level": inc.risk_level,
        "policy_result": inc.policy_result,
        "auto_executable": inc.auto_executable,
        "requires_approval": inc.requires_approval,
        "ai_explanation": inc.ai_explanation,
        "evidence": inc.evidence,
        "recovered_amount": inc.recovered_amount,
        "created_at": inc.created_at.isoformat() if inc.created_at else None,
    }


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    new_status = body.get("status")
    if new_status:
        try:
            inc.status = IncidentStatus(new_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    if body.get("recovered_amount") is not None:
        inc.recovered_amount = float(body["recovered_amount"])

    import datetime
    if new_status == "resolved":
        inc.resolved_at = datetime.datetime.utcnow()

    await db.commit()
    return {"id": inc.id, "status": inc.status, "message": "Incident updated"}


@router.post("/{incident_id}/approve")
async def approve_incident_action(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    import datetime
    inc.status = IncidentStatus.RECOVERING
    inc.requires_approval = False
    inc.auto_executable = True
    inc.policy_result = "ALLOW"
    inc.recovered_amount = inc.expected_recovery
    await db.commit()
    return {"id": inc.id, "status": "recovering", "message": "Action approved — recovery initiated (simulated)"}


@router.post("/{incident_id}/reject")
async def reject_incident_action(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    inc = result.scalar_one_or_none()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.status = IncidentStatus.ESCALATED
    await db.commit()
    return {"id": inc.id, "status": "escalated", "message": "Action rejected — incident escalated"}

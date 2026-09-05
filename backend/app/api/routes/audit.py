from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.database import get_db
from app.models import AuditLog, AIDecision

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
async def list_audit_logs(
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(AuditLog).order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit)
    result = await db.execute(q)
    logs = result.scalars().all()
    return {
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "agent": log.agent,
                "incident_id": log.incident_id,
                "observation": log.observation,
                "decision": log.decision,
                "action": log.action,
                "policy_result": log.policy_result,
                "result": log.result,
                "confidence": log.confidence,
            }
            for log in logs
        ],
        "total": len(logs),
    }


@router.get("/decisions")
async def list_ai_decisions(
    incident_id: str = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AIDecision).order_by(desc(AIDecision.created_at))
    if incident_id:
        q = q.where(AIDecision.incident_id == incident_id)
    q = q.limit(limit)
    result = await db.execute(q)
    decisions = result.scalars().all()
    return {
        "decisions": [
            {
                "id": d.id,
                "incident_id": d.incident_id,
                "agent_name": d.agent_name,
                "decision_type": d.decision_type,
                "observation": d.observation,
                "reasoning": d.reasoning,
                "decision": d.decision,
                "action_taken": d.action_taken,
                "policy_result": d.policy_result,
                "confidence_score": d.confidence_score,
                "expected_impact": d.expected_impact,
                "actual_result": d.actual_result,
                "evidence": d.evidence,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in decisions
        ],
        "total": len(decisions),
    }

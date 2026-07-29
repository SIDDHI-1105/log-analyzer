"""
backend/src/api/v1/alerts.py

Alert API endpoints: CRUD for alert rules and alert history.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.alert_rule import AlertRule
from models.alert_history import AlertHistory
from models.user import User
from schemas.alert import (
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    AlertHistoryResponse,
    AlertRuleWithHistoryResponse,
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ─────────────────────────────────────────────
# Alert Rule CRUD
# ─────────────────────────────────────────────

@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule_in: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Create a new alert rule for the current user.
    """
    rule = AlertRule(
        user_id=current_user.id,
        name=rule_in.name,
        severity=rule_in.severity,
        threshold=rule_in.threshold,
        time_window_seconds=rule_in.time_window_seconds,
        match_pattern=rule_in.match_pattern,
        notification_channels=json.dumps(rule_in.notification_channels),
        is_active=rule_in.is_active,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    # Convert notification_channels back to list for response
    rule.notification_channels = json.loads(rule.notification_channels)
    return rule


@router.get("/rules", response_model=list[AlertRuleResponse])
def list_alert_rules(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AlertRule]:
    """
    List alert rules for the current user.

    Optionally filter to active rules only.
    """
    query = db.query(AlertRule).filter(AlertRule.user_id == current_user.id)
    if active_only:
        query = query.filter(AlertRule.is_active.is_(True))
    rules = query.order_by(AlertRule.created_at.desc()).offset(skip).limit(limit).all()

    # Deserialize notification_channels for each rule
    for rule in rules:
        rule.notification_channels = json.loads(rule.notification_channels)
    return rules


@router.get("/rules/{rule_id}", response_model=AlertRuleWithHistoryResponse)
def get_alert_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Get a single alert rule by ID, including its trigger history.
    """
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id,
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    rule.notification_channels = json.loads(rule.notification_channels)
    return rule


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: str,
    rule_in: AlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertRule:
    """
    Update an existing alert rule (partial update).
    """
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id,
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    # Update only provided fields
    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "notification_channels" and value is not None:
            value = json.dumps(value)
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    rule.notification_channels = json.loads(rule.notification_channels)
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete an alert rule and its associated history.
    """
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id,
    ).first()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )

    db.delete(rule)
    db.commit()
    return None


# ─────────────────────────────────────────────
# Alert History
# ─────────────────────────────────────────────

@router.get("/history", response_model=list[AlertHistoryResponse])
def list_alert_history(
    skip: int = 0,
    limit: int = 50,
    rule_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AlertHistory]:
    """
    List alert history (triggered alerts) for the current user's rules.

    Optionally filter by a specific rule ID.
    """
    # Build subquery: only rules belonging to current user
    user_rule_ids = db.query(AlertRule.id).filter(AlertRule.user_id == current_user.id).subquery()

    query = db.query(AlertHistory).filter(AlertHistory.rule_id.in_(user_rule_ids))
    if rule_id:
        query = query.filter(AlertHistory.rule_id == rule_id)

    return query.order_by(AlertHistory.triggered_at.desc()).offset(skip).limit(limit).all()

"""
backend/src/services/alert_evaluator.py

Alert evaluation engine.

Checks incoming log entries against active alert rules and
creates AlertHistory records when thresholds are breached.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models.alert_history import AlertHistory
from models.alert_rule import AlertRule
from models.log_entry import LogEntry


def evaluate_logs_for_alerts(
    db: Session,
    logs: list[LogEntry],
    user_id: str,
) -> list[AlertHistory]:
    """
    Evaluate a batch of log entries against the user's active alert rules.

    For each active rule:
    1. Filter logs that match the rule's severity and optional pattern.
    2. Count matching logs within the rule's time window.
    3. If count >= threshold, create an AlertHistory record.

    Returns a list of newly created AlertHistory records.
    """
    triggered: list[AlertHistory] = []

    # Fetch all active alert rules for this user
    rules = (
        db.query(AlertRule)
        .filter(AlertRule.user_id == user_id, AlertRule.is_active.is_(True))
        .all()
    )

    if not rules:
        return triggered

    for rule in rules:
        # Deserialize notification channels
        channels = json.loads(rule.notification_channels) if rule.notification_channels else []

        # Determine time window
        window_start = datetime.now(timezone.utc) - timedelta(seconds=rule.time_window_seconds)

        # Build filter criteria
        matching_logs = [
            log for log in logs
            if log.level.upper() == rule.severity.upper()
            and (log.timestamp is None or log.timestamp >= window_start)
            and _matches_pattern(log.message, rule.match_pattern)
        ]

        match_count = len(matching_logs)

        if match_count >= rule.threshold:
            # Check if this rule already has an unresolved alert in the same window
            # to avoid duplicate spam
            existing_unresolved = (
                db.query(AlertHistory)
                .filter(
                    AlertHistory.rule_id == rule.id,
                    AlertHistory.resolved_at.is_(None),
                    AlertHistory.triggered_at >= window_start,
                )
                .first()
            )

            if not existing_unresolved:
                # Create alert history record
                alert = AlertHistory(
                    rule_id=rule.id,
                    severity=rule.severity,
                    details={
                        "matched_count": match_count,
                        "threshold": rule.threshold,
                        "time_window_seconds": rule.time_window_seconds,
                        "match_pattern": rule.match_pattern,
                        "sample_messages": [log.message[:200] for log in matching_logs[:3]],
                        "notification_channels": channels,
                    },
                )
                db.add(alert)
                triggered.append(alert)

    if triggered:
        db.commit()

    return triggered


def _matches_pattern(message: str, pattern: str | None) -> bool:
    """
    Check if a log message matches an optional regex pattern.

    If no pattern is set, all messages match.
    """
    if not pattern:
        return True

    try:
        return bool(re.search(pattern, message, re.IGNORECASE))
    except re.error:
        # If the pattern is an invalid regex, fall back to simple substring match
        return pattern.lower() in message.lower()

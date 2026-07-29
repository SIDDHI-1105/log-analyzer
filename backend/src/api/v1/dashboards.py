"""
backend/src/api/v1/dashboards.py

Dashboard API endpoints: CRUD for saved dashboards.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.database import get_db
from models.dashboard import Dashboard
from models.user import User
from schemas.dashboard import DashboardCreate, DashboardResponse, DashboardUpdate

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.post("/", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    dashboard_in: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dashboard:
    """
    Create a new dashboard for the current user.
    """
    dashboard = Dashboard(
        user_id=current_user.id,
        name=dashboard_in.name,
        widgets=dashboard_in.widgets,
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.get("/", response_model=list[DashboardResponse])
def list_dashboards(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Dashboard]:
    """
    List dashboards for the current user.
    """
    return (
        db.query(Dashboard)
        .filter(Dashboard.user_id == current_user.id)
        .order_by(Dashboard.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{dashboard_id}", response_model=DashboardResponse)
def get_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dashboard:
    """
    Get a single dashboard by ID.
    """
    dashboard = (
        db.query(Dashboard)
        .filter(Dashboard.id == dashboard_id, Dashboard.user_id == current_user.id)
        .first()
    )

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    return dashboard


@router.put("/{dashboard_id}", response_model=DashboardResponse)
def update_dashboard(
    dashboard_id: str,
    dashboard_in: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dashboard:
    """
    Update an existing dashboard (partial update).
    """
    dashboard = (
        db.query(Dashboard)
        .filter(Dashboard.id == dashboard_id, Dashboard.user_id == current_user.id)
        .first()
    )

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    update_data = dashboard_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dashboard, field, value)

    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a dashboard.
    """
    dashboard = (
        db.query(Dashboard)
        .filter(Dashboard.id == dashboard_id, Dashboard.user_id == current_user.id)
        .first()
    )

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    db.delete(dashboard)
    db.commit()
    return None

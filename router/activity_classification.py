from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from dependencies.database import get_db
from dependencies.auth import check_role
from ..services.activity_classification_service import ActivityClassificationService
from utils.api import Router

router = Router()

@router.get("/{activity_id}")
async def classify_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
) -> Dict:
    """
    Classify a specific activity using its description and available activity types.
    """
    service = ActivityClassificationService(db)
    try:
        return service.classify_activity(activity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def classify_all_activities(
    db: Session = Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
) -> List[Dict]:
    """
    Classify all activities in the system.
    """
    service = ActivityClassificationService(db)
    try:
        return service.classify_all_activities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
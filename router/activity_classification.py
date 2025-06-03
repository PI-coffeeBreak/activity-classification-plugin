from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
from dependencies.database import get_db
from dependencies.auth import check_role
from ..services.activity_classification_service import ActivityClassificationService
from utils.api import Router
import uuid
import threading

router = Router()

# In-memory store for background task status/results (use Redis for production)
classification_tasks = {}
classification_tasks_lock = threading.Lock()

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

# Background task function
def run_classification_task(task_id: str, db_session_maker):
    db = next(db_session_maker())
    service = ActivityClassificationService(db)
    try:
        result = service.classify_all_activities()
        with classification_tasks_lock:
            classification_tasks[task_id] = {"status": "done", "result": result}
    except Exception as e:
        with classification_tasks_lock:
            classification_tasks[task_id] = {"status": "error", "error": str(e)}
    finally:
        db.close()

@router.post("/trigger")
async def trigger_classify_all_activities(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    db_session_maker=Depends(get_db),
    _: dict = Depends(check_role(["manage_activities"]))
) -> Dict:
    """
    Trigger classification of all activities in the background. Returns a task_id.
    """
    task_id = str(uuid.uuid4())
    with classification_tasks_lock:
        classification_tasks[task_id] = {"status": "pending"}
    # Pass the session maker, not the session, to the background task
    background_tasks.add_task(run_classification_task, task_id, get_db)
    return {"task_id": task_id}

@router.get("/status/{task_id}")
async def get_classification_status(task_id: str) -> Dict:
    """
    Get the status and result of a classification task.
    """
    with classification_tasks_lock:
        task = classification_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

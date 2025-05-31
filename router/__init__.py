from utils.api import Router
from .activity_classification import router as activity_classification_router

router = Router()
router.include_router(activity_classification_router, "/activity-classifications")

__all__ = ["router"]
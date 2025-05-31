from sqlalchemy.orm import Session
from typing import List, Dict
from services.activity import ActivityService
from models.activity import Activity
from ..classifier import classifier

class ActivityClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.activity_service = ActivityService(db)

    def classify_activity(self, activity_id: int) -> Dict:
        """
        Classify an activity using its description and available activity types.
        Only classifies activities that don't have a type assigned yet.
        
        Args:
            activity_id: ID of the activity to classify
            
        Returns:
            dict: Classification results with labels and scores
        """
        # Get the activity
        activity = self.activity_service.get_by_id(activity_id)
        
        # Skip if activity already has a type
        if activity.type_id is not None:
            return {
                "message": "Activity already has a type assigned",
                "activity_id": activity.id,
                "activity_name": activity.name,
                "current_type_id": activity.type_id
            }
        
        # Get all activity types as candidate labels
        activity_types = self.activity_service.get_activity_types()
        candidate_labels = [activity_type.type for activity_type in activity_types]
        
        # Use the activity description for classification
        text = f"{activity.name}. {activity.description}"
        
        # Get classification results
        result = classifier.classify(text, candidate_labels)
        
        return {
            "activity_id": activity.id,
            "activity_name": activity.name,
            "classification": result
        }

    def classify_all_activities(self) -> List[Dict]:
        """
        Classify all activities in the system that don't have a type assigned yet.
        
        Returns:
            List[Dict]: List of classification results for each untyped activity
        """
        # Get only activities without a type
        untyped_activities = self.db.query(Activity).filter(Activity.type_id.is_(None)).all()
        results = []
        
        for activity in untyped_activities:
            result = self.classify_activity(activity.id)
            results.append(result)
            
        return results 
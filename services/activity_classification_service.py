from sqlalchemy.orm import Session
from typing import Dict
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
        Updates the activity's type in the database if classified.
        
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
        type_map = {activity_type.type: activity_type.id for activity_type in activity_types}
        
        # Use the activity description for classification
        text = f"{activity.name}. {activity.description}"
        
        # Get classification results
        result = classifier.classify(text, candidate_labels)
        
        # Pick the top label
        top_label = result["labels"][0] if "labels" in result and result["labels"] else None
        top_type_id = type_map[top_label] if top_label in type_map else None
        
        # Update the activity's type if a valid type was found
        if top_type_id is not None:
            from schemas.activity import ActivityUpdate
            update_data = ActivityUpdate(
                name=activity.name,
                description=activity.description,
                type_id=top_type_id
            )
            self.activity_service.update(activity.id, update_data)
        
        return {
            "activity_id": activity.id,
            "activity_name": activity.name,
            "classification": result,
            "assigned_type": top_label
        }

    def classify_all_activities(self) -> Dict[str, list]:
        """
        Classify all activities in the system that don't have a type assigned yet.
        Updates their types and returns a mapping of type names to lists of activities assigned to each type.
        
        Returns:
            Dict[str, list]: Mapping of type names to lists of activity info
        """
        # Get only activities without a type
        untyped_activities = self.db.query(Activity).filter(Activity.type_id.is_(None)).all()
        type_to_activities = {}
        
        for activity in untyped_activities:
            result = self.classify_activity(activity.id)
            assigned_type = result.get("assigned_type")
            if assigned_type:
                if assigned_type not in type_to_activities:
                    type_to_activities[assigned_type] = []
                type_to_activities[assigned_type].append({
                    "activity_id": result["activity_id"],
                    "activity_name": result["activity_name"]
                })
        
        return type_to_activities 
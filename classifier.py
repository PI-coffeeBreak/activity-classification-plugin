from transformers import pipeline
import logging

logger = logging.getLogger("coffeebreak.activity-classification")

class ActivityClassifier:
    def __init__(self):
        self.classifier = None
        
    def initialize(self):
        """Initialize the zero-shot classification model."""
        try:
            logger.info("Initializing activity classifier")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("Activity classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize activity classifier: {str(e)}")
            raise
            
    def classify(self, text, candidate_labels):
        """
        Classify the given text into one of the candidate labels.
        
        Args:
            text (str): The text to classify
            candidate_labels (list): List of possible activity labels
            
        Returns:
            dict: Classification results with scores
        """
        if not self.classifier:
            raise RuntimeError("Classifier not initialized. Call initialize() first.")
            
        return self.classifier(text, candidate_labels)
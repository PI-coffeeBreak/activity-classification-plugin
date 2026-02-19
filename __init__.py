from .router import router
from .classifier import classifier
import logging

logger = logging.getLogger("coffeebreak.activity-classification")


async def REGISTER():
    try:
        classifier.initialize()
        logger.debug("Activity classification plugin registered.")
    except Exception as e:
        logger.error(f"Failed to register activity classification plugin: {str(e)}")
        raise
    logger.debug("Activity classification plugin registered.")


async def UNREGISTER():
    logger.debug("Activity classification plugin unregistered.")

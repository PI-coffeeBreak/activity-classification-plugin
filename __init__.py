from .router import router
import logging

logger = logging.getLogger("coffeebreak.activity-classification")

NAME = "Activity Classification Plugin"
DESCRIPTION = "A plugin for classifying activities in a conference or event setting."

async def register_plugin():    
    # try:
    #     classifier.initialize()
    #     logger.debug("Activity classification plugin registered.")
    # except Exception as e:
    #     logger.error(f"Failed to register activity classification plugin: {str(e)}")
    #     raise
    logger.debug("Activity classification plugin registered.")

async def unregister_plugin():
    logger.debug("Activity classification plugin unregistered.")

REGISTER = register_plugin
UNREGISTER = unregister_plugin

CONFIG_PAGE = True

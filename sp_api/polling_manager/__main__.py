from loguru import logger

class PollingManager:
    def __init__(self, logging_configs=None):
        self.configure_logging(logging_configs)

    def configure_logging(self, configs):
        if configs is not None:
            # Remove all previously added handlers, including the default ones
            logger.remove()
            
            # Add custom log configurations from the provided list of dictionaries
            for config in configs:
                logger.add(**config)
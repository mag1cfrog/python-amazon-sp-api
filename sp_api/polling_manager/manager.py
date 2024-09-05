from loguru import logger
from sp_api.base import Marketplaces
from .orders import fetch_all_orders

class PollingManager:
    def __init__(self, credentials: dict, marketplace: Marketplaces=Marketplaces.US, logging_configs=None):
        self.configure_logging(logging_configs)
        self.credentials = credentials
        self.marketplace = marketplace
        self._orders = None

    def configure_logging(self, configs):
        if configs is not None:
            # Remove all previously added handlers, including the default ones
            logger.remove()
            
            # Add custom log configurations from the provided list of dictionaries
            for config in configs:
                logger.add(**config)

    @property
    def orders(self):
        if self._orders is None:
            self._orders = self.Orders(self)
        return self._orders
    
    class Orders:
        def __init__(self, manager):
            self.manager = manager

        def fetch_all_orders(self, **kwargs):
            # Utilize the manager's credentials and marketplace for fetching orders
            return fetch_all_orders(
                credentials=self.manager.credentials,
                marketplace=self.manager.marketplace,
                **kwargs
            )
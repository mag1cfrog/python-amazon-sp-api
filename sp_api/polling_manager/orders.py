from loguru import logger
from sp_api.util.backoff import exponential_backoff_with_jitter
from sp_api.base import Marketplaces
from sp_api.api import Orders

def refresh_client(credentials: dict, marketplace: Marketplaces) -> Orders:
    # Logic to refresh or create a new client
    return Orders(credentials=credentials, marketplace=marketplace)


def fetch_all_orders(credentials: dict, marketplace: Marketplaces=Marketplaces.US, base_sleep_time: float=5, max_attempts: int=5, backoff_base: float=4, max_client_refreshes: int=3, **kwargs):
    all_orders = []
    next_token = None
    attempt = 1
    should_continue = True
    orders_client = Orders(credentials=credentials, marketplace=marketplace)
    client_refresh = 0

    while should_continue: 
        try:
            response = orders_client.get_orders(
                NextToken=next_token,
                **kwargs
            )
            all_orders.extend(response.payload['Orders'])

            # Handle pagination
            next_token = response.next_token 
            if not next_token:
                break 
        
        # Handle exceptions
        except Exception as e:

            # Handle rate limiting
            if orders_client.res.status_code == 429:  
                if attempt < max_attempts:
                    exponential_backoff_with_jitter(base_sleep_time, attempt, backoff_base)
                    attempt += 1
                    continue
                else:
                    logger.error("API request rate exceeded after several retries")
                    should_continue = False
            
            # Handle client expiration
            if orders_client.res.status_code == 403 and "expired" in str(e).lower():
                    if client_refresh < max_client_refreshes:
                        logger.info("Refreshing client...")
                        orders_client = refresh_client(credentials, marketplace)
                        client_refresh += 1
                        logger.info("Client refreshed, retrying...")
                        continue
                    else:
                        logger.info("Client refresh limit exceeded")
                        should_continue = False
                        logger.error("Client refresh limit exceeded, stopping polling...")

            else:
                # If unexpected error occurs, raise it immediately
                raise Exception("An error occurred:", e)


    return all_orders

from sp_api.util.handle_api_error import handle_api_error
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

            # Handle API errors
            should_continue, client_refresh, orders_client = handle_api_error(
                e=e,
                api_client=orders_client,
                attempt=attempt,
                max_attempts=max_attempts,
                base_sleep_time=base_sleep_time,
                backoff_base=backoff_base,
                client_refresh=client_refresh,
                max_client_refreshes=max_client_refreshes,
                credentials=credentials,
                marketplace=marketplace,
                refresh_client=refresh_client
            )


    return all_orders
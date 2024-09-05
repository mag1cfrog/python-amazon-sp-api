from typing import Callable
from loguru import logger
from sp_api.util.handle_api_error import handle_api_error
from sp_api.base import Marketplaces, ApiResponse
from sp_api.api import Orders

def refresh_client(credentials: dict, marketplace: Marketplaces) -> Orders:
    # Logic to refresh or create a new client
    return Orders(credentials=credentials, marketplace=marketplace)


def fetch_all_orders(
        credentials: dict, 
        marketplace: Marketplaces=Marketplaces.US, 
        base_sleep_time: float=5, 
        max_attempts: int=5, 
        backoff_base: float=4, 
        max_client_refreshes: int=3, 
        **kwargs
    ) -> list:
    """
    Fetch all orders from the API.

    Args:

        credentials (dict): The credentials to use for the API client.
        marketplace (Marketplaces): The marketplace to fetch orders from. Default is US.
        base_sleep_time (float): The base sleep time in seconds. Default is 5.
        max_attempts (int): The maximum number of attempts. Default is 5.
        backoff_base (float): The base for exponential backoff. Default is 4.
        max_client_refreshes (int): The maximum number of times the client can be refreshed. Default is 3.
        **kwargs: Additional keyword arguments to pass to the API client.

    Returns:
        list: A list of orders.

    Raises:
        Exception: An unexpected error occurred.

    Examples:
        fetch_all_orders(
            credentials=credentials,
            marketplace=Marketplaces.US,
            base_sleep_time=5,
            max_attempts=5,
            backoff_base=4,
            max_client_refreshes=3
        )


    """
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


def fetch_all_order_attributes(
        orders: list, 
        credentials: dict, 
        fetch_attribute_func: Callable,
        refresh_client: Callable,
        marketplace: Marketplaces=Marketplaces.US, 
        max_attempts: int=5,
        max_client_refreshes: int=3,
        base_sleep_time: float=5
    )-> list:
    """
    Fetch all order attributes from the API based on a given list of AmazonOrderIds.

    Args:
    
        orders (list): A list of AmazonOrderIds.
        credentials (dict): The credentials to use for the API client.
        fetch_attribute_func (Callable): The function to fetch order attributes.
        refresh_client (Callable): The function to refresh the client.
        marketplace (Marketplaces): The marketplace to fetch orders from.
        max_attempts (int): The maximum number of attempts. Default is 5.
        max_client_refreshes (int): The maximum number of times the client can be refreshed. Default is 3.
        base_sleep_time (float): The base sleep time in seconds. Default is 5.

    Returns:
        list: A list of order attributes.

    Raises:
        Exception: An unexpected error occurred.

    Examples:

        fetch_all_order_attributes(
            orders=orders,
            credentials=credentials,
            fetch_attribute_func=fetch_one_order_address,
            refresh_client=refresh_client,
            marketplace=Marketplaces.US,
            max_attempts=5,
            max_client_refreshes=3,
            base_sleep_time=5

        )

    """
    all_order_attributes = []
    orders_client = Orders(credentials=credentials, marketplace=marketplace)
    should_continue = True  # Flag to control the outer loop
    
    total_orders = len(orders)
    order_count = 0
    for order in orders:
        next_token = None
        
        attempt = 1
        
        client_refresh = 0

        while should_continue:
            try:
                response = fetch_attribute_func(order['AmazonOrderId'], orders_client, next_token)
                print("Fetching order attribute for order:", order['AmazonOrderId'])
                order_count += 1
                all_order_attributes.append(response.payload)
                next_token = response.next_token

                if not next_token:
                    break  # Exit loop if no more data to fetch
            except Exception as e:
                should_continue, client_refresh, orders_client = handle_api_error(
                    e=e,
                    api_client=orders_client,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    base_sleep_time=base_sleep_time,
                    backoff_base=4,
                    client_refresh=client_refresh,
                    max_client_refreshes=max_client_refreshes,
                    credentials=credentials,
                    marketplace=marketplace,
                    refresh_client=refresh_client
                )

        if not should_continue:
            logger.error("Failed to fetch order attributes for order: {order_id}", order_id=order['AmazonOrderId'])
            logger.error(f"{total_orders - order_count} orders left to fetch, {order_count/ total_orders}% finished ")
            break  # Exit the outer loop if the flag is set to false
        
    print(f"Order fetching completed, total orders fetched: {order_count}")
        
    return all_order_attributes


def fetch_one_order_address(order_id: str, order_client: Orders, next_token: str) -> ApiResponse:
    """
    Fetch one order address from the API.
    """
    return order_client.get_order_address(
        order_id=order_id,
        NextToken=next_token
    )


def fetch_one_order_items(order_id: str, order_client: Orders, next_token: str) -> ApiResponse:
    """
    Fetch one order items from the API.
    """
    return order_client.get_order_items(
        order_id=order_id,
        NextToken=next_token
    )


def fetch_all_order_items(orders:list, credentials: dict, marketplace: Marketplaces=Marketplaces.US, **kwargs) -> list:
    """
    Fetch all order items from the API based on a given list of AmazonOrderIds.

    Args:

        orders (list): A list of dictionary that contains AmazonOrderIds.
        credentials (dict): The credentials to use for the API client.
        marketplace (Marketplaces): The marketplace to fetch orders from.
        **kwargs: Additional keyword arguments to pass to the API client.

    Returns:
        list: A list of order items.

    Raises:
        Exception: An unexpected error occurred.

    Examples:

        fetch_all_order_items(
            orders=orders,
            credentials=credentials,
            marketplace=Marketplaces.US
        )

    """
    return fetch_all_order_attributes(
        orders=orders,
        credentials=credentials,
        fetch_attribute_func=fetch_one_order_items,
        refresh_client=refresh_client,
        marketplace=marketplace,
        **kwargs
    )


def fetch_all_order_addresses(orders:dict, credentials: dict, marketplace: Marketplaces=Marketplaces.US, **kwargs) -> list:
    """
    Fetch all order addresses from the API based on a given list of AmazonOrderIds.

    Args:
    
            orders (list): A list of dictionary that contains AmazonOrderIds.
            credentials (dict): The credentials to use for the API client.
            marketplace (Marketplaces): The marketplace to fetch orders from.
            **kwargs: Additional keyword arguments to pass to the API client.

    Returns:
        list: A list of order addresses.

    Raises:
        Exception: An unexpected error occurred.
    
    Examples:
    
            fetch_all_order_addresses(
                orders=orders,
                credentials=credentials,
                marketplace=Marketplaces.US
            )
    
        """    
    
    return fetch_all_order_attributes(
        orders=orders,
        credentials=credentials,
        fetch_attribute_func=fetch_one_order_address,
        refresh_client=refresh_client,
        marketplace=marketplace,
        **kwargs
    )


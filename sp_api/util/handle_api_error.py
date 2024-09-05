from typing import Callable, Tuple
from loguru import logger
from sp_api.base import Marketplaces, Client
from sp_api.util.backoff import exponential_backoff_with_jitter


def handle_api_error(
        e: Exception, 
        api_client: Client, 
        attempt: int, 
        max_attempts: int, 
        base_sleep_time: float, 
        backoff_base: float, 
        client_refresh: int, 
        max_client_refreshes: int, 
        credentials: dict, 
        marketplace: Marketplaces, 
        refresh_client: Callable
    ) -> Tuple[bool, int, Client]:
    """
    Handle API errors and exceptions.

    Args:
        e (Exception): The exception that was raised.
        api_client (Client): The client instance that raised the exception.
        attempt (int): The current attempt number.
        max_attempts (int): The maximum number of attempts.
        base_sleep_time (float): The base sleep time in seconds.
        backoff_base (float): The base for exponential backoff.
        client_refresh (int): The number of times the client has been refreshed.
        max_client_refreshes (int): The maximum number of times the client can be refreshed.
        credentials (dict): The credentials used to create the client.
        marketplace (Marketplaces): The marketplace of the client.
        refresh_client (Callable): The function to refresh the client.

    Returns:
        Tuple[bool, int, Client]: A tuple containing a boolean indicating whether to continue polling, the number of client refreshes, and the client instance.
    
    Raises:
        Exception: An unexpected error occurred.
        
    Examples:
        handle_api_error(
            e=Exception("An error occurred"),
            api_client=client,
            attempt=1,
            max_attempts=5,
            base_sleep_time=5,
            backoff_base=4,
            client_refresh=0,
            max_client_refreshes=3,
            credentials=credentials,
            marketplace=Marketplaces.US,
            refresh_client=refresh_client
        )
    """
    
    if api_client.res.status_code == 429:  # Rate limiting
        if attempt < max_attempts:
            exponential_backoff_with_jitter(base_sleep_time, attempt, backoff_base)
            return True, client_refresh, api_client
        else:
            logger.error("API request rate exceeded after several retries")
            return False, client_refresh, api_client

    if api_client.res.status_code == 403 and "expired" in str(e).lower():  # Client expiration
        if client_refresh < max_client_refreshes:
            logger.info("Refreshing client...")
            api_client = refresh_client(credentials, marketplace)
            client_refresh += 1
            logger.info("Client refreshed, retrying...")
            return True, client_refresh, api_client
        else:
            logger.info("Client refresh limit exceeded")
            logger.error("Client refresh limit exceeded, stopping polling...")
            return False, client_refresh, api_client

    # If an unexpected error occurs, raise it immediately
    raise Exception(f"An unexpected error occurred: {e}")

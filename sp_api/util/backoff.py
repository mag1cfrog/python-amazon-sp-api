


def exponential_backoff_with_jitter(base_sleep_time: float, attempt: int, backoff_base: int = 4):
    """
    Exponential backoff with jitter.
    Args:
        base_sleep_time (float): Base sleep time in seconds.
        attempt (int): Attempt number.
        backoff_base (int): Base for exponential backoff. Default is 4.

    Returns:
        None
    
    Raises:
        None
    
    Examples:
        exponential_backoff_with_jitter(5, 1)  # Sleep for 5 - 5.5 seconds
    
    """
    import random
    import time

    sleep_time = base_sleep_time * (backoff_base ** attempt)  # Exponential backoff
    jitter = random.uniform(0, sleep_time * 0.1)
    time.sleep(sleep_time + jitter)
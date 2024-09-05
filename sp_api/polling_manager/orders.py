from sp_api.util.backoff import exponential_backoff_with_jitter


def fetch_all_orders(orders_client, base_sleep_time: float=5, max_attempts: int=5, backoff_base: float=4, **kwargs):
    all_orders = []
    next_token = None
    attempt = 1
    
    while True: # Handle pagination
        try:
            response = orders_client.get_orders(
                NextToken=next_token,
                **kwargs
            )
            all_orders.extend(response.payload['Orders'])
            next_token = response.next_token

            if not next_token:
                break  # Exit loop if no more data to fetch
        except Exception as e:
            if orders_client.res.status_code == 429:  # Check if rate limit exceeded
                if attempt < max_attempts:
                    exponential_backoff_with_jitter(base_sleep_time, attempt, backoff_base)
                    attempt += 1
                    continue
                else:
                    raise Exception("API request rate exceeded after several retries")
            else:
                print("An error occurred:", e)
                break  # Break on other types of exceptions


    return all_orders
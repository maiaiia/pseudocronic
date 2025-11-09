from fastapi import Request, HTTPException
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict

# In-memory storage (resets when server restarts)
rate_limit_store = defaultdict(lambda: {"count": 0, "reset_time": None})


def rate_limit(max_calls: int, window_hours: int = 1):
    """
    Rate limiter decorator that tracks requests by IP address.
    Uses in-memory storage (resets on server restart).
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            key = f"rate_limit:{func.__name__}:{client_ip}"
            now = datetime.now()

            # Check if we need to reset the counter
            if (rate_limit_store[key]["reset_time"] is None or
                    now > rate_limit_store[key]["reset_time"]):
                rate_limit_store[key] = {
                    "count": 1,
                    "reset_time": now + timedelta(hours=window_hours)
                }
                remaining = max_calls - 1
            elif rate_limit_store[key]["count"] >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {max_calls} requests per hour. Try again later."
                )
            else:
                rate_limit_store[key]["count"] += 1
                remaining = max_calls - rate_limit_store[key]["count"]

            # Execute the actual route handler
            response = await func(request, *args, **kwargs)

            # Handle different response types
            if isinstance(response, dict):
                # Already a dict - just add remaining_calls
                response["remaining_calls"] = remaining
                return response
            elif hasattr(response, 'dict'):
                # It's a Pydantic model - convert to dict and add remaining_calls
                response_dict = response.dict()
                response_dict["remaining_calls"] = remaining
                return response_dict
            elif hasattr(response, '__dict__'):
                # Has __dict__ - convert and add remaining_calls
                response_dict = response.__dict__.copy()
                response_dict["remaining_calls"] = remaining
                return response_dict
            else:
                # Can't add remaining_calls, return as-is
                return response

        return wrapper

    return decorator
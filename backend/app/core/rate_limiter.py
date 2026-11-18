
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


_requests = defaultdict(deque)


def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
):
    async def dependency(request: Request):
        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        key = f"{client_ip}:{request.url.path}"
        now = time.monotonic()

        request_times = _requests[key]

        while (
            request_times
            and now - request_times[0] > window_seconds
        ):
            request_times.popleft()

        if len(request_times) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        request_times.append(now)

    return dependency

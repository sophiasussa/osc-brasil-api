from collections.abc import Callable
from time import monotonic

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from core.security.rate_limiter import SlidingWindowRateLimiter


RATE_LIMIT_DETAIL = "Rate limit exceeded. Please try again later."
MISSING_CLIENT_KEY = "<missing-client-ip>"


class RateLimitMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        max_requests: int,
        window_seconds: float,
        enabled: bool,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.app = app
        self.enabled = enabled
        self.limiter = SlidingWindowRateLimiter(
            max_requests=max_requests,
            window_seconds=window_seconds,
            clock=clock,
        )

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if not self.enabled or scope.get("path") == "/health":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = (
            client[0]
            if client is not None and client[0]
            else MISSING_CLIENT_KEY
        )
        retry_after = self.limiter.check_request(client_ip)
        if retry_after is not None:
            response = JSONResponse(
                status_code=429,
                content={"detail": RATE_LIMIT_DETAIL},
                headers={"Retry-After": str(retry_after)},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

from collections import deque
from collections.abc import Callable
from math import ceil, isfinite
from threading import Lock
from time import monotonic


class SlidingWindowRateLimiter:
    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: float,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if not isfinite(window_seconds) or window_seconds <= 0:
            raise ValueError("window_seconds must be a positive finite number")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._cleanup_interval = min(window_seconds, 60.0)
        self._next_cleanup = clock() + self._cleanup_interval
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check_request(self, client_ip: str) -> int | None:
        """Register an allowed request or return its retry delay in seconds."""
        with self._lock:
            now = self._clock()
            cutoff = now - self.window_seconds
            if now >= self._next_cleanup:
                self._remove_expired_clients(cutoff)
                now = self._clock()
                cutoff = now - self.window_seconds
                self._next_cleanup = now + self._cleanup_interval

            timestamps = self._requests.get(client_ip)
            if timestamps is not None:
                self._remove_expired_requests(timestamps, cutoff)
                if not timestamps:
                    del self._requests[client_ip]
                    timestamps = None

            if timestamps is not None and len(timestamps) >= self.max_requests:
                expiration = timestamps[0] + self.window_seconds
                return max(1, ceil(expiration - now))

            if timestamps is None:
                timestamps = deque()
                self._requests[client_ip] = timestamps
            timestamps.append(now)
            return None

    def _remove_expired_clients(self, cutoff: float) -> None:
        for client_ip, timestamps in list(self._requests.items()):
            self._remove_expired_requests(timestamps, cutoff)
            if not timestamps:
                del self._requests[client_ip]

    @staticmethod
    def _remove_expired_requests(
        timestamps: deque[float],
        cutoff: float,
    ) -> None:
        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()
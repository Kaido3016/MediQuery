"""Rate limiting with a shared Redis backend in production.

Development may use a bounded per-process fallback. Production must configure
Redis so replicas share limits; backend failures fail closed rather than silently
disabling protection.
"""

from collections import OrderedDict, deque
from threading import Lock
from time import monotonic
from uuid import uuid4

from redis.asyncio import Redis


_REDIS_SLIDING_WINDOW = """
local key = KEYS[1]
local now_parts = redis.call('TIME')
local now = (tonumber(now_parts[1]) * 1000) + math.floor(tonumber(now_parts[2]) / 1000)
local window_ms = tonumber(ARGV[1])
local limit = tonumber(ARGV[2])
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window_ms)
local count = redis.call('ZCARD', key)
if count >= limit then
  redis.call('PEXPIRE', key, window_ms)
  return 0
end
redis.call('ZADD', key, now, tostring(now) .. ':' .. ARGV[3])
redis.call('PEXPIRE', key, window_ms)
return 1
"""


class RateLimitBackendUnavailable(RuntimeError):
    """Raised when the configured production rate-limit backend cannot be used."""


class FixedWindowRateLimiter:
    """Atomic Redis sliding window, with a bounded local fallback for development."""

    def __init__(self, max_local_keys: int = 10_000) -> None:
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()
        self._max_local_keys = max_local_keys
        self._calls = 0
        self._redis_clients: dict[str, Redis] = {}

    async def allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        *,
        redis_url: str | None = None,
        fail_closed: bool = False,
    ) -> bool:
        if limit < 1 or window_seconds < 1:
            raise ValueError("limit and window_seconds must be positive")

        if redis_url:
            try:
                client = self._redis_clients.get(redis_url)
                if client is None:
                    client = Redis.from_url(
                        redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                        socket_connect_timeout=1,
                        socket_timeout=1,
                        health_check_interval=30,
                    )
                    self._redis_clients[redis_url] = client
                result = await client.eval(
                    _REDIS_SLIDING_WINDOW,
                    1,
                    f"mediquery:ratelimit:{key}",
                    window_seconds * 1000,
                    limit,
                    uuid4().hex,
                )
                return bool(result)
            except Exception as exc:
                if fail_closed:
                    raise RateLimitBackendUnavailable(
                        "The shared rate-limit service is unavailable"
                    ) from exc

        if fail_closed:
            raise RateLimitBackendUnavailable(
                "A shared Redis rate-limit URL is required in production"
            )
        return self._local_allowed(key, limit, window_seconds)

    def _local_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            self._calls += 1
            history = self._hits.get(key)
            if history is None:
                history = deque()
                self._hits[key] = history
            else:
                self._hits.move_to_end(key)

            while history and history[0] <= cutoff:
                history.popleft()

            # Periodically reclaim expired client keys and bound memory even when
            # an attacker sends requests from many distinct source addresses.
            if self._calls % 64 == 0:
                for stale_key in list(self._hits):
                    stale_history = self._hits[stale_key]
                    while stale_history and stale_history[0] <= cutoff:
                        stale_history.popleft()
                    if not stale_history:
                        self._hits.pop(stale_key, None)

            if not history:
                self._hits.pop(key, None)
                history = deque()
                self._hits[key] = history
            if len(history) >= limit:
                return False
            history.append(now)
            self._hits.move_to_end(key)
            while len(self._hits) > self._max_local_keys:
                self._hits.popitem(last=False)
            return True


rate_limiter = FixedWindowRateLimiter()

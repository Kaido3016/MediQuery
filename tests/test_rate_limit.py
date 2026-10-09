import asyncio

import pytest

from src.core.rate_limit import FixedWindowRateLimiter, RateLimitBackendUnavailable
from src.core.settings import Settings


def test_local_limiter_enforces_window(monkeypatch):
    clock = {"now": 100.0}
    monkeypatch.setattr("src.core.rate_limit.monotonic", lambda: clock["now"])
    limiter = FixedWindowRateLimiter()

    assert asyncio.run(limiter.allowed("client", 2, 60))
    assert asyncio.run(limiter.allowed("client", 2, 60))
    assert not asyncio.run(limiter.allowed("client", 2, 60))

    clock["now"] = 161.0
    assert asyncio.run(limiter.allowed("client", 2, 60))


def test_local_limiter_bounds_distinct_client_memory():
    limiter = FixedWindowRateLimiter(max_local_keys=2)
    for key in ("one", "two", "three", "four"):
        assert asyncio.run(limiter.allowed(key, 10, 60))
    assert len(limiter._hits) <= 2


def test_production_limiter_fails_closed_without_shared_backend():
    limiter = FixedWindowRateLimiter()
    with pytest.raises(RateLimitBackendUnavailable):
        asyncio.run(
            limiter.allowed(
                "client",
                10,
                60,
                redis_url=None,
                fail_closed=True,
            )
        )


def test_production_settings_require_shared_rate_limit_backend():
    settings = Settings(
        environment="production",
        database_url="postgresql://user:pass@db:5432/mediquery",
        jwt_secret="x" * 48,
        cors_origins=["https://app.example.test"],
        rate_limit_redis_url=None,
    )
    with pytest.raises(RuntimeError, match="RATE_LIMIT_REDIS_URL"):
        settings.validate_for_runtime()


def test_production_limiter_fails_closed_when_redis_is_unavailable(monkeypatch):
    class BrokenRedis:
        async def eval(self, *args, **kwargs):
            raise OSError("backend unavailable")

    monkeypatch.setattr(
        "src.core.rate_limit.Redis.from_url",
        lambda *args, **kwargs: BrokenRedis(),
    )
    limiter = FixedWindowRateLimiter()
    with pytest.raises(RateLimitBackendUnavailable):
        asyncio.run(
            limiter.allowed(
                "client",
                10,
                60,
                redis_url="redis://private-redis.example.test:6379/0",
                fail_closed=True,
            )
        )

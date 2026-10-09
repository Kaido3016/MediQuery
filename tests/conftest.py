"""Shared test fixtures that keep request-rate state isolated between tests."""

import pytest

from src.core.rate_limit import rate_limiter


@pytest.fixture(autouse=True)
def reset_process_local_rate_limit_state():
    """Prevent unrelated TestClient cases from consuming one another's rate budget."""
    rate_limiter.reset_local_state()
    yield
    rate_limiter.reset_local_state()

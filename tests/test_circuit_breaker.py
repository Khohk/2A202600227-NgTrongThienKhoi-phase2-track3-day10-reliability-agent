import time

import pytest

from reliability_lab.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from reliability_lab.gateway import ReliabilityGateway
from reliability_lab.providers import FakeLLMProvider, ProviderError


def test_circuit_breaker_reopens_after_half_open_failure() -> None:
    breaker = CircuitBreaker("primary", failure_threshold=1, reset_timeout_seconds=0.01)

    def fail() -> None:
        raise ProviderError("boom")

    try:
        breaker.call(fail)
    except ProviderError:
        pass

    assert breaker.state == CircuitState.OPEN
    assert breaker.allow_request() is False

    time.sleep(0.02)
    assert breaker.allow_request() is True
    assert breaker.state == CircuitState.HALF_OPEN

    try:
        breaker.call(fail)
    except ProviderError:
        pass

    assert breaker.state == CircuitState.OPEN
    assert breaker.transition_log[-1]["reason"] == "probe_failure"


def test_gateway_uses_fallback_when_primary_circuit_is_open() -> None:
    primary = FakeLLMProvider("primary", fail_rate=1.0, base_latency_ms=1, cost_per_1k_tokens=0.001)
    backup = FakeLLMProvider("backup", fail_rate=0.0, base_latency_ms=1, cost_per_1k_tokens=0.001)
    primary_breaker = CircuitBreaker("primary", failure_threshold=1, reset_timeout_seconds=1)
    backup_breaker = CircuitBreaker("backup", failure_threshold=1, reset_timeout_seconds=1)
    gateway = ReliabilityGateway(
        [primary, backup],
        {"primary": primary_breaker, "backup": backup_breaker},
    )

    first_result = gateway.complete("hello world")
    second_result = gateway.complete("hello world")

    assert first_result.route.startswith("fallback:")
    assert second_result.route.startswith("fallback:")
    assert primary_breaker.state == CircuitState.OPEN

    with pytest.raises(CircuitOpenError):
        primary_breaker.call(lambda: None)

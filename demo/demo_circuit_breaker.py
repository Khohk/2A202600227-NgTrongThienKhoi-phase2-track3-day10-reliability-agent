from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.circuit_breaker import CircuitBreaker, CircuitState
from reliability_lab.providers import ProviderError


def always_fail() -> None:
    raise ProviderError("simulated provider failure")


def always_succeed() -> str:
    return "ok"


def main() -> None:
    breaker = CircuitBreaker(
        name="demo-primary",
        failure_threshold=2,
        reset_timeout_seconds=0.2,
        success_threshold=1,
    )
    print(f"start state: {breaker.state.value}")

    for attempt in range(1, 3):
        try:
            breaker.call(always_fail)
        except ProviderError as exc:
            print(f"attempt {attempt}: failure -> {exc} | state={breaker.state.value}")

    print(f"allow while open? {breaker.allow_request()}")
    time.sleep(0.25)
    print(f"after timeout state: {breaker.state.value} -> allow={breaker.allow_request()}")
    print(f"state after probe gate: {breaker.state.value}")

    result = breaker.call(always_succeed)
    print(f"probe result: {result} | final state={breaker.state.value}")
    print("transition log:")
    for entry in breaker.transition_log:
        print(entry)

    assert breaker.state == CircuitState.CLOSED


if __name__ == "__main__":
    main()

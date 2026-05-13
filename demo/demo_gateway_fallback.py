from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.cache import ResponseCache
from reliability_lab.circuit_breaker import CircuitBreaker
from reliability_lab.gateway import ReliabilityGateway
from reliability_lab.providers import FakeLLMProvider


def main() -> None:
    primary = FakeLLMProvider("primary", fail_rate=1.0, base_latency_ms=1, cost_per_1k_tokens=0.01)
    backup = FakeLLMProvider("backup", fail_rate=0.0, base_latency_ms=1, cost_per_1k_tokens=0.006)
    breakers = {
        "primary": CircuitBreaker("primary", failure_threshold=1, reset_timeout_seconds=1),
        "backup": CircuitBreaker("backup", failure_threshold=1, reset_timeout_seconds=1),
    }
    gateway = ReliabilityGateway([primary, backup], breakers, ResponseCache(60, 0.5))

    first = gateway.complete("Explain fallback routing.")
    second = gateway.complete("Explain fallback routing.")

    print("first response:", first.route, first.provider, f"cache_hit={first.cache_hit}")
    print("second response:", second.route, second.provider, f"cache_hit={second.cache_hit}")
    print("primary transitions:", breakers["primary"].transition_log)


if __name__ == "__main__":
    main()

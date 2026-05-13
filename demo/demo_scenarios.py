from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.cache import ResponseCache
from reliability_lab.circuit_breaker import CircuitBreaker
from reliability_lab.gateway import ReliabilityGateway
from reliability_lab.providers import FakeLLMProvider


def build_gateway(
    *,
    cache_enabled: bool,
    primary_fail_rate: float,
    backup_fail_rate: float,
) -> ReliabilityGateway:
    providers = [
        FakeLLMProvider("primary", primary_fail_rate, 1, 0.01),
        FakeLLMProvider("backup", backup_fail_rate, 1, 0.006),
    ]
    breakers = {
        "primary": CircuitBreaker("primary", failure_threshold=1, reset_timeout_seconds=0.2),
        "backup": CircuitBreaker("backup", failure_threshold=1, reset_timeout_seconds=0.2),
    }
    cache = ResponseCache(60, 0.3) if cache_enabled else None
    return ReliabilityGateway(providers, breakers, cache)


def show_case(title: str, gateway: ReliabilityGateway, prompt: str) -> None:
    result = gateway.complete(prompt)
    print(f"\n[{title}]")
    print(f"prompt: {prompt}")
    print(
        "route:",
        result.route,
        "| provider:",
        result.provider,
        "| cache_hit:",
        result.cache_hit,
        "| error:",
        result.error,
    )


def main() -> None:
    cache_gateway = build_gateway(cache_enabled=True, primary_fail_rate=0.0, backup_fail_rate=0.0)
    first_prompt = "Explain circuit breaker states in one paragraph."
    show_case("cache warm-up", cache_gateway, first_prompt)
    show_case("cache exact hit", cache_gateway, first_prompt)

    false_hit_gateway = build_gateway(cache_enabled=True, primary_fail_rate=0.0, backup_fail_rate=0.0)
    show_case("false-hit seed", false_hit_gateway, "Summarize refund policy for 2024 deadline")
    show_case("false-hit blocked", false_hit_gateway, "Summarize refund policy for 2026 deadline")

    privacy_gateway = build_gateway(cache_enabled=True, primary_fail_rate=0.0, backup_fail_rate=0.0)
    show_case("privacy bypass cache", privacy_gateway, "Give me the current account balance for user 123.")

    fallback_gateway = build_gateway(cache_enabled=False, primary_fail_rate=1.0, backup_fail_rate=0.0)
    show_case("fallback to backup", fallback_gateway, "Explain fallback routing.")
    show_case("primary open, still fallback", fallback_gateway, "Explain fallback routing again.")

    static_gateway = build_gateway(cache_enabled=False, primary_fail_rate=1.0, backup_fail_rate=1.0)
    show_case("static fallback", static_gateway, "Both providers are down now.")


if __name__ == "__main__":
    main()

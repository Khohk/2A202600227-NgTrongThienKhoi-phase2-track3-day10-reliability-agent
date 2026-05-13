from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.cache import ResponseCache


def main() -> None:
    cache = ResponseCache(ttl_seconds=60, similarity_threshold=0.3)

    cache.set("Explain circuit breaker states.", "Circuit breaker answer")
    hit, score = cache.get("Explain circuit breaker states.")
    print("exact hit:", hit, f"score={score:.2f}")

    cache.set("account balance for user 123", "private answer")
    private_hit, private_score = cache.get("account balance for user 123")
    print("privacy query:", private_hit, f"score={private_score:.2f}")

    cache.set("Summarize refund policy for 2024 deadline", "policy-2024")
    false_hit, false_score = cache.get("Summarize refund policy for 2026 deadline")
    print("year mismatch:", false_hit, f"score={false_score:.2f}")

    cache.set("What should I do when API calls return 429?", "rate-limit answer")
    api_hit, api_score = cache.get("What should I do when API calls return 500?")
    print("status-code mismatch:", api_hit, f"score={api_score:.2f}")


if __name__ == "__main__":
    main()

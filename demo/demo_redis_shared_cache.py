from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.cache import SharedRedisCache


def main() -> None:
    cache_a = SharedRedisCache(
        redis_url="redis://localhost:6379/0",
        ttl_seconds=60,
        similarity_threshold=0.5,
        prefix="rl:demo:",
    )
    cache_b = SharedRedisCache(
        redis_url="redis://localhost:6379/0",
        ttl_seconds=60,
        similarity_threshold=0.5,
        prefix="rl:demo:",
    )

    if not cache_a.ping():
        print("Redis is not reachable on localhost:6379")
        return

    cache_a.flush()
    cache_a.set("shared query", "shared response")
    hit, score = cache_b.get("shared query")

    print("instance A wrote: shared query")
    print(f"instance B read: {hit} | score={score:.2f}")

    cache_a.flush()
    cache_a.close()
    cache_b.close()


if __name__ == "__main__":
    main()

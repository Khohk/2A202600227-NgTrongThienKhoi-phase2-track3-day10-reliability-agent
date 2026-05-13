# Demo Folder

This folder contains small demo scripts that explain the main reliability flows
without changing the production code in `src/reliability_lab/`.

## Files

- `demo_circuit_breaker.py`: shows `CLOSED -> OPEN -> HALF_OPEN -> CLOSED`
- `demo_cache.py`: shows exact hit, privacy skip, and false-hit blocking when numbers differ
- `demo_gateway_fallback.py`: shows primary failure and fallback to backup provider
- `demo_chaos.py`: runs a tiny chaos simulation and prints metrics per scenario
- `demo_redis_shared_cache.py`: shows two Redis cache instances sharing the same state

## Run examples

Use your Python 3.10+ environment from the repo root:

```bash
python demo/demo_circuit_breaker.py
python demo/demo_cache.py
python demo/demo_gateway_fallback.py
python demo/demo_chaos.py
python demo/demo_redis_shared_cache.py
```

The Redis demo requires Redis running on `localhost:6379`.

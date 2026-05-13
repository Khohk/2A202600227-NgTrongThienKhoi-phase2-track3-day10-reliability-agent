# Scenario Map

This file summarizes the main execution paths in the current lab code.

## Gateway Flow

```text
prompt
  |
  v
cache enabled?
  | yes
  v
cache.get(prompt)
  | hit --------------------------> route = cache_hit:<score>
  | miss
  v
try primary provider through circuit breaker
  | success ----------------------> route = primary:<provider_name>
  | fail / circuit open
  v
try backup provider through circuit breaker
  | success ----------------------> route = fallback:<provider_name>
  | fail / circuit open
  v
static fallback ------------------> route = static_fallback
```

## Main Cases

| Scenario | Cache | Primary | Backup / another model | Expected route |
|---|---|---|---|---|
| Exact cache hit | enabled, has exact entry | not called | not called | `cache_hit:1.00` |
| Similar cache hit | enabled, similar text and same numbers | not called | not called | `cache_hit:<score>` |
| Privacy query | enabled but query contains `balance`, `account`, `user 123`, etc. | called | maybe called | `primary:*` or `fallback:*` |
| False-hit candidate | enabled, similar text but different numbers like `2024` vs `2026` | called | maybe called | cache blocked, provider path used |
| Cache disabled | disabled | called | maybe called | `primary:*` or `fallback:*` |
| Primary healthy | any | success | not needed | `primary:primary` |
| Primary fails once but backup healthy | any | fail | success | `fallback:backup` |
| Primary circuit opens | any | skipped after threshold | success if healthy | `fallback:backup` |
| Both models fail | any | fail/open | fail/open | `static_fallback` |
| Redis shared cache exact hit | redis enabled, entry written by another instance | not called | not called | `cache_hit:1.00` |

## Cache Logic

### Cache returns a hit when

- cache backend is enabled
- query is not privacy-sensitive
- similarity score is above `similarity_threshold`
- if numbers appear in both queries, the number sets must match

### Cache returns a miss when

- query matches privacy rules
- entry expired by TTL
- text is similar but numbers differ
- similarity score is below threshold

## Circuit Breaker Logic

| State | What happens |
|---|---|
| `CLOSED` | requests go through, failures are counted |
| `OPEN` | requests fail fast until timeout elapses |
| `HALF_OPEN` | one probe is allowed; success closes, failure re-opens |

## Chaos Scenarios In Current Config

| Scenario | Provider override | Expected effect |
|---|---|---|
| `primary_timeout_100` | `primary=1.0` | primary opens circuit, backup handles traffic |
| `primary_flaky_50` | `primary=0.5` | mix of primary and fallback, some circuit opens |
| `all_healthy` | `primary=0.0`, `backup=0.0` | primary handles requests, no circuit opens |

## Good Demo Inputs

- Cache exact hit:
  `Explain circuit breaker states in one paragraph.`
- Privacy skip:
  `Give me the current account balance for user 123.`
- False-hit block:
  `Summarize refund policy for 2024 deadline`
  `Summarize refund policy for 2026 deadline`
- Another numeric intent:
  `What should I do when API calls return 429?`
  `What should I do when API calls return 500?`

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="reports/metrics.json")
    parser.add_argument("--out", default="reports/final_report.md")
    args = parser.parse_args()
    metrics = json.loads(Path(args.metrics).read_text())
    scenarios = metrics.get("scenarios", {})
    lines = [
        "# Day 10 Reliability Final Report",
        "",
        "## Architecture Summary",
        "",
        "User -> Gateway -> Cache check -> Circuit breaker -> Provider chain -> Static fallback",
        "",
        "## Metrics Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in metrics.items():
        if key == "scenarios":
            continue
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Chaos Scenarios", "", "| Scenario | Status |", "|---|---|"]
    for key, value in scenarios.items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Notes",
        "",
        "- Fill in your config rationale table from `configs/default.yaml`.",
        "- Add a cache comparison section with cache enabled vs disabled metrics.",
        "- Include Redis local evidence from `redis-cli KEYS \"rl:cache:*\"` if you ran the shared cache path.",
        "- Add one short failure analysis section describing a remaining production risk.",
    ]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

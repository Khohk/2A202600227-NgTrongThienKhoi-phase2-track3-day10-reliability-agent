from __future__ import annotations

import argparse
import json
from pathlib import Path

from reliability_lab.chaos import load_queries, run_simulation
from reliability_lab.config import load_config


def format_delta(before: float, after: float) -> str:
    if before == 0:
        return "n/a" if after == 0 else f"+{after:.4f}"
    change = ((after - before) / before) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--off-config", default="configs/cache_compare_off.yaml")
    parser.add_argument("--on-config", default="configs/cache_compare_on.yaml")
    parser.add_argument("--json-out", default="reports/cache_comparison.json")
    parser.add_argument("--md-out", default="reports/cache_comparison.md")
    args = parser.parse_args()

    queries = load_queries()
    off_metrics = run_simulation(load_config(args.off_config), queries).to_report_dict()
    on_metrics = run_simulation(load_config(args.on_config), queries).to_report_dict()

    comparison = {
        "without_cache": off_metrics,
        "with_cache": on_metrics,
        "delta": {
            "latency_p50_ms": format_delta(float(off_metrics["latency_p50_ms"]), float(on_metrics["latency_p50_ms"])),
            "latency_p95_ms": format_delta(float(off_metrics["latency_p95_ms"]), float(on_metrics["latency_p95_ms"])),
            "estimated_cost": format_delta(float(off_metrics["estimated_cost"]), float(on_metrics["estimated_cost"])),
            "cache_hit_rate": format_delta(float(off_metrics["cache_hit_rate"]), float(on_metrics["cache_hit_rate"])),
        },
    }

    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(comparison, indent=2, ensure_ascii=False))

    lines = [
        "# Cache Comparison",
        "",
        "| Metric | Without cache | With cache | Delta |",
        "|---|---:|---:|---|",
        f"| latency_p50_ms | {off_metrics['latency_p50_ms']} | {on_metrics['latency_p50_ms']} | {comparison['delta']['latency_p50_ms']} |",
        f"| latency_p95_ms | {off_metrics['latency_p95_ms']} | {on_metrics['latency_p95_ms']} | {comparison['delta']['latency_p95_ms']} |",
        f"| estimated_cost | {off_metrics['estimated_cost']} | {on_metrics['estimated_cost']} | {comparison['delta']['estimated_cost']} |",
        f"| cache_hit_rate | {off_metrics['cache_hit_rate']} | {on_metrics['cache_hit_rate']} | {comparison['delta']['cache_hit_rate']} |",
    ]

    md_path = Path(args.md_out)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines))

    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")


if __name__ == "__main__":
    main()

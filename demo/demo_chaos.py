from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from reliability_lab.chaos import load_queries, run_scenario
from reliability_lab.config import ScenarioConfig, load_config


def main() -> None:
    config = load_config("configs/default.yaml")
    config.load_test.requests = 10
    queries = load_queries()

    scenarios = [
        ScenarioConfig(
            name="primary_timeout_100",
            description="Primary always fails",
            provider_overrides={"primary": 1.0},
        ),
        ScenarioConfig(
            name="primary_flaky_50",
            description="Primary fails half the time",
            provider_overrides={"primary": 0.5},
        ),
        ScenarioConfig(
            name="all_healthy",
            description="Both providers healthy",
            provider_overrides={"primary": 0.0, "backup": 0.0},
        ),
    ]

    for scenario in scenarios:
        metrics = run_scenario(config, queries, scenario)
        print(f"\nscenario: {scenario.name}")
        print(metrics.to_report_dict())


if __name__ == "__main__":
    main()

"""Tests for the newsvendor-style risk model."""

from __future__ import annotations

import numpy as np
import pytest

from risk_model import SCENARIOS, calculate_risk_with_controls

PRESETS = [name for name in SCENARIOS if name != "Custom"]


def run(scenario: dict, maturity: int = 0, **overrides: float) -> dict:
    args = {k: scenario[k] for k in ("mean_demand", "std_demand", "cost_overage", "cost_underage", "volume")}
    args.update(overrides)
    return calculate_risk_with_controls(**args, trust_maturity=maturity)


@pytest.mark.parametrize("name", PRESETS)
def test_threshold_is_the_critical_ratio_quantile(name: str) -> None:
    scenario = SCENARIOS[name]
    result = run(scenario)
    ratio = scenario["cost_overage"] / (scenario["cost_overage"] + scenario["cost_underage"])
    expected = np.percentile(result["demand_scenarios_baseline"], ratio * 100)
    assert result["optimal_static_q_baseline"] == pytest.approx(expected)
    assert result["optimal_static_q_baseline"] > 0


@pytest.mark.parametrize("name", PRESETS)
def test_failure_cost_changes_the_result(name: str) -> None:
    scenario = SCENARIOS[name]
    high = run(scenario, cost_overage=scenario["cost_overage"] * 1.2)["annual_evpi"]
    low = run(scenario, cost_overage=scenario["cost_overage"] * 0.8)["annual_evpi"]
    assert high > low


@pytest.mark.parametrize("name", PRESETS)
def test_higher_maturity_lowers_expected_cost(name: str) -> None:
    scenario = SCENARIOS[name]
    costs = [run(scenario, maturity=level)["expected_cost_improved"] for level in range(6)]
    assert all(later <= earlier for earlier, later in zip(costs, costs[1:]))
    assert run(scenario, maturity=0)["annual_evsi"] == pytest.approx(0.0)


def test_costs_are_per_decision_times_volume() -> None:
    scenario = SCENARIOS[PRESETS[0]]
    result = run(scenario)
    assert result["annual_evpi"] == pytest.approx(result["expected_cost_baseline"] * scenario["volume"])

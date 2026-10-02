"""Risk model for the calculator: a newsvendor-style threshold on a simulated AI failure rate."""

from typing import Dict

import numpy as np


# ============================================================================
# THE MODEL
# ============================================================================
def calculate_risk_with_controls(
    mean_demand: float,
    std_demand: float,
    cost_overage: float,
    cost_underage: float,
    volume: int,
    trust_maturity: int = 0,
    n_simulations: int = 10000
) -> Dict:
    """
    Compute a baseline mismatch cost per decision (labeled EVPI) and the cost
    difference under a maturity level's assumed reductions (labeled EVSI, this
    tool's own term), from a Monte Carlo draw of failure rates.
    
    A newsvendor-style model of AI risk:
    - Demand = failures per decision, which is uncertain
    - The threshold = review capacity, set at the critical-ratio quantile
    - Shortfall = failures beyond the threshold; each costs cost_overage
    - Excess = review capacity beyond the actual failures; each costs cost_underage
    
    Args:
        mean_demand: Average risk level (failures per 1000 decisions)
        std_demand: Spread of the failure rate (failures per 1000 decisions)
        cost_overage: Cost per failure event
        cost_underage: Cost per review
        volume: Annual decision volume
        trust_maturity: Control maturity level (0 to 5)
        n_simulations: Number of Monte Carlo runs
    
    Returns:
        Dictionary with the baseline cost (labeled EVPI), the cost difference under the maturity level (labeled EVSI) and related figures
    """
    
    # The maturity level cuts the spread and the failure cost; the mean failure rate never changes
    # Level 0: No controls (baseline)
    # Levels 1 to 5: larger assumed reductions
    uncertainty_reduction = {
        0: 0.0,   # No controls
        1: 0.15,  # Basic logging & monitoring
        2: 0.30,  # + Data provenance tracking
        3: 0.45,  # + Continuous validation & attestation
        4: 0.60,  # + practices aligned to NIST AI RMF
        5: 0.75   # + Defense-in-depth + real-time intervention
    }
    
    failure_cost_reduction = {
        0: 0.0,   # No controls
        1: 0.10,  # Early detection reduces impact
        2: 0.20,  # + Incident response automation
        3: 0.35,  # + Predictive risk scoring
        4: 0.50,  # + Zero-trust architecture
        5: 0.65   # + AI safety guardrails
    }
    
    reduction_factor = uncertainty_reduction.get(trust_maturity, 0.0)
    cost_reduction_factor = failure_cost_reduction.get(trust_maturity, 0.0)
    
    # Normalize mean_demand: treat as failures per 1000 decisions
    # So mean_demand = 45 means 45 failures per 1000 decisions = 4.5% failure rate
    failure_rate_baseline = mean_demand / 1000.0  # Convert to rate per decision
    failure_rate_std = std_demand / 1000.0
    
    # Generate demand scenarios as failure rates (0-1 scale)
    np.random.seed(42)  # For reproducibility
    demand_scenarios_baseline = np.random.normal(failure_rate_baseline, failure_rate_std, n_simulations)
    demand_scenarios_baseline = np.clip(demand_scenarios_baseline, 0, 1)  # Keep between 0-1
    
    # The same draws with the level's reduced spread
    # Reset seed to ensure same base scenarios, then apply reduction
    improved_std = failure_rate_std * (1 - reduction_factor)
    np.random.seed(42)  # Same seed for fair comparison
    demand_scenarios_improved = np.random.normal(failure_rate_baseline, improved_std, n_simulations)
    demand_scenarios_improved = np.clip(demand_scenarios_improved, 0, 1)
    
    # The level's reduced failure cost
    effective_cost_overage = cost_overage * (1 - cost_reduction_factor)
    
    # Optimal static threshold (as a failure rate): the newsvendor critical-ratio
    # quantile. A shortfall (failures beyond the threshold) costs a failure each;
    # an excess (review capacity beyond the actual failures) costs a review each.
    critical_ratio = cost_overage / (cost_overage + cost_underage)
    optimal_static_q_baseline = np.percentile(demand_scenarios_baseline, critical_ratio * 100)

    # Same rule for the improved scenario
    critical_ratio_improved = effective_cost_overage / (effective_cost_overage + cost_underage)
    optimal_static_q_improved = np.percentile(demand_scenarios_improved, critical_ratio_improved * 100)

    # Expected cost PER DECISION with the BASELINE strategy (no controls)
    shortfall_baseline = np.maximum(demand_scenarios_baseline - optimal_static_q_baseline, 0)
    excess_baseline = np.maximum(optimal_static_q_baseline - demand_scenarios_baseline, 0)
    costs_baseline = (shortfall_baseline * cost_overage) + (excess_baseline * cost_underage)
    expected_cost_baseline = np.mean(costs_baseline)

    # Expected cost PER DECISION with the level's assumptions
    shortfall_improved = np.maximum(demand_scenarios_improved - optimal_static_q_improved, 0)
    excess_improved = np.maximum(optimal_static_q_improved - demand_scenarios_improved, 0)
    costs_improved = (shortfall_improved * effective_cost_overage) + (excess_improved * cost_underage)
    expected_cost_improved = np.mean(costs_improved)
    
    # Calculate expected cost with perfect information
    expected_cost_perfect = 0
    
    # Baseline mismatch cost per decision; the perfect-information cost is 0, so this equals the EVPI
    evpi = expected_cost_baseline - expected_cost_perfect
    # Annual cost = cost per decision * number of decisions
    annual_evpi = evpi * volume
    
    # Cost difference under the level's assumed reductions (labeled EVSI here)
    evsi = expected_cost_baseline - expected_cost_improved
    annual_evsi = evsi * volume
    
    # The difference as a share of the baseline
    recovery_percentage = (evsi / evpi * 100) if evpi > 0 else 0
    
    return {
        'evpi': evpi,
        'annual_evpi': annual_evpi,
        'evsi': evsi,
        'annual_evsi': annual_evsi,
        'recovery_percentage': recovery_percentage,
        'expected_cost_baseline': expected_cost_baseline,
        'expected_cost_improved': expected_cost_improved,
        'optimal_static_q_baseline': optimal_static_q_baseline,
        'optimal_static_q_improved': optimal_static_q_improved,
        'demand_scenarios_baseline': demand_scenarios_baseline,
        'demand_scenarios_improved': demand_scenarios_improved,
        'costs_baseline': costs_baseline,
        'costs_improved': costs_improved,
        'mean_demand': mean_demand,
        'std_demand': std_demand,
        'improved_std': improved_std,
        'trust_maturity': trust_maturity,
        'uncertainty_reduction': reduction_factor,
        'cost_reduction': cost_reduction_factor
    }

# ============================================================================
# PRE-DEFINED SCENARIOS
# ============================================================================
SCENARIOS = {
    "Custom": {
        "mean_demand": 50.0,      # 50 failures per 1000 decisions = 5% failure rate
        "std_demand": 15.0,       # Standard deviation in failures per 1000
        "cost_overage": 100000,   # Cost per failure event
        "cost_underage": 5000,    # Cost per manual intervention
        "volume": 1000,           # Annual decision volume
        "description": "Configure your own scenario"
    },
    "Radiology AI (Diagnostic Errors)": {
        "mean_demand": 45.0,      # 45 failures per 1000 scans = 4.5% failure rate
        "std_demand": 20.0,       # Variability in failure rate
        "cost_overage": 2500000,  # illustrative cost per failure
        "cost_underage": 15000,   # illustrative cost per review
        "volume": 50000,          # Annual scans
        "description": "Illustrative: an AI reading radiology studies"
    },
    "OT Valve Controller (ICS/SCADA)": {
        "mean_demand": 30.0,      # 30 failures per 1000 decisions = 3% failure rate
        "std_demand": 25.0,       # High variability in control systems
        "cost_overage": 5000000,  # illustrative cost per failure
        "cost_underage": 25000,   # illustrative cost per review
        "volume": 8760,           # Hourly decisions (24/7/365)
        "description": "Illustrative: an AI advising an industrial valve controller"
    },
    "Pharmacy Automation (Drug Dispensing)": {
        "mean_demand": 40.0,      # 40 failures per 1000 dispenses = 4% failure rate
        "std_demand": 18.0,       # Moderate variability
        "cost_overage": 1500000,  # illustrative cost per failure
        "cost_underage": 8000,    # illustrative cost per review
        "volume": 100000,         # Annual dispensing decisions
        "description": "Illustrative: automated medication dispensing"
    }
}

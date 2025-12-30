import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Tuple, Dict
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Cost of Untrusted AI Calculator | HealthSec Alliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
    }
    .big-red-number {
        font-size: 72px;
        font-weight: bold;
        color: #ff4b4b;
        text-align: center;
        margin: 20px 0;
    }
    .subtitle {
        font-size: 24px;
        color: #ffa500;
        text-align: center;
        margin-bottom: 30px;
    }
    .insight-box {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ffa500;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# MONTE CARLO EVPI/EVSI CALCULATION ENGINE
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
    Calculate Expected Value of Perfect Information (EVPI) and 
    Expected Value of Sample Information (EVSI) using Monte Carlo simulation.
    
    This adapts the Newsvendor model to AI Risk:
    - Demand = AI Risk Events (uncertain)
    - Overage = Cost of failure (lawsuit, breach, harm)
    - Underage = Cost of inefficiency (manual review, missed opportunity)
    
    Args:
        mean_demand: Average risk level (failures per 1000 decisions)
        std_demand: Uncertainty/volatility in risk (failures per 1000 decisions)
        cost_overage: Cost per failure event
        cost_underage: Cost per manual intervention
        volume: Annual decision volume
        trust_maturity: Trust stack maturity level (0-5)
        n_simulations: Number of Monte Carlo runs
    
    Returns:
        Dictionary with EVPI, EVSI and related metrics
    """
    
    # Trust maturity reduces uncertainty and failure probability
    # Level 0: No controls (baseline)
    # Level 1-5: Incremental control improvements
    uncertainty_reduction = {
        0: 0.0,   # No controls
        1: 0.15,  # Basic logging & monitoring
        2: 0.30,  # + Data provenance tracking
        3: 0.45,  # + Continuous validation & attestation
        4: 0.60,  # + Full NIST AI RMF compliance
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
    
    # Generate improved scenarios with controls (reduced uncertainty)
    # Reset seed to ensure same base scenarios, then apply reduction
    improved_std = failure_rate_std * (1 - reduction_factor)
    np.random.seed(42)  # Same seed for fair comparison
    demand_scenarios_improved = np.random.normal(failure_rate_baseline, improved_std, n_simulations)
    demand_scenarios_improved = np.clip(demand_scenarios_improved, 0, 1)
    
    # Reduce failure costs with controls
    effective_cost_overage = cost_overage * (1 - cost_reduction_factor)
    
    # Calculate optimal static threshold for baseline (as failure rate)
    critical_ratio = cost_underage / (cost_overage + cost_underage)
    optimal_static_q_baseline = np.percentile(demand_scenarios_baseline, critical_ratio * 100)
    
    # Calculate optimal for improved scenario
    critical_ratio_improved = cost_underage / (effective_cost_overage + cost_underage)
    optimal_static_q_improved = np.percentile(demand_scenarios_improved, critical_ratio_improved * 100)
    
    # Calculate expected cost PER DECISION with BASELINE strategy (no controls)
    # overage = excess failures beyond threshold (cost per failure)
    # underage = excess manual reviews (cost per review)
    overage_baseline = np.maximum(optimal_static_q_baseline - demand_scenarios_baseline, 0)
    underage_baseline = np.maximum(demand_scenarios_baseline - optimal_static_q_baseline, 0)
    
    # Cost per decision = (excess failures * cost_per_failure) + (excess reviews * cost_per_review)
    # Scale by volume to get expected failures/reviews
    costs_baseline = (overage_baseline * cost_overage) + (underage_baseline * cost_underage)
    expected_cost_baseline = np.mean(costs_baseline)
    
    # Calculate expected cost PER DECISION with IMPROVED strategy (with controls)
    overage_improved = np.maximum(optimal_static_q_improved - demand_scenarios_improved, 0)
    underage_improved = np.maximum(demand_scenarios_improved - optimal_static_q_improved, 0)
    costs_improved = (overage_improved * effective_cost_overage) + (underage_improved * cost_underage)
    expected_cost_improved = np.mean(costs_improved)
    
    # Calculate expected cost with perfect information
    expected_cost_perfect = 0
    
    # EVPI: Value of perfect information (theoretical max) - per decision
    evpi = expected_cost_baseline - expected_cost_perfect
    # Annual cost = cost per decision * number of decisions
    annual_evpi = evpi * volume
    
    # EVSI: Value of sample/improved information (with controls)
    evsi = expected_cost_baseline - expected_cost_improved
    annual_evsi = evsi * volume
    
    # Recoverable value percentage
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
        "cost_overage": 2500000,  # Malpractice lawsuit avg per failure
        "cost_underage": 15000,   # Radiologist review cost per intervention
        "volume": 50000,          # Annual scans
        "description": "AI diagnostic system with liability exposure"
    },
    "OT Valve Controller (ICS/SCADA)": {
        "mean_demand": 30.0,      # 30 failures per 1000 decisions = 3% failure rate
        "std_demand": 25.0,       # High variability in control systems
        "cost_overage": 5000000,  # Safety incident, downtime per failure
        "cost_underage": 25000,   # Manual intervention cost
        "volume": 8760,           # Hourly decisions (24/7/365)
        "description": "Industrial control system with physical safety impact"
    },
    "Pharmacy Automation (Drug Dispensing)": {
        "mean_demand": 40.0,      # 40 failures per 1000 dispenses = 4% failure rate
        "std_demand": 18.0,       # Moderate variability
        "cost_overage": 1500000,  # Adverse drug event litigation per failure
        "cost_underage": 8000,    # Pharmacist verification cost per intervention
        "volume": 100000,         # Annual dispensing decisions
        "description": "Automated medication dispensing with patient safety risk"
    }
}

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Header
st.markdown("<h1 style='text-align: center; color: white;'>🛡️ Cost of Untrusted AI Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 18px;'>Quantify the Risk Tax of Operating AI Without Verification | HealthSec Alliance</p>", unsafe_allow_html=True)

# Disclaimer banner
st.markdown("""
<div style='background-color: #2d2d3d; padding: 12px 20px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ffa500;'>
<p style='margin: 0; font-size: 13px; color: #ccc;'>
<strong style='color: #ffa500;'>📊 Scenario Explorer:</strong> This tool provides illustrative risk scenarios for strategic planning and discussion. 
Estimates are based on simplified models and industry experience. Actual risk quantification requires detailed organizational assessment.
</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR INPUTS
# ============================================================================
st.sidebar.header("⚙️ Risk Configuration")

# Scenario selector
scenario_name = st.sidebar.selectbox(
    "Select Scenario",
    list(SCENARIOS.keys()),
    index=0
)
scenario = SCENARIOS[scenario_name]

st.sidebar.markdown(f"*{scenario['description']}*")
st.sidebar.markdown("---")

# Financial inputs
st.sidebar.subheader("💰 Financial Parameters")
cost_overage = st.sidebar.number_input(
    "Cost of Failure (Overage) - $",
    min_value=1000,
    max_value=100000000,
    value=scenario['cost_overage'],
    step=10000,
    help="Cost when AI over-performs or fails catastrophically (e.g., lawsuit, breach, harm)"
)

cost_underage = st.sidebar.number_input(
    "Cost of Human Labor/Inefficiency (Underage) - $",
    min_value=100,
    max_value=1000000,
    value=scenario['cost_underage'],
    step=1000,
    help="Cost when AI under-performs and humans must intervene (e.g., manual review)"
)

volume = st.sidebar.number_input(
    "Annual Decision Volume",
    min_value=1,
    max_value=10000000,
    value=scenario['volume'],
    step=1000,
    help="Number of AI decisions made per year"
)

# Risk parameters
st.sidebar.subheader("📊 Risk Parameters")
mean_demand = st.sidebar.slider(
    "Mean Failure Rate (per 1000 decisions)",
    min_value=1.0,
    max_value=100.0,
    value=scenario['mean_demand'],
    step=1.0,
    help="Expected failures per 1000 decisions (e.g., 45 = 4.5% failure rate)"
)

std_demand = st.sidebar.slider(
    "Failure Rate Uncertainty (σ per 1000)",
    min_value=1.0,
    max_value=50.0,
    value=scenario['std_demand'],
    step=1.0,
    help="Standard deviation in failure rate - how unpredictable is the AI behavior?"
)

# Trust Stack Maturity
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Trust Stack Maturity")
trust_maturity = st.sidebar.select_slider(
    "Control Maturity Level",
    options=[0, 1, 2, 3, 4, 5],
    value=0,
    format_func=lambda x: {
        0: "L0: None (Baseline)",
        1: "L1: Basic Monitoring",
        2: "L2: + Provenance",
        3: "L3: + Attestation",
        4: "L4: + NIST AI RMF",
        5: "L5: Defense-in-Depth"
    }[x],
    help="Select your current or target trust control maturity level"
)

st.sidebar.markdown(f"""
<div style='background-color: #1e2130; padding: 10px; border-radius: 5px; font-size: 12px;'>
<strong>Level {trust_maturity}:</strong><br>
{['No controls - baseline risk', 
  'Basic logging & monitoring', 
  'Data provenance tracking', 
  'Continuous validation & attestation',
  'Full NIST AI RMF compliance',
  'Defense-in-depth + real-time intervention'][trust_maturity]}
</div>
<p style='font-size: 10px; color: #666; margin-top: 8px;'>
<em>Risk reduction estimates based on industry experience and control effectiveness research.</em>
</p>
""", unsafe_allow_html=True)

# Run calculation
if st.sidebar.button("🔄 Recalculate", type="primary"):
    st.rerun()

# ============================================================================
# MAIN PANEL - CALCULATIONS AND RESULTS
# ============================================================================

# Run the risk calculation with trust maturity
results = calculate_risk_with_controls(
    mean_demand=mean_demand,
    std_demand=std_demand,
    cost_overage=cost_overage,
    cost_underage=cost_underage,
    volume=volume,
    trust_maturity=trust_maturity
)

# ============================================================================
# THE BIG NUMBER
# ============================================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if trust_maturity == 0:
        st.markdown(
            f"<div class='big-red-number'>${results['annual_evpi']:,.0f}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<div class='subtitle'>Estimated Annual Cost of AI Uncertainty</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='big-red-number' style='color: #00ff00;'>${results['annual_evsi']:,.0f}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='subtitle'>Estimated Annual Recoverable Value (L{trust_maturity})</div>",
            unsafe_allow_html=True
        )

# ============================================================================
# KEY METRICS
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Baseline Annual Cost",
        value=f"${results['annual_evpi']:,.0f}",
        delta=None
    )

with col2:
    st.metric(
        label=f"Recoverable (L{trust_maturity})",
        value=f"${results['annual_evsi']:,.0f}",
        delta=f"{results['recovery_percentage']:.1f}% of max",
        delta_color="normal"
    )

with col3:
    baseline_std_normalized = results['std_demand'] / 1000.0
    st.metric(
        label="Uncertainty Reduction",
        value=f"{results['uncertainty_reduction']*100:.0f}%",
        delta=f"σ: {baseline_std_normalized:.4f} → {results['improved_std']:.4f} (per decision)"
    )

with col4:
    st.metric(
        label="Failure Cost Reduction",
        value=f"{results['cost_reduction']*100:.0f}%",
        delta=f"Per event savings"
    )

st.markdown("---")

# ============================================================================
# VISUALIZATION
# ============================================================================
st.subheader("📈 Risk Distribution & Impact")

# Create comparison histogram
fig = go.Figure()

# Add baseline costs
fig.add_trace(go.Histogram(
    x=results['costs_baseline'],
    nbinsx=50,
    name='Baseline (No Controls)',
    marker_color='rgba(255, 75, 75, 0.6)',
    hovertemplate='Cost Range: $%{x:,.0f}<br>Frequency: %{y}<extra></extra>'
))

# Add improved costs if controls are active
if trust_maturity > 0:
    fig.add_trace(go.Histogram(
        x=results['costs_improved'],
        nbinsx=50,
        name=f'With Controls (L{trust_maturity})',
        marker_color='rgba(0, 255, 0, 0.6)',
        hovertemplate='Cost Range: $%{x:,.0f}<br>Frequency: %{y}<extra></extra>'
    ))

# Add mean lines
fig.add_vline(
    x=results['expected_cost_baseline'],
    line_dash="dash",
    line_color="red",
    annotation_text=f"Baseline: ${results['expected_cost_baseline']:,.2f}",
    annotation_position="top left"
)

if trust_maturity > 0:
    fig.add_vline(
        x=results['expected_cost_improved'],
        line_dash="dash",
        line_color="green",
        annotation_text=f"Improved: ${results['expected_cost_improved']:,.2f}",
        annotation_position="top right"
    )

fig.update_layout(
    title="Cost Distribution: Baseline vs. Trust Controls",
    xaxis_title="Cost per Decision ($)",
    yaxis_title="Frequency (out of 10,000 simulations)",
    template="plotly_dark",
    height=400,
    showlegend=True,
    barmode='overlay'
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# RISK DISTRIBUTION CURVE
# ============================================================================
fig2 = go.Figure()

# Baseline risk events
fig2.add_trace(go.Histogram(
    x=results['demand_scenarios_baseline'],
    nbinsx=50,
    name='Baseline Risk',
    marker_color='rgba(255, 75, 75, 0.6)',
    histnorm='probability density'
))

# Improved risk events if controls active
if trust_maturity > 0:
    fig2.add_trace(go.Histogram(
        x=results['demand_scenarios_improved'],
        nbinsx=50,
        name=f'With Controls (L{trust_maturity})',
        marker_color='rgba(0, 255, 0, 0.6)',
        histnorm='probability density'
    ))

    # Add threshold lines
    fig2.add_vline(
        x=results['optimal_static_q_baseline'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Baseline Threshold: {results['optimal_static_q_baseline']:.3f} ({results['optimal_static_q_baseline']*1000:.1f} per 1000)",
        annotation_position="top left"
    )

    if trust_maturity > 0:
        fig2.add_vline(
            x=results['optimal_static_q_improved'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Improved Threshold: {results['optimal_static_q_improved']:.3f} ({results['optimal_static_q_improved']*1000:.1f} per 1000)",
            annotation_position="top right"
        )

fig2.update_layout(
    title="Failure Rate Distribution: Impact of Trust Controls",
    xaxis_title="Failure Rate (per decision, 0-1 scale)",
    yaxis_title="Probability Density",
    template="plotly_dark",
    height=400,
    barmode='overlay'
)

st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# INSIGHTS & EXPLANATION
# ============================================================================
st.markdown("---")
st.subheader("🎯 What Does This Mean?")

if trust_maturity == 0:
    st.markdown(f"""
<div class='insight-box'>
<h3 style='color: #ffa500;'>The Cost of Uncertainty (Baseline)</h3>
<p style='font-size: 18px;'>
Your organization is currently paying a <strong style='color: #ff4b4b;'>"Risk Tax"</strong> 
of <strong style='color: #ff4b4b;'>${results['annual_evpi']:,.0f} annually</strong> 
by operating AI systems without trust verification.
</p>
<p style='font-size: 16px;'>
This cost comes from two sources:
</p>
<ul style='font-size: 16px;'>
<li><strong>Over-trust failures:</strong> When AI makes errors that lead to costly incidents (${cost_overage:,} per event)</li>
<li><strong>Under-trust inefficiency:</strong> When humans must intervene because AI isn't trusted (${cost_underage:,} per intervention)</li>
</ul>
<p style='font-size: 16px; margin-top: 20px;'>
💡 <strong>Next Step:</strong> Use the <strong>Trust Stack Maturity</strong> slider in the sidebar to see how controls reduce this cost.
</p>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class='insight-box'>
<h3 style='color: #00ff00;'>Value of Trust Controls (Level {trust_maturity})</h3>
<p style='font-size: 18px;'>
By implementing <strong style='color: #00ff00;'>Trust Level {trust_maturity}</strong> controls, 
you can recover <strong style='color: #00ff00;'>${results['annual_evsi']:,.0f} annually</strong> 
— that's <strong>{results['recovery_percentage']:.1f}%</strong> of the theoretical maximum.
</p>
<p style='font-size: 16px;'>
<strong>How controls reduce risk:</strong>
</p>
<ul style='font-size: 16px;'>
<li>✅ <strong>Uncertainty reduction:</strong> {results['uncertainty_reduction']*100:.0f}% (failure rate σ: {results['std_demand']/1000:.4f} → {results['improved_std']:.4f} per decision)</li>
<li>✅ <strong>Failure cost reduction:</strong> {results['cost_reduction']*100:.0f}% per incident</li>
<li>✅ <strong>Annual savings:</strong> ${results['annual_evsi']:,.0f}</li>
<li>✅ <strong>Baseline cost:</strong> ${results['annual_evpi']:,.0f} → <strong>Improved:</strong> ${results['annual_evpi'] - results['annual_evsi']:,.0f}</li>
</ul>
<p style='font-size: 16px; margin-top: 20px;'>
<strong style='color: #ffa500;'>The HealthSec Alliance Trust Stack</strong> provides:
</p>
<ul style='font-size: 14px;'>
<li>✅ Cryptographic verification of AI training data provenance</li>
<li>✅ Continuous monitoring and attestation of AI behavior</li>
<li>✅ Auditable trust chains for HIPAA, FDA, and GxP compliance</li>
<li>✅ Real-time risk scoring and automated intervention</li>
</ul>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================
st.markdown("---")
st.subheader("📊 Sensitivity Analysis: What Drives Your Risk?")

# Calculate sensitivity by varying each parameter ±20%
def calculate_sensitivities():
    base_annual_cost = results['annual_evpi']
    sensitivities = {}
    
    # Test cost_overage impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage * 1.2, cost_underage, volume, 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage * 0.8, cost_underage, volume, 0
    )
    sensitivities['Failure Cost'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
    # Test cost_underage impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage * 1.2, volume, 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage * 0.8, volume, 0
    )
    sensitivities['Inefficiency Cost'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
    # Test volume impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage, int(volume * 1.2), 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage, int(volume * 0.8), 0
    )
    sensitivities['Decision Volume'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
    # Test uncertainty impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand * 1.2, cost_overage, cost_underage, volume, 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand * 0.8, cost_overage, cost_underage, volume, 0
    )
    sensitivities['AI Uncertainty (σ)'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
    return sensitivities

with st.spinner('Calculating sensitivity...'):
    sensitivities = calculate_sensitivities()

# Sort by absolute impact
sorted_sens = dict(sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True))

col1, col2 = st.columns([1, 1])

with col1:
    # Tornado chart
    fig_tornado = go.Figure()
    
    params = list(sorted_sens.keys())
    values = [sorted_sens[p] for p in params]
    
    colors = ['#ff4b4b' if v > 0 else '#00ff00' for v in values]
    
    fig_tornado.add_trace(go.Bar(
        y=params,
        x=values,
        orientation='h',
        marker_color=colors,
        text=[f'${abs(v):,.0f}' for v in values],
        textposition='outside',
        hovertemplate='%{y}<br>Impact: $%{x:,.0f}<extra></extra>'
    ))
    
    fig_tornado.update_layout(
        title="Tornado Diagram: Top Risk Drivers (±20% change)",
        xaxis_title="Impact on Annual Cost ($)",
        yaxis_title="",
        template="plotly_dark",
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig_tornado, use_container_width=True)

with col2:
    st.markdown("""
    <div style='background-color: #1e2130; padding: 20px; border-radius: 10px; height: 350px;'>
    <h4 style='color: #ffa500;'>Key Insights</h4>
    <p style='font-size: 14px;'>
    This tornado diagram shows how a <strong>±20% change</strong> in each parameter 
    affects your annual risk cost.
    </p>
    <p style='font-size: 14px; margin-top: 15px;'>
    <strong style='color: #ff4b4b;'>Focus on the largest bars</strong> — these are your 
    highest-leverage areas for risk reduction.
    </p>
    <ul style='font-size: 13px; margin-top: 15px;'>
    """, unsafe_allow_html=True)
    
    for i, (param, value) in enumerate(sorted_sens.items()):
        if i < 2:  # Top 2 drivers
            st.markdown(f"<li><strong>{param}:</strong> {abs(value/results['annual_evpi']*100):.1f}% impact</li>", unsafe_allow_html=True)
    
    st.markdown("""
    </ul>
    <p style='font-size: 13px; margin-top: 15px; color: #888;'>
    <strong>Break-even analysis:</strong><br>
    If trust stack costs &lt; ${:,.0f}/year, it's justified.
    </p>
    </div>
    """.format(results['annual_evsi'] if trust_maturity > 0 else results['annual_evpi'] * 0.4), unsafe_allow_html=True)

# ============================================================================
# THE MATH EXPLAINED
# ============================================================================
with st.expander("📐 How Is This Calculated? (The Math)"):
    st.markdown("""
    ### The Expected Value of Perfect Information (EVPI)
    
    This calculator uses the **Newsvendor Model** from operations research, adapted for AI risk.
    
    **The Core Equation:**
    ```
    EVPI = E[Cost_with_uncertainty] - E[Cost_with_perfect_information]
    ```
    
    **What We're Modeling:**
    - **Failure Rate:** The probability that an AI decision will fail (e.g., 45 failures per 1000 = 4.5% failure rate)
    - **Current Strategy:** You set a static threshold for when to trust AI vs. when to intervene manually
    - **Perfect Information:** You would know exactly when AI will fail and act accordingly
    
    **The Simulation:**
    1. We normalize your input (failures per 1000 decisions) to a failure rate per decision (0-1 scale)
    2. We generate 10,000 scenarios of potential failure rates using your uncertainty parameters
    3. For each scenario, we calculate the cost per decision of your current static strategy
    4. We compare this to the theoretical cost if you had perfect foresight
    5. The gap is the **EVPI** (cost per decision), multiplied by volume to get annual cost
    
    **Trust Maturity Impact:**
    The risk reduction percentages (15-75% uncertainty reduction, 10-65% cost reduction) are based on 
    industry experience with trust control implementations. Actual results depend on implementation 
    quality, organizational context, and specific AI system characteristics.
    
    **Key Assumptions:**
    - Failure rates are approximately normally distributed
    - Costs are proportional to failure/intervention rates
    - Trust controls reduce uncertainty and failure impact progressively
    
    **Limitations:**
    - This is a simplified model for strategic planning, not a precise actuarial calculation
    - Actual failure rates and costs should be validated with organizational data
    - Tail risks (rare catastrophic events) may not be fully captured
    
    **References:**
    - Cachon, G. & Terwiesch, C. (2013). *Matching Supply with Demand*. McGraw-Hill.
    - NIST AI Risk Management Framework (2023)
    - Howard, R.A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics*.
    """)

# ============================================================================
# COMPLIANCE & CONTROLS TRACEABILITY
# ============================================================================
with st.expander("🔒 Compliance & Control Traceability Matrix"):
    st.markdown("""
    ### How Trust Controls Map to Regulatory Requirements
    
    This matrix shows how each trust maturity level addresses key compliance frameworks 
    relevant to healthcare, life sciences, medtech, and defense sectors.
    """)
    
    # Create compliance mapping dataframe
    compliance_data = {
        'Control Level': ['L0: Baseline', 'L1: Monitoring', 'L2: Provenance', 'L3: Attestation', 'L4: NIST AI RMF', 'L5: Defense-in-Depth'],
        'NIST AI RMF': [
            '❌ No coverage',
            '🟡 GOVERN-1.1 (policies)',
            '🟡 MAP-1.1 (context)',
            '🟢 MEASURE-2.1 (validation)',
            '🟢 MANAGE-4.1 (continuous)',
            '🟢 All functions covered'
        ],
        'HIPAA Security': [
            '❌ No coverage',
            '🟡 §164.308(a)(1) (audit)',
            '🟢 §164.312(b) (audit logs)',
            '🟢 §164.308(a)(5) (integrity)',
            '🟢 §164.308(a)(8) (evaluation)',
            '🟢 Full administrative controls'
        ],
        'FDA 21 CFR Part 11': [
            '❌ No coverage',
            '🟡 §11.10(e) (audit trail)',
            '🟢 §11.10(a) (validation)',
            '🟢 §11.10(k) (system checks)',
            '🟢 §11.50 (signature/record)',
            '🟢 Full Part 11 compliance'
        ],
        'ISO 13485 (MedTech)': [
            '❌ No coverage',
            '🟡 7.3.2 (design inputs)',
            '🟢 7.5.1 (production control)',
            '🟢 7.5.6 (validation)',
            '🟢 8.2.1 (monitoring)',
            '🟢 Full QMS integration'
        ],
        'NIST 800-53': [
            '❌ No coverage',
            '🟡 AU-2 (audit events)',
            '🟢 CM-3 (configuration mgmt)',
            '🟢 SI-7 (integrity verification)',
            '🟢 RA-5 (vulnerability monitoring)',
            '🟢 All control families'
        ]
    }
    
    df_compliance = pd.DataFrame(compliance_data)
    
    # Style the dataframe
    st.dataframe(
        df_compliance,
        use_container_width=True,
        hide_index=True,
        height=280
    )
    
    st.markdown("---")
    
    # Evidence artifacts by level
    st.markdown("### 📋 Evidence Artifacts Generated by Trust Level")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Level 1-2: Basic Documentation**
        - System activity logs (timestamped)
        - Data lineage documentation
        - Model versioning records
        - Change control logs
        - Training data manifests
        
        **Level 3-4: Compliance-Ready**
        - Cryptographic attestation certificates
        - Continuous validation reports
        - Risk assessment documentation
        - Audit trail (tamper-evident)
        - Model cards with provenance
        - Automated compliance reports
        """)
    
    with col2:
        st.markdown("""
        **Level 5: Audit-Ready Defense**
        - Real-time monitoring dashboards
        - Automated incident response logs
        - Zero-trust verification records
        - Supply chain integrity reports
        - Regulatory submission packages
        - Executive risk summary reports
        - Third-party audit evidence bundles
        - Litigation defense documentation
        """)
    
    st.markdown("---")
    
    # Framework references
    st.markdown("""
    <div style='background-color: #1e2130; padding: 15px; border-radius: 10px;'>
    <h4 style='color: #ffa500;'>Framework References</h4>
    <ul style='font-size: 13px;'>
    <li><strong>NIST AI RMF 1.0</strong> (2023): AI Risk Management Framework</li>
    <li><strong>HIPAA Security Rule</strong> (45 CFR 164): Administrative, Physical, Technical Safeguards</li>
    <li><strong>FDA 21 CFR Part 11</strong>: Electronic Records & Signatures (applicable to SaMD, clinical trials)</li>
    <li><strong>ISO 13485:2016</strong>: Medical Devices Quality Management System</li>
    <li><strong>ISO 14971:2019</strong>: Medical Device Risk Management</li>
    <li><strong>IEC 62304</strong>: Medical Device Software Lifecycle</li>
    <li><strong>IEC 81001-5-1</strong>: Health Software & Security (incl. AI/ML)</li>
    <li><strong>NIST SP 800-53 Rev 5</strong>: Security & Privacy Controls</li>
    <li><strong>ICH-GCP E6(R2)</strong>: Good Clinical Practice (clinical trials)</li>
    <li><strong>CMMC 2.0</strong>: Cybersecurity Maturity Model (defense contractors)</li>
    </ul>
    <p style='font-size: 12px; color: #888; margin-top: 10px;'>
    ⚠️ <strong>Disclaimer:</strong> This matrix is informational only and not legal/regulatory advice. 
    Consult qualified compliance professionals for your specific requirements.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# EXPORT REPORT FUNCTIONALITY
# ============================================================================
st.markdown("---")
st.subheader("📥 Export Results")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Generate Markdown report
    def generate_markdown_report():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# 🛡️ HealthSec AI Risk Assessment Report

**Cost of Untrusted AI Calculator | HealthSec Alliance**

Generated: {timestamp}

> **📊 Scenario Explorer:** This report provides illustrative risk scenarios for strategic planning and discussion. 
> Estimates are based on simplified models and industry experience. Actual risk quantification requires detailed organizational assessment.

---

## Executive Summary

**Scenario:** {scenario_name}  
**Trust Maturity Level:** {trust_maturity} of 5

### {'Annual Recoverable Value' if trust_maturity > 0 else 'Annual Cost of Uncertainty (Baseline)'}

# ${results['annual_evsi' if trust_maturity > 0 else 'annual_evpi']:,.0f}

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Baseline Annual Cost | ${results['annual_evpi']:,.0f} |
| Recoverable Value (L{trust_maturity}) | ${results['annual_evsi']:,.0f} |
| Recovery Percentage | {results['recovery_percentage']:.1f}% |
| Uncertainty Reduction | {results['uncertainty_reduction']*100:.0f}% |
| Cost Reduction | {results['cost_reduction']*100:.0f}% |

---

## Input Parameters

| Parameter | Value |
|----------|-------|
| Cost of Failure (Overage) | ${cost_overage:,.0f} |
| Cost of Human Labor/Inefficiency (Underage) | ${cost_underage:,.0f} |
| Annual Decision Volume | {volume:,} |
| Mean Failure Rate (per 1000 decisions) | {mean_demand:.1f} ({mean_demand/10:.2f}% failure rate) |
| Failure Rate Uncertainty (σ per 1000) | {std_demand:.1f} |
| Trust Maturity Level | {trust_maturity} |

---

## Sensitivity Analysis

Impact of ±20% change in key parameters:

| Parameter | Impact on Annual Cost |
|----------|----------------------|"""
        
        for param, value in sorted_sens.items():
            md_content += f"\n| {param} | ${abs(value):,.0f} |"
        
        md_content += "\n\n---\n\n## Recommendations\n\n"
        
        if trust_maturity < 3:
            md_content += """- Consider increasing trust control maturity to Level 3+ for optimal risk reduction
- Implement data provenance tracking and continuous validation
- Establish auditable trust chains for regulatory compliance
"""
        else:
            md_content += f"""- Current trust controls (Level {trust_maturity}) provide strong risk mitigation
- Maintain continuous monitoring and attestation processes
- Document all control activities for compliance audits
"""
        
        md_content += """- Focus on highest-sensitivity parameters identified in analysis
- Regular review and updates to risk assessments (quarterly recommended)
- Engage with HealthSec Alliance for trust stack implementation guidance

---

## About This Analysis

This report was generated using Monte Carlo simulation (10,000 runs) applying the Newsvendor Model adapted for AI risk. The Expected Value of Perfect Information (EVPI) and Expected Value of Sample Information (EVSI) methodologies quantify the financial impact of uncertainty and the value of trust controls.

**Methodology:** Howard, R.A. (1966). "Information Value Theory."

**Frameworks Referenced:** NIST AI RMF, HIPAA Security Rule, FDA 21 CFR Part 11, ISO 13485, IEC 62304, NIST 800-53

---

## Contact

**HealthSec Alliance** | A Big Data Plumbing Initiative

Securing Healthcare • OT • AI at the Intersection of Digital and Physical Safety

Email: info@healthsecalliance.com  
Website: https://healthsecalliance.com

---

⚠️ **DISCLAIMER:** This report is for informational purposes only and does not constitute legal, regulatory, or medical advice. Consult qualified professionals for your specific requirements.
"""
        
        return md_content
    
    # Create download button
    if st.button("📄 Generate Executive Report", type="primary", use_container_width=True):
        md_report = generate_markdown_report()
        st.download_button(
            label="⬇️ Download Markdown Report",
            data=md_report,
            file_name=f"healthsec_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.success("✅ Report generated! Click the button above to download.")

# ============================================================================
# CALL TO ACTION
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 40px; background-color: #1e2130; border-radius: 10px;'>
<h2 style='color: #ffa500;'>Ready to Reduce Your Risk Tax?</h2>
<p style='font-size: 18px; color: #ccc;'>
The HealthSec Alliance helps healthcare and life sciences organizations build trust 
into AI systems from the ground up - with cryptographic provenance, continuous monitoring, 
and compliance-ready documentation.
</p>
<p style='font-size: 16px; margin-top: 20px; color: #ccc;'>
<strong>Contact:</strong> <a href='mailto:info@healthsecalliance.com' style='color: #00ff00; text-decoration: none;'>info@healthsecalliance.com</a>
</p>
<p style='font-size: 16px; margin-top: 10px; color: #ccc;'>
<strong>Website:</strong> <a href='https://healthsecalliance.com' style='color: #00ff00; text-decoration: none;'>healthsecalliance.com</a>
</p>
<p style='font-size: 14px; color: #888; margin-top: 30px;'>
🛡️ <strong>HealthSec Alliance</strong> | A <strong>Big Data Plumbing</strong> Initiative<br>
Securing Healthcare • OT • AI at the Intersection of Digital and Physical Safety
</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
Built with Streamlit | Monte Carlo Simulation (10,000 runs) | 
<a href='https://healthsecalliance.com' style='color: #888; text-decoration: none;'>healthsecalliance.com</a>
</div>
""", unsafe_allow_html=True)


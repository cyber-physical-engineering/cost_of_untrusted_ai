import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from risk_model import SCENARIOS, calculate_risk_with_controls

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Cost of Untrusted AI Calculator",
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
# STREAMLIT UI
# ============================================================================

# Header
st.markdown("<h1 style='text-align: center; color: white;'>🛡️ Cost of Untrusted AI Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-size: 18px;'>A what-if model of the cost of AI uncertainty under assumed control levels</p>", unsafe_allow_html=True)

# Disclaimer banner
st.markdown("""
<div style='background-color: #2d2d3d; padding: 12px 20px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ffa500;'>
<p style='margin: 0; font-size: 13px; color: #ccc;'>
<strong style='color: #ffa500;'>What-if model:</strong> every default is an illustrative placeholder, and the reductions by maturity level are assumptions, not measurements. Replace the inputs with your own data before drawing any conclusion.
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
st.sidebar.subheader("Costs")
cost_overage = st.sidebar.number_input(
    "Cost per failure ($)",
    min_value=1000,
    max_value=100000000,
    value=scenario['cost_overage'],
    step=10000,
    help="Charged for each failure the review capacity did not cover (a lawsuit, a breach, harm)"
)

cost_underage = st.sidebar.number_input(
    "Cost per review ($)",
    min_value=100,
    max_value=1000000,
    value=scenario['cost_underage'],
    step=1000,
    help="Charged for each review slot beyond the actual failures (a manual review that was not needed)"
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
st.sidebar.subheader("Failure rate")
mean_demand = st.sidebar.slider(
    "Mean Failure Rate (per 1000 decisions)",
    min_value=1.0,
    max_value=100.0,
    value=scenario['mean_demand'],
    step=1.0,
    help="Expected failures per 1000 decisions (e.g., 45 = 4.5% failure rate)"
)

std_demand = st.sidebar.slider(
    "Failure rate spread (σ per 1000)",
    min_value=1.0,
    max_value=50.0,
    value=scenario['std_demand'],
    step=1.0,
    help="Standard deviation of the failure rate, per 1,000 decisions"
)

# Control maturity
st.sidebar.markdown("---")
st.sidebar.subheader("Control maturity")
trust_maturity = st.sidebar.select_slider(
    "Control Maturity Level",
    options=[0, 1, 2, 3, 4, 5],
    value=0,
    format_func=lambda x: {
        0: "L0: None (Baseline)",
        1: "L1: Basic Monitoring",
        2: "L2: + Provenance",
        3: "L3: + Attestation",
        4: "L4: + AI RMF practices",
        5: "L5: Defense-in-Depth"
    }[x],
    help="Pick a current or target level; each level applies the assumed reductions"
)

st.sidebar.markdown(f"""
<div style='background-color: #1e2130; padding: 10px; border-radius: 5px; font-size: 12px;'>
<strong>Level {trust_maturity}:</strong><br>
{['No controls - baseline risk', 
  'Basic logging & monitoring', 
  'Data provenance tracking', 
  'Continuous validation & attestation',
  'Practices aligned to NIST AI RMF',
  'Defense-in-depth + real-time intervention'][trust_maturity]}
</div>
<p style='font-size: 10px; color: #666; margin-top: 8px;'>
<em>The reduction percentages are assumptions written into the model, not measurements.</em>
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
            "<div class='subtitle'>Modeled annual cost of AI uncertainty</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='big-red-number' style='color: #00ff00;'>${results['annual_evsi']:,.0f}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='subtitle'>Modeled annual reduction (L{trust_maturity})</div>",
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
        label=f"Modeled reduction (L{trust_maturity})",
        value=f"${results['annual_evsi']:,.0f}",
        delta=f"{results['recovery_percentage']:.1f}% of baseline",
        delta_color="normal"
    )

with col3:
    baseline_std_normalized = results['std_demand'] / 1000.0
    st.metric(
        label="Spread reduction",
        value=f"{results['uncertainty_reduction']*100:.0f}%",
        delta=f"σ: {baseline_std_normalized:.4f} → {results['improved_std']:.4f} (per decision)"
    )

with col4:
    st.metric(
        label="Failure cost reduction",
        value=f"{results['cost_reduction']*100:.0f}%",
        delta="per failure (assumed)"
    )

st.markdown("---")

# ============================================================================
# VISUALIZATION
# ============================================================================
st.subheader("Distributions")

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
        name=f'Level {trust_maturity} assumptions',
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
        annotation_text=f"Level {trust_maturity}: ${results['expected_cost_improved']:,.2f}",
        annotation_position="top right"
    )

fig.update_layout(
    title="Cost per decision: baseline vs. the level's assumptions",
    xaxis_title="Cost per Decision ($)",
    yaxis_title="Count (of 10,000 draws)",
    template="plotly_dark",
    height=400,
    showlegend=True,
    barmode='overlay'
)

st.plotly_chart(fig, width="stretch")

# ============================================================================
# RISK DISTRIBUTION CURVE
# ============================================================================
fig2 = go.Figure()

# Baseline risk events
fig2.add_trace(go.Histogram(
    x=results['demand_scenarios_baseline'],
    nbinsx=50,
    name='Baseline failure rate',
    marker_color='rgba(255, 75, 75, 0.6)',
    histnorm='probability density'
))

# Improved risk events if controls active
if trust_maturity > 0:
    fig2.add_trace(go.Histogram(
        x=results['demand_scenarios_improved'],
        nbinsx=50,
        name=f'Level {trust_maturity} assumptions',
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
            annotation_text=f"Level {trust_maturity} threshold: {results['optimal_static_q_improved']:.3f} ({results['optimal_static_q_improved']*1000:.1f} per 1000)",
            annotation_position="top right"
        )

fig2.update_layout(
    title="Failure rate: baseline vs. the level's assumptions",
    xaxis_title="Failure Rate (per decision, 0-1 scale)",
    yaxis_title="Probability Density",
    template="plotly_dark",
    height=400,
    barmode='overlay'
)

st.plotly_chart(fig2, width="stretch")

# ============================================================================
# INSIGHTS & EXPLANATION
# ============================================================================
st.markdown("---")
st.subheader("Reading the result")

if trust_maturity == 0:
    st.markdown(f"""
<div class='insight-box'>
<h3 style='color: #ffa500;'>The Cost of Uncertainty (Baseline)</h3>
<p style='font-size: 18px;'>
With these inputs, the model puts the annual cost of AI uncertainty at <strong style='color: #ff4b4b;'>${results['annual_evpi']:,.0f}</strong>.
</p>
<p style='font-size: 16px;'>
The model charges two kinds of cost:
</p>
<ul style='font-size: 16px;'>
<li><strong>Failures beyond the review threshold:</strong> ${cost_overage:,} each</li>
<li><strong>Review capacity beyond the actual failures:</strong> ${cost_underage:,} each</li>
</ul>
<p style='font-size: 16px; margin-top: 20px;'>
Move the maturity slider in the sidebar to apply the assumed reductions.
</p>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class='insight-box'>
<h3 style='color: #00ff00;'>Modeled reduction at level {trust_maturity}</h3>
<p style='font-size: 18px;'>
With the level {trust_maturity} assumptions, the model's annual cost falls by <strong style='color: #00ff00;'>${results['annual_evsi']:,.0f}</strong>, which is <strong>{results['recovery_percentage']:.1f}%</strong> of the baseline.
</p>
<p style='font-size: 16px;'>
<strong>What the level changes:</strong>
</p>
<ul style='font-size: 16px;'>
<li><strong>Spread reduction:</strong> {results['uncertainty_reduction']*100:.0f}% (failure rate σ: {results['std_demand']/1000:.4f} → {results['improved_std']:.4f} per decision)</li>
<li><strong>Failure cost reduction:</strong> {results['cost_reduction']*100:.0f}% per failure</li>
<li><strong>Modeled reduction:</strong> ${results['annual_evsi']:,.0f} a year</li>
<li><strong>Baseline cost:</strong> ${results['annual_evpi']:,.0f} → <strong>Improved:</strong> ${results['annual_evpi'] - results['annual_evsi']:,.0f}</li>
</ul>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================
st.markdown("---")
st.subheader("Sensitivity: which input moves the result")

# Calculate sensitivity by varying each parameter ±20%
def calculate_sensitivities():
    sensitivities = {}
    
    # Test cost_overage impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage * 1.2, cost_underage, volume, 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage * 0.8, cost_underage, volume, 0
    )
    sensitivities['Cost per failure'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
    # Test cost_underage impact
    results_high = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage * 1.2, volume, 0
    )
    results_low = calculate_risk_with_controls(
        mean_demand, std_demand, cost_overage, cost_underage * 0.8, volume, 0
    )
    sensitivities['Cost per review'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
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
    sensitivities['Failure rate spread (σ)'] = (results_high['annual_evpi'] - results_low['annual_evpi']) / 2
    
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
        title="Tornado chart: each input moved ±20%",
        xaxis_title="Impact on Annual Cost ($)",
        yaxis_title="",
        template="plotly_dark",
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig_tornado, width="stretch")

with col2:
    # Top 2 drivers
    drivers = "".join(
        f"<li><strong>{param}:</strong> {abs(value/results['annual_evpi']*100):.1f}% impact</li>"
        for param, value in list(sorted_sens.items())[:2]
    )
    if trust_maturity > 0:
        break_even = "Controls costing less than ${:,.0f} a year would pay for themselves under these inputs.".format(results['annual_evsi'])
    else:
        break_even = "Move the maturity slider to see a break-even figure."
    st.markdown(f"""
    <div style='background-color: #1e2130; padding: 20px; border-radius: 10px; min-height: 350px;'>
    <h4 style='color: #ffa500;'>Reading the chart</h4>
    <p style='font-size: 14px;'>
    Each bar shows how a <strong>±20% change</strong> in one input moves the modeled annual cost.
    </p>
    <p style='font-size: 14px; margin-top: 15px;'>
    <strong style='color: #ff4b4b;'>The longest bars are the inputs worth checking first.</strong>
    </p>
    <ul style='font-size: 13px; margin-top: 15px;'>{drivers}</ul>
    <p style='font-size: 13px; margin-top: 15px; color: #888;'>
    <strong>Break-even:</strong><br>
    {break_even}
    </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# THE MATH EXPLAINED
# ============================================================================
with st.expander("How the number is computed"):
    st.markdown("""
    ### The baseline cost (labeled EVPI)
    
    This calculator uses the **Newsvendor Model** from operations research, adapted for AI risk.
    
    **The Core Equation:**
    ```
    EVPI = E[Cost_with_uncertainty] - E[Cost_with_perfect_information]
    ```
    
    **What We're Modeling:**
    - **Failure Rate:** The probability that an AI decision will fail (e.g., 45 failures per 1000 = 4.5% failure rate)
    - **Review threshold:** a fixed share of decisions gets a manual review, set at the critical-ratio quantile
    - **Perfect information:** the review threshold could follow the real failure rate exactly, so the mismatch cost would be zero
    
    **The Simulation:**
    1. We normalize your input (failures per 1000 decisions) to a failure rate per decision (0-1 scale)
    2. We draw 10,000 failure rates from a normal distribution with your mean and spread (fixed seed)
    3. For each draw, we charge each failure beyond the threshold and each unused review slot
    4. We compare that with perfect information, where the mismatch cost is zero
    5. The mean cost per decision, labeled EVPI, times volume is the annual figure
    
    **Trust Maturity Impact:**
    The reduction percentages (15% to 75% on the spread, 10% to 65% on the failure cost) are assumptions
    written into the model. Nothing here measures them. Your own results depend on your controls and your data.
    
    **Key Assumptions:**
    - Failure rates are approximately normally distributed
    - Costs are proportional to failure/intervention rates
    - The maturity level cuts the spread and the failure cost by assumed percentages
    
    **Limitations:**
    - This is a simplified model for strategic planning, not a precise actuarial calculation
    - Replace every default with your own data before using the result
    - Tail risks (rare catastrophic events) may not be fully captured
    
    **References:**
    - Cachon, G. & Terwiesch, C. (2013). *Matching Supply with Demand*. McGraw-Hill.
    - NIST AI Risk Management Framework (2023)
    - Howard, R.A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics*.
    """)

# ============================================================================
# COMPLIANCE & CONTROLS TRACEABILITY
# ============================================================================
with st.expander("Framework references by level"):
    st.markdown("""
    ### Example clauses next to each level
    
    The table lists one example clause from each framework per maturity level. It is a reading aid, not a mapping and not a finding about any system.
    """)
    
    # Create compliance mapping dataframe
    compliance_data = {
        'Control Level': ['L0: Baseline', 'L1: Monitoring', 'L2: Provenance', 'L3: Attestation', 'L4: AI RMF practices', 'L5: Defense-in-Depth'],
        'NIST AI RMF': [
            '❌ No coverage',
            '🟡 GOVERN-1.1 (legal and regulatory requirements)',
            '🟡 MAP-1.1 (context)',
            '🟢 MEASURE-2.1 (validation)',
            '🟢 MANAGE-4.1 (continuous)',
            '🟢 GOVERN, MAP, MEASURE and MANAGE practices in place (assumed)'
        ],
        'HIPAA Security': [
            '❌ No coverage',
            '🟡 §164.308(a)(1) (audit)',
            '🟢 §164.312(b) (audit logs)',
            '🟢 §164.312(c)(1) (integrity)',
            '🟢 §164.308(a)(8) (evaluation)',
            '🟢 Administrative safeguards in place (assumed)'
        ],
        'FDA 21 CFR Part 11': [
            '❌ No coverage',
            '🟡 §11.10(e) (audit trail)',
            '🟢 §11.10(a) (validation)',
            '🟢 §11.10(f) (system checks)',
            '🟢 §11.70 (signature/record)',
            '🟢 Part 11 controls in place (assumed)'
        ],
        'ISO 13485 (MedTech)': [
            '❌ No coverage',
            '🟡 7.3.3 (design inputs)',
            '🟢 7.5.1 (production control)',
            '🟢 7.5.6 (validation)',
            '🟢 8.2.1 (monitoring)',
            '🟢 QMS procedures cover the AI system (assumed)'
        ],
        'NIST 800-53': [
            '❌ No coverage',
            '🟡 AU-2 (audit events)',
            '🟢 CM-3 (configuration mgmt)',
            '🟢 SI-7 (integrity verification)',
            '🟢 RA-5 (vulnerability monitoring)',
            '🟢 Controls from each family in place (assumed)'
        ]
    }
    
    df_compliance = pd.DataFrame(compliance_data)
    
    # Style the dataframe
    st.dataframe(
        df_compliance,
        width="stretch",
        hide_index=True,
        height=280
    )
    
    st.markdown("---")
    
    # Evidence artifacts by level
    st.markdown("### Evidence a reviewer might ask for, by level")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Levels 1 and 2**
        - System activity logs (timestamped)
        - Data lineage documentation
        - Model versioning records
        - Change control logs
        - Training data manifests
        
        **Levels 3 and 4**
        - Cryptographic attestation certificates
        - Continuous validation reports
        - Risk assessment documentation
        - Audit trail a reviewer can check for changes
        - Model cards with provenance
        - Control reports
        """)
    
    with col2:
        st.markdown("""
        **Level 5**
        - Real-time monitoring dashboards
        - Automated incident response logs
        - Access verification records
        - Supply chain integrity reports
        - Regulatory submission packages
        - Executive risk summary reports
        - Third-party audit evidence bundles
        """)
    
    st.markdown("---")
    
    # Framework references
    st.markdown("""
    <div style='background-color: #1e2130; padding: 15px; border-radius: 10px;'>
    <h4 style='color: #ffa500;'>Framework References</h4>
    <ul style='font-size: 13px;'>
    <li><strong>NIST AI RMF 1.0</strong> (2023): AI Risk Management Framework</li>
    <li><strong>HIPAA Security Rule</strong> (45 CFR 164): Administrative, Physical, Technical Safeguards</li>
    <li><strong>FDA 21 CFR Part 11</strong>: electronic records kept under FDA record rules</li>
    <li><strong>ISO 13485:2016</strong>: Medical Devices Quality Management System</li>
    <li><strong>ISO 14971:2019</strong>: Medical Device Risk Management</li>
    <li><strong>IEC 62304</strong>: Medical Device Software Lifecycle</li>
    <li><strong>IEC 81001-5-1</strong>: Health Software & Security</li>
    <li><strong>NIST SP 800-53 Rev 5</strong>: Security & Privacy Controls</li>
    <li><strong>ICH-GCP E6(R3)</strong>: Good Clinical Practice (clinical trials)</li>
    <li><strong>CMMC 2.0</strong>: Cybersecurity Maturity Model Certification (defense contractors)</li>
    </ul>
    <p style='font-size: 12px; color: #888; margin-top: 10px;'>
    <strong>Note:</strong> this table lists example clauses next to each level. It is not legal or regulatory advice, and it makes no finding about any system.
    </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# EXPORT REPORT FUNCTIONALITY
# ============================================================================
st.markdown("---")
st.subheader("Export")

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    # Generate Markdown report
    def generate_markdown_report():
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# AI Risk Scenario Report

**Cost of Untrusted AI Calculator**

Generated: {timestamp}

> **What-if model.** Every input in this report is an illustrative placeholder unless you replaced it with your own data. The reductions by maturity level are assumptions, not measurements.

---

## Summary

**Scenario:** {scenario_name}  
**Control maturity level:** {trust_maturity} of 5

### {'Modeled annual reduction' if trust_maturity > 0 else 'Annual Cost of Uncertainty (Baseline)'}

# ${results['annual_evsi' if trust_maturity > 0 else 'annual_evpi']:,.0f}

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Baseline Annual Cost | ${results['annual_evpi']:,.0f} |
| Modeled reduction (L{trust_maturity}) | ${results['annual_evsi']:,.0f} |
| Reduction as a share of baseline | {results['recovery_percentage']:.1f}% |
| Spread reduction | {results['uncertainty_reduction']*100:.0f}% |
| Failure cost reduction | {results['cost_reduction']*100:.0f}% |

---

## Input Parameters

| Parameter | Value |
|----------|-------|
| Cost per failure | ${cost_overage:,.0f} |
| Cost per review | ${cost_underage:,.0f} |
| Annual Decision Volume | {volume:,} |
| Mean Failure Rate (per 1000 decisions) | {mean_demand:.1f} ({mean_demand/10:.2f}% failure rate) |
| Failure rate spread (σ per 1000) | {std_demand:.1f} |
| Control maturity level | {trust_maturity} |

---

## Sensitivity Analysis

Impact of ±20% change in key parameters:

| Parameter | Impact on Annual Cost |
|----------|----------------------|"""
        
        for param, value in sorted_sens.items():
            md_content += f"\n| {param} | ${abs(value):,.0f} |"
        
        md_content += "\n\n---\n\n## Recommendations\n\n"
        
        if trust_maturity < 3:
            md_content += """- Re-run the model at level 3 or higher to see the assumed reductions
"""
        else:
            md_content += f"""- The level {trust_maturity} assumptions were applied
- Keep records of control activities
"""
        
        md_content += """- Check the inputs with the largest tornado bars first
- Revisit the inputs when your data changes

---

## About This Analysis

This report comes from 10,000 draws of a simulated failure rate (fixed seed) and a newsvendor-style threshold. The baseline cost is labeled EVPI. The cost difference under the chosen maturity level is labeled EVSI; that is this tool's own label for a cost difference under assumed reductions.

**Methodology:** Howard, R.A. (1966). "Information Value Theory."

**Frameworks Referenced:** NIST AI RMF, HIPAA Security Rule, FDA 21 CFR Part 11, ISO 13485, IEC 62304, NIST 800-53

---

**Note:** this report is a what-if model with illustrative defaults. It is not legal, regulatory or medical advice.
"""
        
        return md_content
    
    # Create download button
    if st.button("Generate report", type="primary", width="stretch"):
        md_report = generate_markdown_report()
        st.download_button(
            label="⬇️ Download Markdown Report",
            data=md_report,
            file_name=f"ai_risk_scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            width="stretch"
        )
        st.success("Report generated. Use the download button above.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
Built with Streamlit | 10,000 draws with a fixed seed | MIT License
</div>
""", unsafe_allow_html=True)


# 🚀 Quick Start Guide

> **📊 About This Tool:** This calculator provides illustrative risk scenarios for strategic planning. 
> Use it to explore "what-if" scenarios and support investment discussions. For actual risk quantification, 
> validate assumptions with your organization's data.

## Running Locally

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python3 -m streamlit run app.py
   ```

3. **Open in browser:**
   - The app will automatically open, or navigate to: http://localhost:8501
   - If port 8501 is busy, Streamlit will use 8502, 8503, etc.

## Using the Calculator

### Step 1: Select a Scenario
Choose from pre-configured scenarios or create your own:
- **Radiology AI** - Diagnostic errors with malpractice exposure
- **OT Valve Controller** - Industrial control with physical safety impact
- **Pharmacy Automation** - Drug dispensing with patient safety risk
- **Custom** - Configure your own parameters

### Step 2: Configure Parameters
Adjust in the sidebar:
- **Financial Parameters:** Failure costs (per incident) and manual intervention costs
- **Risk Parameters:** Mean failure rate (failures per 1000 decisions) and uncertainty (σ)
- **Trust Maturity:** Select control level (L0-L5) to see estimated impact of controls

### Step 3: Analyze Results
Review:
- **Big Number:** Annual cost or recoverable value
- **Key Metrics:** Baseline cost, recovery %, uncertainty reduction
- **Charts:** Cost and risk distributions (baseline vs. improved)
- **Sensitivity Analysis:** Top risk drivers (tornado diagram)
- **Compliance Matrix:** Framework mappings and evidence artifacts

### Step 4: Export Report
Click "Generate Executive Report" to create a professional HTML report for:
- Board presentations
- Audit documentation
- Client proposals
- Internal risk assessments

## Understanding Trust Maturity Levels

- **L0: None (Baseline)** - No controls, baseline risk
- **L1: Basic Monitoring** - Logging and basic audit trails
- **L2: + Provenance** - Data lineage and model versioning
- **L3: + Attestation** - Continuous validation and attestation
- **L4: + NIST AI RMF** - Full framework compliance
- **L5: Defense-in-Depth** - Real-time intervention + zero-trust

Each level reduces uncertainty (15-75% estimated) and failure costs (10-65% estimated).

*Note: These percentages are illustrative estimates based on industry experience. Actual results depend on implementation quality and organizational context.*

## Deploying to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: HealthSec Cost of Untrusted AI Calculator"
   git remote add origin https://github.com/YOUR_USERNAME/cost-of-untrusted-ai.git
   git push -u origin main
   ```

2. **Deploy:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

## Customization Tips

### Changing Recovery Rates by Trust Level
In `app.py`, modify the `uncertainty_reduction` and `failure_cost_reduction` dictionaries (around lines 90-105):
```python
uncertainty_reduction = {
    0: 0.0,   # No controls
    1: 0.15,  # Your custom %
    # ... etc
}
```

### Adding New Scenarios
In `app.py`, add to the `SCENARIOS` dictionary (starting around line 140):
```python
"Your Scenario Name": {
    "mean_demand": 50.0,
    "std_demand": 20.0,
    "cost_overage": 1000000,
    "cost_underage": 10000,
    "volume": 5000,
    "description": "Your scenario description"
}
```

### Customizing the Compliance Matrix
Add rows to the `compliance_data` dictionary in the compliance expander section (around line 520):
```python
'Your Framework': [
    '❌ No coverage',
    '🟡 Partial (control ID)',
    # ... for each level
]
```

### Updating Branding
- **Colors:** Modify the `<style>` section at the top of `app.py`
- **Contact Info:** Update footer and CTA sections (search for "contact@healthsecalliance.com")
- **Logos:** Add image files and reference with `st.image()`

## Troubleshooting

### Port Already in Use
If you see "Address already in use", either:
- Stop the other Streamlit process
- Or Streamlit will automatically use the next available port (8502, 8503, etc.)

### Missing Dependencies
```bash
pip3 install --upgrade streamlit numpy pandas plotly
```

### Python Version
Requires Python 3.8+. Check your version:
```bash
python3 --version
```

## Using in Presentations

### Taking Screenshots
The app includes professional dark-mode styling perfect for screenshots. Key areas:
- **Big number display** - Center of page (baseline or recoverable value)
- **Metrics cards** - Top row with 4 key metrics
- **Charts** - Cost distribution and risk distribution comparisons
- **Tornado diagram** - Sensitivity analysis
- **Compliance matrix** - Framework traceability table

### Exporting Data
Use the **"Generate Executive Report"** button to create:
- Professional HTML report with all metrics
- Charts and visualizations embedded
- Full methodology documentation
- Timestamped for audit trails

You can also add custom exports:
```python
import json

# Add after calculations
if st.button("📥 Export Raw Data"):
    export_data = {
        'scenario': scenario_name,
        'annual_evpi': results['annual_evpi'],
        'annual_evsi': results['annual_evsi'],
        # ... more fields
    }
    st.download_button(
        label="Download JSON",
        data=json.dumps(export_data, indent=2),
        file_name="risk_data.json",
        mime="application/json"
    )
```

## Key Differences from v1.0

### What's New in v2.0
1. **Trust Maturity Model** - 6 levels with graduated control impacts
2. **EVSI Calculation** - Shows actual recoverable value, not just theoretical
3. **Sensitivity Analysis** - Tornado diagrams + break-even analysis
4. **Compliance Matrix** - Maps to 8+ regulatory frameworks
5. **Executive Reports** - One-click HTML export
6. **Improved Visualizations** - Baseline vs. improved overlays

### Migration Notes
- Old "40% recovery" is now dynamic based on trust level
- Results now show both EVPI (baseline) and EVSI (with controls)
- All exports include compliance documentation

## Support

For issues or questions:
- 📧 Email: contact@healthsecalliance.com
- 🐛 GitHub Issues: https://github.com/YOUR_USERNAME/cost-of-untrusted-ai/issues

---

**Built by HealthSec Alliance | Big Data Plumbing**


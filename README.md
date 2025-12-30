# 🛡️ Cost of Untrusted AI Calculator

**A risk scenario explorer for healthcare, life sciences, medtech, and defense sectors**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

> **📊 About This Tool:** This calculator provides illustrative risk scenarios for strategic planning and discussion. 
> It uses established decision theory methodology (EVPI/EVSI) to help organizations understand the potential 
> financial impact of AI uncertainty. Estimates are based on simplified models; actual risk quantification 
> requires detailed organizational assessment.

---

## 🎯 What Is This?

The **Cost of Untrusted AI Calculator** is a Monte Carlo simulation tool that helps estimate the financial impact of operating AI systems without proper trust verification and compliance infrastructure. It provides CISOs, Chief Risk Officers, and compliance professionals with scenario-based analysis to support strategic planning and investment decisions.

Built by the **HealthSec Alliance**, this calculator helps quantify the potential "Risk Tax" organizations pay when running AI systems with uncertainty—and demonstrates the estimated ROI of trust controls.

---

## ✨ Key Features (v2.0)

### 🎚️ **Trust Maturity Modeling**
- Interactive 6-level trust maturity scale (L0-L5)
- EVPI (baseline) vs. EVSI (with controls) comparison
- Real-time calculation of uncertainty and cost reduction
- Visual comparison of baseline vs. improved risk distributions

### 📊 **Sensitivity Analysis**
- Tornado diagram showing top risk drivers
- Impact analysis: ±20% parameter variation
- Break-even analysis for trust stack investments
- Identifies highest-leverage areas for risk reduction

### 🔒 **Compliance Traceability Matrix**
- Maps trust controls to regulatory frameworks:
  - **NIST AI RMF 1.0** (AI Risk Management Framework)
  - **HIPAA Security Rule** (45 CFR 164)
  - **FDA 21 CFR Part 11** (Electronic Records & Signatures)
  - **ISO 13485** (Medical Devices QMS)
  - **IEC 62304** (Medical Device Software)
  - **NIST 800-53** (Security & Privacy Controls)
  - **ICH-GCP E6(R2)** (Clinical Trials)
  - **CMMC 2.0** (Defense Contractors)
- Evidence artifact documentation by maturity level
- Audit-ready compliance documentation

### 📥 **Executive Report Export**
- One-click HTML report generation
- Professional formatting for board presentations
- Includes all metrics, charts, and recommendations
- Timestamped with full methodology documentation

### 🎨 **Pre-configured Scenarios**
- Radiology AI (Diagnostic Errors)
- OT Valve Controller (ICS/SCADA)
- Pharmacy Automation (Drug Dispensing)
- Custom scenario builder

---

## 💡 Why Does This Matter?

When AI systems operate in high-stakes environments—healthcare diagnostics, clinical trials, medical devices, industrial control systems—organizations face two types of costs:

1. **Over-trust failures:** When AI makes errors leading to lawsuits, breaches, or physical harm
2. **Under-trust inefficiency:** When humans must intervene because AI isn't trusted, wasting resources

The gap between your current state and "perfect information" is measurable. That gap is the **EVPI (Expected Value of Perfect Information)**—the annual cost of uncertainty. The value of **trust controls** is measured as **EVSI (Expected Value of Sample/Improved Information)**.

---

## 🧮 The Math: EVPI/EVSI with Newsvendor Model

This calculator adapts the classical **Newsvendor Model** from operations research to AI risk management.

### Core Concept

- **Inventory → Autonomy:** How much should you trust the AI to act independently?
- **Demand → Risk Events:** How many failures or edge cases will occur?
- **Overage Cost → Failure Cost:** The cost when AI is over-trusted and fails (lawsuit, breach, harm)
- **Underage Cost → Inefficiency Cost:** The cost when AI is under-trusted and humans must intervene

### The Calculation

```
EVPI = E[Cost_Baseline] - E[Cost_Perfect_Information]
EVSI = E[Cost_Baseline] - E[Cost_With_Controls]
```

Where:
- **Baseline:** Current state (no trust controls)
- **With Controls:** Improved state (trust maturity levels 1-5)
- **Perfect Information:** Theoretical maximum (L5 approaches this asymptote)

### Trust Controls Impact

Each maturity level reduces (estimates based on industry experience):
- **Uncertainty (σ):** 15-75% reduction in AI volatility
- **Failure Costs:** 10-65% reduction through early detection and intervention

*Note: These percentages are illustrative estimates. Actual results depend on implementation quality, organizational context, and specific AI system characteristics.*

### Monte Carlo Simulation

We run **10,000 scenarios** to model:
1. Baseline risk distributions (failure rates normalized per 1000 decisions)
2. Improved distributions with trust controls
3. Expected costs across all scenarios
4. Sensitivity to key parameters

### Key Assumptions

- Failure rates are approximately normally distributed
- Costs are proportional to failure/intervention rates
- Trust controls reduce uncertainty and failure impact progressively

### Limitations

- This is a simplified model for strategic planning, not a precise actuarial calculation
- Actual failure rates and costs should be validated with organizational data
- Tail risks (rare catastrophic events) may not be fully captured

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/cost-of-untrusted-ai.git
   cd cost-of-untrusted-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally:**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

---

## 🌐 Deploy to Streamlit Cloud

1. Push this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select this repository
5. Click "Deploy"

Your app will be live in ~45 seconds with a public URL.

---

## 🎨 Features

- **Trust Maturity Slider:** 6-level control maturity scale with real-time EVSI calculation
- **Pre-configured Scenarios:** Radiology AI, OT Valve Controllers, Pharmacy Automation, and Custom
- **Interactive Risk Modeling:** Adjust financial parameters and AI volatility in real-time
- **Monte Carlo Simulation:** 10,000-run simulation for statistical rigor
- **Sensitivity Analysis:** Tornado diagrams showing top risk drivers and break-even points
- **Compliance Matrix:** Traceability to NIST AI RMF, HIPAA, FDA, ISO 13485, and defense frameworks
- **Executive Reports:** One-click HTML export for board and audit presentations
- **Professional Visualizations:** Plotly-powered interactive charts comparing baseline vs. improved
- **Dark Mode Design:** High-contrast, professional aesthetic for executive presentations
- **Explainable Math:** Built-in explanations of EVPI/EVSI methodology with academic references

---

## 📊 Use Cases

### For CISOs
- Quantify cyber risk exposure from unverified AI systems in dollars
- Justify security budget with ROI calculations
- Demonstrate value of trust controls to executive leadership

### For Chief Risk/Regulatory Officers
- Map trust controls to compliance frameworks (HIPAA, FDA, ISO, NIST)
- Generate audit-ready documentation
- Assess compliance gaps and remediation priorities

### For Compliance Consultants
- Demonstrate ROI of trust infrastructure to clients
- Create professional reports for proposals and assessments
- Tailor scenarios to client-specific use cases

### For Product Security Teams (MedTech/Clinical Trials/Defense)
- Justify budgets for AI safety and monitoring systems
- Assess risk across medical device portfolios
- Support regulatory submissions with quantified risk data

### For Executives & Board Members
- Understand the hidden "Risk Tax" of AI without verification
- See clear ROI for trust stack investments
- Make data-driven decisions on AI governance

---

## 🏥 HealthSec Alliance

The **HealthSec Alliance** is a strategic collective focused on securing the intersection of:
- **Healthcare Systems** (EHR, diagnostics, patient data)
- **Operational Technology** (ICS/SCADA, medical devices, building systems)
- **Artificial Intelligence** (ML models, automation, decision support)

We help hospitals, life sciences companies, and defense contractors prevent physical harm from digital systems through:
- ✅ Cryptographic provenance tracking for AI training data
- ✅ Continuous behavioral monitoring and attestation
- ✅ Compliance-ready documentation (HIPAA, FDA, GxP)
- ✅ Secure data flows across the health ecosystem

**Contact:** [info@healthsecalliance.com](mailto:info@healthsecalliance.com)

---

## 📚 References

- Cachon, G. & Terwiesch, C. (2013). *Matching Supply with Demand: An Introduction to Operations Management*. McGraw-Hill.
- Howard, R.A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics*, SSC-2(1), 22-26.
- NIST AI Risk Management Framework (AI RMF 1.0), January 2023.
- FDA Guidance on Software as a Medical Device (SaMD), 2023.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

---

## ⭐ Support

If this tool helps you quantify AI risk for your organization, please:
- ⭐ Star this repo
- 📢 Share with your network
- 🐛 Report bugs or suggest features via Issues

---

**Built with ❤️ by Big Data Plumbing


# Quick start

Python 3.12 or later.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

## Using it

1. Pick a scenario in the sidebar, or stay on Custom. Every default is an illustrative placeholder.
2. Edit the inputs: mean failure rate and spread (per 1,000 decisions), cost per failure, cost per review, annual volume.
3. Move the maturity slider (0 to 5) to apply the assumed reductions and compare the two distributions.
4. Read the tornado chart for which input moves the result most.
5. Generate and download the Markdown report.

## Changing the model

- The reductions by level are the two dictionaries at the top of `calculate_risk_with_controls` in `risk_model.py`.
- The presets are the `SCENARIOS` dictionary in `risk_model.py`.
- The framework table is `compliance_data` in `app.py`.

## Tests

```bash
pip install pytest
pytest -q
```

Fifteen tests: the model (threshold, failure-cost effect, cost falling with maturity, annual arithmetic) and an AppTest run of every preset plus the report.

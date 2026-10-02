# Cost of Untrusted AI Calculator

A Streamlit what-if calculator. It samples an AI failure rate, applies a newsvendor-style threshold from operations research, and shows how assumed control levels change an illustrative annual cost. Every default is a placeholder, not sourced data.

**Status: prototype.** 15 tests pass (pytest on the model, Streamlit's AppTest on the app), and the app starts headless (October 2, 2026; Python 3.12.15, Apple Silicon Mac).

[![CI](https://github.com/cyber-physical-engineering/cost_of_untrusted_ai/actions/workflows/ci.yml/badge.svg)](https://github.com/cyber-physical-engineering/cost_of_untrusted_ai/actions/workflows/ci.yml)

James Thornton set the architecture and requirements. The code was written with AI-assisted development in late 2025. The tests and checks were re-run in October 2026.

## What it does

- Draws 10,000 failure-rate values from a normal distribution with a fixed seed, clipped to 0 and 1. Results repeat exactly from run to run.
- Applies the newsvendor critical-ratio rule (Cachon and Terwiesch, 2013). The threshold is the quantile at failure cost divided by failure cost plus review cost. Failures beyond the threshold cost one failure each; review capacity beyond the actual failures costs one review each. The mean mismatch cost per decision, times annual volume, is the headline figure. The app labels it EVPI.
- A 0 to 5 control-maturity slider applies assumed reductions: the spread of the failure rate falls 15% to 75%, and the failure cost falls 10% to 65%. The cost difference is shown as the modeled reduction. The code and the report notes label it EVSI; that is the repo's own term for a cost difference, not sample information in the decision-theory sense.
- Shows the two distributions, a tornado chart of plus or minus 20% swings on the four inputs, a break-even line, and a Markdown report.
- Ships three preset scenarios (radiology AI, an industrial valve controller, pharmacy dispensing) and a custom one. Every input is editable, and every default is illustrative.
- Shows a static table of example clauses next to each maturity level. The clauses come from NIST AI RMF 1.0, the HIPAA Security Rule, 21 CFR Part 11, ISO 13485 and NIST SP 800-53. The table is informational, not a compliance mapping.

## Quick start

Python 3.12 or later.

```bash
git clone https://github.com/cyber-physical-engineering/cost_of_untrusted_ai.git
cd cost_of_untrusted_ai
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

Run the tests:

```bash
pip install pytest
pytest -q
```

The model lives in `risk_model.py`, which `app.py` imports. `tests/test_risk_model.py` checks four things: the threshold equals the critical-ratio quantile and sits above zero; the failure cost changes the result; the cost falls as maturity rises; the annual figure equals cost per decision times volume. `tests/test_app.py` runs every preset in AppTest and builds the report.

## Reading the numbers

The dollar figures are outputs of illustrative inputs. They show how the model behaves when an input moves; they are not estimates of anyone's costs. To use the model for your own case, replace every input with your own data and treat the reductions by maturity level as assumptions to argue about.

## Limits

- No input is sourced. The preset rates, costs and volumes are placeholders.
- The reductions by maturity level are assumptions written into the code, not measurements.
- "EVSI" is the repo's own label for a cost difference.
- The framework table lists example clauses. It makes no finding about any system.
- The seed is fixed, so the Recalculate button repeats the same numbers.
- The report is Markdown and carries no charts.
- The app runs on your machine. There is no hosted instance.

## References

- Cachon, G. and Terwiesch, C. (2013). *Matching Supply with Demand: An Introduction to Operations Management.* McGraw-Hill.
- Howard, R. A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics*, SSC-2(1), 22-26.
- NIST AI 100-1, *AI Risk Management Framework (AI RMF 1.0)*, January 2023.

## License

MIT. See [LICENSE](LICENSE).

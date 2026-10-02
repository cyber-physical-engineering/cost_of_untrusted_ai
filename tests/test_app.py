"""Smoke test: the app runs every preset and builds the report without errors."""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from risk_model import SCENARIOS

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.mark.parametrize("name", list(SCENARIOS))
def test_each_scenario_runs(name: str) -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    at.sidebar.selectbox[0].set_value(name)
    at.run()
    assert not at.exception


def test_report_button_builds_a_report() -> None:
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    at.button[0].click()
    at.run()
    assert not at.exception

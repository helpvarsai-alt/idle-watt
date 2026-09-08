from __future__ import annotations

import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from data.synthetic import generate_synthetic_usage
from detector import classify_utilization
from estimator import (
    UnknownMicroarchitectureError,
    UnknownRegionCodeError,
    estimate_resource_impacts,
    kg_co2_to_miles_driven,
)
from ingest.loader import IngestValidationError, load_usage_csv
from simulator import simulate_cleanup


def _base_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "resource_id": "r-1",
                "resource_name": "demo",
                "microarchitecture": "Intel Coffee Lake",
                "region_code": "US_NATIONAL_AVG",
                "vcpu_count": 4,
                "memory_gb": 16,
                "storage_tb": 0.5,
                "avg_cpu_utilization": 0.0,
                "hours_running": 24,
                "hourly_cost_usd": 0.2,
            }
        ]
    )


def test_idle_draw_nonzero_and_below_full_load() -> None:
    idle_df = _base_df()
    full_df = _base_df().assign(avg_cpu_utilization=1.0)
    idle = estimate_resource_impacts(classify_utilization(idle_df)).iloc[0]
    full = estimate_resource_impacts(classify_utilization(full_df)).iloc[0]
    assert idle["cpu_watts"] > 0
    assert idle["cpu_watts"] < full["cpu_watts"]


def test_invalid_utilization_rejected() -> None:
    bad_df = _base_df().assign(avg_cpu_utilization=1.2)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad.csv"
        bad_df.to_csv(p, index=False)
        try:
            load_usage_csv(p)
        except IngestValidationError:
            pass
        else:
            raise AssertionError("Expected IngestValidationError for invalid utilization")


def test_unknown_coefficients_raise_errors() -> None:
    bad_region = _base_df().assign(region_code="UNKNOWN_REGION")
    try:
        estimate_resource_impacts(classify_utilization(bad_region))
    except UnknownRegionCodeError:
        pass
    else:
        raise AssertionError("Expected UnknownRegionCodeError")

    bad_arch = _base_df().assign(microarchitecture="Unknown CPU")
    try:
        estimate_resource_impacts(classify_utilization(bad_arch))
    except UnknownMicroarchitectureError:
        pass
    else:
        raise AssertionError("Expected UnknownMicroarchitectureError")


def test_pipeline_runs_on_synthetic() -> None:
    df = generate_synthetic_usage(n_resources=50, seed=42)
    result = estimate_resource_impacts(classify_utilization(df))
    sim = simulate_cleanup(result)
    assert len(result) == 50
    assert sim["before"]["kwh"] >= 0


def test_cleanup_simulation_bounds() -> None:
    df = generate_synthetic_usage(n_resources=50, seed=42)
    result = estimate_resource_impacts(classify_utilization(df))
    sim = simulate_cleanup(result)

    for key in ["kwh", "kg_co2e", "usd"]:
        assert sim["saved"][key] >= 0
        assert sim["after"][key] <= sim["before"][key]
        assert sim["after"][key] >= 0


def test_miles_conversion_exact_factor() -> None:
    assert kg_co2_to_miles_driven(1.0) == 2.5


if __name__ == "__main__":
    tests = [
        test_idle_draw_nonzero_and_below_full_load,
        test_invalid_utilization_rejected,
        test_unknown_coefficients_raise_errors,
        test_pipeline_runs_on_synthetic,
        test_cleanup_simulation_bounds,
        test_miles_conversion_exact_factor,
    ]
    for test in tests:
        test()
    print(f"Ran {len(tests)} tests successfully.")

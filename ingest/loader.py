from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "resource_id",
    "resource_name",
    "microarchitecture",
    "region_code",
    "vcpu_count",
    "memory_gb",
    "storage_tb",
    "avg_cpu_utilization",
    "hours_running",
    "hourly_cost_usd",
]


class IngestValidationError(ValueError):
    """Raised when usage CSV validation fails."""


def load_usage_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_usage_df(df)
    return df


def validate_usage_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise IngestValidationError(f"Missing required columns: {missing}")

    duplicates = df[df["resource_id"].duplicated()]["resource_id"].tolist()
    if duplicates:
        raise IngestValidationError(f"Duplicate resource_id values found: {duplicates}")

    util = df["avg_cpu_utilization"]
    if ((util < 0) | (util > 1)).any():
        bad = df[(util < 0) | (util > 1)][["resource_id", "avg_cpu_utilization"]]
        raise IngestValidationError(
            "avg_cpu_utilization must be within [0, 1]. Offending rows: "
            f"{bad.to_dict(orient='records')}"
        )

    if (df["vcpu_count"] <= 0).any():
        bad = df[df["vcpu_count"] <= 0][["resource_id", "vcpu_count"]]
        raise IngestValidationError(
            "vcpu_count must be > 0. Offending rows: "
            f"{bad.to_dict(orient='records')}"
        )

    if (df["hours_running"] < 0).any():
        bad = df[df["hours_running"] < 0][["resource_id", "hours_running"]]
        raise IngestValidationError(
            "hours_running must be >= 0. Offending rows: "
            f"{bad.to_dict(orient='records')}"
        )

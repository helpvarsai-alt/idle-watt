from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class WasteThresholds:
    ghost_max_utilization: float = 0.03
    underutilized_max_utilization: float = 0.20


CATEGORY_GHOST = "ghost"
CATEGORY_UNDERUTILIZED = "underutilized"
CATEGORY_HEALTHY = "healthy"


def classify_utilization(
    df: pd.DataFrame,
    thresholds: WasteThresholds = WasteThresholds(),
) -> pd.DataFrame:
    if thresholds.ghost_max_utilization > thresholds.underutilized_max_utilization:
        raise ValueError("ghost_max_utilization cannot exceed underutilized_max_utilization")

    result = df.copy()
    util = result["avg_cpu_utilization"]

    result["waste_category"] = CATEGORY_HEALTHY
    result.loc[util <= thresholds.underutilized_max_utilization, "waste_category"] = CATEGORY_UNDERUTILIZED
    result.loc[util <= thresholds.ghost_max_utilization, "waste_category"] = CATEGORY_GHOST
    return result

from __future__ import annotations

"""Synthetic usage generator for dashboard demos.

Utilization bands mirror published ranges discussed in infrastructure-efficiency research:
- ghost: 0-3%
- underutilized: 5-25%
- healthy: 40-75%

Rationale citation: studies report single-application servers commonly run around 5-15% utilization,
with broader observed utilization ranges around 10-50% across large server populations.
These ranges are used only to shape synthetic demo data and do not alter any environmental coefficients.
"""

import random

import pandas as pd

from data.coefficients import CARBON_INTENSITY_KG_PER_KWH, CPU_POWER_COEFFICIENTS


def generate_synthetic_usage(n_resources: int = 50, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)

    categories = [
        ("GHOST", 0.00, 0.03, max(1, n_resources // 3)),
        ("UNDERUTILIZED", 0.05, 0.25, max(1, n_resources // 3)),
    ]
    healthy_count = n_resources - sum(item[3] for item in categories)
    categories.append(("HEALTHY", 0.40, 0.75, healthy_count))

    microarchitectures = list(CPU_POWER_COEFFICIENTS.keys())
    regions = list(CARBON_INTENSITY_KG_PER_KWH.keys())

    rows = []
    idx = 1
    for label, util_min, util_max, count in categories:
        for _ in range(count):
            rows.append(
                {
                    "resource_id": f"demo-{idx:04d}",
                    "resource_name": f"[{label}] demo-instance-{idx:04d}",
                    "microarchitecture": rng.choice(microarchitectures),
                    "region_code": rng.choice(regions),
                    "vcpu_count": rng.choice([2, 4, 8, 16, 32]),
                    "memory_gb": rng.choice([8, 16, 32, 64, 128]),
                    "storage_tb": rng.choice([0.1, 0.25, 0.5, 1.0, 2.0]),
                    "avg_cpu_utilization": round(rng.uniform(util_min, util_max), 4),
                    "hours_running": rng.choice([24, 72, 168, 360, 720]),
                    "hourly_cost_usd": round(rng.uniform(0.05, 2.5), 4),
                }
            )
            idx += 1

    rng.shuffle(rows)
    return pd.DataFrame(rows)

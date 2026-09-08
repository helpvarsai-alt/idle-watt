from __future__ import annotations

import pandas as pd

from estimator import kg_co2_to_miles_driven


def simulate_cleanup(df: pd.DataFrame) -> dict:
    before = {
        "kwh": float(df["facility_energy_kwh"].sum()),
        "kg_co2e": float(df["carbon_kg_co2e"].sum()),
        "usd": float(df["cost_usd"].sum()),
    }

    reduction_factor = df["waste_category"].map(
        {
            "ghost": 1.0,
            # Modeling assumption for simulator scenario only: rightsizing underutilized resources by 50%.
            "underutilized": 0.5,
            "healthy": 0.0,
        }
    )

    saved_kwh = float((df["facility_energy_kwh"] * reduction_factor).sum())
    saved_kg = float((df["carbon_kg_co2e"] * reduction_factor).sum())
    saved_usd = float((df["cost_usd"] * reduction_factor).sum())

    after = {
        "kwh": before["kwh"] - saved_kwh,
        "kg_co2e": before["kg_co2e"] - saved_kg,
        "usd": before["usd"] - saved_usd,
    }

    saved = {
        "kwh": max(saved_kwh, 0.0),
        "kg_co2e": max(saved_kg, 0.0),
        "usd": max(saved_usd, 0.0),
        "miles_driven_equivalent": kg_co2_to_miles_driven(max(saved_kg, 0.0)),
    }

    return {"before": before, "after": after, "saved": saved}

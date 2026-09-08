from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import streamlit as st

from data.coefficients import (
    CARBON_INTENSITY_KG_PER_KWH,
    CPU_POWER_COEFFICIENTS,
    MEMORY_KWH_PER_GB_HOUR,
    PASSENGER_VEHICLE_KG_CO2_PER_MILE,
    PUE,
    SSD_STORAGE_KWH_PER_TB_HOUR,
)
from data.synthetic import generate_synthetic_usage
from detector import classify_utilization
from estimator import estimate_resource_impacts
from ingest.loader import IngestValidationError, validate_usage_df
from simulator import simulate_cleanup


st.set_page_config(page_title="IdleWatt", layout="wide")
st.title("IdleWatt: Cloud Waste to Energy & Carbon")

uploaded = st.file_uploader("Upload cloud usage CSV", type=["csv"])
using_synthetic = uploaded is None

if using_synthetic:
    st.warning(
        "Synthetic demo data in use (not a real cloud bill). Upload your CSV to analyze real usage.",
        icon="⚠️",
    )
    raw_df = generate_synthetic_usage()
else:
    raw_df = pd.read_csv(io.BytesIO(uploaded.getvalue()))

try:
    validate_usage_df(raw_df)
    classified = classify_utilization(raw_df)
    estimated = estimate_resource_impacts(classified)
    simulation = simulate_cleanup(estimated)
except (IngestValidationError, ValueError, KeyError) as exc:
    st.error(f"Input validation/estimation error: {exc}")
    st.stop()

with st.expander("About the numbers on this page", expanded=False):
    st.markdown("### CPU power coefficients (watts per vCPU)")
    st.table(
        pd.DataFrame(
            [
                {
                    "microarchitecture": k,
                    "min_watts_per_vcpu": v["min_watts_per_vcpu"],
                    "max_watts_per_vcpu": v["max_watts_per_vcpu"],
                    "source": v["source"],
                }
                for k, v in CPU_POWER_COEFFICIENTS.items()
            ]
        )
    )

    st.markdown("### Memory and storage coefficients")
    st.table(
        pd.DataFrame(
            [
                {
                    "component": "memory",
                    "value": MEMORY_KWH_PER_GB_HOUR,
                    "unit": "kWh per GB-hour",
                    "source": "Cloud Carbon Footprint methodology (average of memory manufacturer published values), cited in arXiv:2510.26413",
                },
                {
                    "component": "ssd_storage",
                    "value": SSD_STORAGE_KWH_PER_TB_HOUR,
                    "unit": "kWh per TB-hour",
                    "source": "Cloud Carbon Footprint methodology, derived from the 2016 US Data Center Usage Report, cited in arXiv:2510.26413",
                },
            ]
        )
    )

    st.markdown("### Grid carbon intensity (kg CO2e per kWh)")
    st.table(
        pd.DataFrame(
            [
                {
                    "region_code": code,
                    "region_name": v["region_name"],
                    "kg_co2_per_kwh": v["kg_co2_per_kwh"],
                    "source": v["source"],
                }
                for code, v in CARBON_INTENSITY_KG_PER_KWH.items()
            ]
        )
    )

    st.markdown(
        f"- **PUE**: {PUE} (disclosed round mid-range estimate from Uptime Institute industry-average band ~1.5–1.6, not facility-specific)."
    )
    st.markdown(
        f"- **Passenger vehicle factor**: {PASSENGER_VEHICLE_KG_CO2_PER_MILE} kg CO2/mile (EPA Greenhouse Gas Emissions from a Typical Passenger Vehicle)."
    )

before = simulation["before"]
after = simulation["after"]
saved = simulation["saved"]

c1, c2, c3 = st.columns(3)
c1.metric("Total energy (kWh)", f"{before['kwh']:,.2f}", delta=f"-{saved['kwh']:,.2f} if cleaned")
c2.metric("Total emissions (kg CO2e)", f"{before['kg_co2e']:,.2f}", delta=f"-{saved['kg_co2e']:,.2f} if cleaned")
c3.metric("Total cost (USD)", f"${before['usd']:,.2f}", delta=f"-${saved['usd']:,.2f} if cleaned")

st.subheader("Cleanup impact equivalence")
st.info(
    f"CO2 avoided is equivalent to about {saved['miles_driven_equivalent']:,.1f} passenger-vehicle miles driven "
    f"(EPA factor: {PASSENGER_VEHICLE_KG_CO2_PER_MILE} kg CO2 per mile)."
)

bar_df = estimated.groupby("waste_category", as_index=False)["cost_usd"].sum()
bar = px.bar(bar_df, x="waste_category", y="cost_usd", title="Cost by waste category")
st.plotly_chart(bar, use_container_width=True)

scatter = px.scatter(
    estimated,
    x="avg_cpu_utilization",
    y="carbon_kg_co2e",
    size="facility_energy_kwh",
    color="waste_category",
    hover_data=["resource_id", "resource_name", "region_code", "microarchitecture"],
    title="Utilization vs emissions (bubble size = kWh)",
)
st.plotly_chart(scatter, use_container_width=True)

st.subheader("Resource details")
st.dataframe(estimated.sort_values(["waste_category", "carbon_kg_co2e"], ascending=[True, False]), use_container_width=True)

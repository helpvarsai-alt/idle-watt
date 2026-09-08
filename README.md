# IdleWatt

IdleWatt translates cloud infrastructure waste from a cost story into an energy/carbon story.

## Why this matters

- Research summarized by NRDC and Microsoft-sourced discussions indicates idle server draw is often around **60-90% of peak power**, so "idle" still burns substantial energy.
- Industry reporting (Flexera/Harness) often cites roughly **27-29% cloud spend as waste**, showing major cleanup opportunity.

These figures motivate this project but are **not** used as direct calculation coefficients.

## What IdleWatt does

- Ingests resource usage CSV records.
- Flags each resource as `ghost`, `underutilized`, or `healthy` based on transparent CPU-utilization thresholds.
- Estimates energy (kWh), emissions (kg CO2e), and cost.
- Simulates cleanup impact (terminate ghost resources; rightsize underutilized resources).
- Visualizes everything in a Streamlit dashboard.

## Input schema

Required CSV columns:

- `resource_id`
- `resource_name`
- `microarchitecture`
- `region_code`
- `vcpu_count`
- `memory_gb`
- `storage_tb`
- `avg_cpu_utilization` (0.0-1.0)
- `hours_running`
- `hourly_cost_usd`

## Coefficients and sources

### CPU power coefficients (watts per vCPU)

| microarchitecture | min_watts_per_vcpu | max_watts_per_vcpu | source |
|---|---:|---:|---|
| Intel Coffee Lake | 1.14 | 5.42 | SPECpower_ssj2008 (2022-03-01 release), via cloud-carbon-footprint/ccf-coefficients tool README example output |
| AMD EPYC 7763v (3rd Gen) | 0.434 | 1.948 | SPECpower-derived, reported in Bras et al., "Environmental Impact of CI/CD Pipelines" (arXiv:2510.26413), citing Cloud Carbon Footprint methodology |

Formula:

`watts = (min_watts_per_vcpu + utilization_fraction * (max-min)) * vcpu_count`

### Memory and storage energy

| component | value | unit | source |
|---|---:|---|---|
| memory | 0.000392 | kWh per GB-hour | Cloud Carbon Footprint methodology (average of memory manufacturer published values), cited in arXiv:2510.26413 |
| ssd_storage | 0.0012 | kWh per TB-hour | Cloud Carbon Footprint methodology, derived from the 2016 US Data Center Usage Report, cited in arXiv:2510.26413 |

### Grid carbon intensity (kg CO2e per kWh)

| region_code | region_name | kg_co2_per_kwh | source |
|---|---|---:|---|
| US_NATIONAL_AVG | United States (national average, 2022 gen.) | 0.3733 | EPA Greenhouse Gas Equivalencies Calculator, Calculations & References page (epa.gov/energy), citing EPA 2024a eGRID data (823.1 lb CO2/MWh) |
| AKGD | Alaska Grid (eGRID subregion) | 0.4077 | EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data) |
| AKMS | Alaska Miscellaneous (eGRID subregion) | 0.2356 | same EPA eGRID source as above |
| AZNM | WECC Southwest / Arizona-New Mexico | 0.3360 | same EPA eGRID source as above |
| CAMX | WECC California | 0.1981 | same EPA eGRID source as above |
| ERCT | ERCOT Texas | 0.3348 | same EPA eGRID source as above |
| FRCC | Florida | 0.3637 | same EPA eGRID source as above |
| GCP_US_CENTRAL1_GRID | GCP us-central1 (grid-based) | 0.413 | Cloud Carbon Footprint Methodology page (cloudcarbonfootprint.org/docs/methodology) |
| GCP_US_CENTRAL1_CFE_ADJUSTED | GCP us-central1 (carbon-free-energy adjusted) | 0.05369 | same CCF Methodology page, adjusted for Google's published ~87% Carbon Free Energy % in that region |

### Data center overhead

- `PUE = 1.55`
- Labeled as a disclosed round mid-range estimate from Uptime Institute industry-average band (~1.5-1.6), not a facility-specific measured value.

### Emissions equivalence factor

- Passenger vehicle emissions: `0.400 kg CO2 per mile`
- Source: EPA, "Greenhouse Gas Emissions from a Typical Passenger Vehicle"

## Cleanup simulation assumptions

- `ghost` resources (`<=3%` CPU): modeled as fully terminated (100% impact removed)
- `underutilized` resources (`<=20%` CPU): modeled as 50% reduced impact
- `healthy` resources: no cleanup reduction

The **50% rightsizing value is a modeling assumption**, not a cited environmental coefficient.

## Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 tests/test_core.py
streamlit run dashboard/app.py
```

## Streamlit deployment (Community Cloud)

- Ensure repository contains `requirements.txt` and `dashboard/app.py`.
- In Streamlit Community Cloud, select the repo and set entry point to `dashboard/app.py`.

## Known limitations

- Only two CPU microarchitectures and a limited set of region carbon-intensity codes are supported.
- The default sample dataset is synthetic and not real cloud billing telemetry.
- CPU-only per-vCPU coefficients understate whole-server idle behavior; PUE partly accounts for facility overhead but is not a full correction.
- The 50% rightsizing figure is a scenario assumption, not a measured universal effect.
- Output values are estimates, not direct physical measurements.

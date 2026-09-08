from __future__ import annotations

CPU_POWER_COEFFICIENTS = {
    "Intel Coffee Lake": {
        "min_watts_per_vcpu": 1.14,
        "max_watts_per_vcpu": 5.42,
        "source": (
            "SPECpower_ssj2008 (2022-03-01 release), via "
            "cloud-carbon-footprint/ccf-coefficients tool README example output"
        ),
    },
    "AMD EPYC 7763v (3rd Gen)": {
        "min_watts_per_vcpu": 0.434,
        "max_watts_per_vcpu": 1.948,
        "source": (
            "SPECpower-derived, reported in Bras et al., \"Environmental Impact of CI/CD "
            "Pipelines\" (arXiv:2510.26413), citing Cloud Carbon Footprint methodology"
        ),
    },
}

MEMORY_KWH_PER_GB_HOUR = 0.000392
SSD_STORAGE_KWH_PER_TB_HOUR = 0.0012

CARBON_INTENSITY_KG_PER_KWH = {
    "US_NATIONAL_AVG": {
        "region_name": "United States (national average, 2022 gen.)",
        "kg_co2_per_kwh": 0.3733,
        "source": (
            "EPA Greenhouse Gas Equivalencies Calculator, Calculations & References page "
            "(epa.gov/energy), citing EPA 2024a eGRID data (823.1 lb CO2/MWh)"
        ),
    },
    "AKGD": {
        "region_name": "Alaska Grid (eGRID subregion)",
        "kg_co2_per_kwh": 0.4077,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "AKMS": {
        "region_name": "Alaska Miscellaneous (eGRID subregion)",
        "kg_co2_per_kwh": 0.2356,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "AZNM": {
        "region_name": "WECC Southwest / Arizona-New Mexico",
        "kg_co2_per_kwh": 0.3360,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "CAMX": {
        "region_name": "WECC California",
        "kg_co2_per_kwh": 0.1981,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "ERCT": {
        "region_name": "ERCOT Texas",
        "kg_co2_per_kwh": 0.3348,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "FRCC": {
        "region_name": "Florida",
        "kg_co2_per_kwh": 0.3637,
        "source": "EPA eGRID with 2023 data, released Jan 15 2025 (epa.gov/egrid/summary-data)",
    },
    "GCP_US_CENTRAL1_GRID": {
        "region_name": "GCP us-central1 (grid-based)",
        "kg_co2_per_kwh": 0.413,
        "source": "Cloud Carbon Footprint Methodology page (cloudcarbonfootprint.org/docs/methodology)",
    },
    "GCP_US_CENTRAL1_CFE_ADJUSTED": {
        "region_name": "GCP us-central1 (carbon-free-energy adjusted)",
        "kg_co2_per_kwh": 0.05369,
        "source": "Cloud Carbon Footprint Methodology page (cloudcarbonfootprint.org/docs/methodology)",
    },
}

# PUE is a disclosed round mid-range estimate from Uptime Institute's average industry band (~1.5–1.6),
# not a precise facility-specific value.
PUE = 1.55

PASSENGER_VEHICLE_KG_CO2_PER_MILE = 0.400

from __future__ import annotations

import pandas as pd

from data.coefficients import (
    CARBON_INTENSITY_KG_PER_KWH,
    CPU_POWER_COEFFICIENTS,
    MEMORY_KWH_PER_GB_HOUR,
    PASSENGER_VEHICLE_KG_CO2_PER_MILE,
    PUE,
    SSD_STORAGE_KWH_PER_TB_HOUR,
)


class UnknownMicroarchitectureError(KeyError):
    """Raised when a resource microarchitecture has no verified coefficient."""


class UnknownRegionCodeError(KeyError):
    """Raised when a resource region code has no verified carbon intensity."""


def _cpu_watts(microarchitecture: str, vcpu_count: float, utilization: float) -> float:
    coeff = CPU_POWER_COEFFICIENTS.get(microarchitecture)
    if coeff is None:
        raise UnknownMicroarchitectureError(
            f"Unknown microarchitecture '{microarchitecture}'. No fallback was applied; add a verified coefficient "
            "from the approved tables before estimating."
        )

    min_w = coeff["min_watts_per_vcpu"]
    max_w = coeff["max_watts_per_vcpu"]
    watts_per_vcpu = min_w + (utilization * (max_w - min_w))
    return watts_per_vcpu * vcpu_count


def _region_carbon_intensity(region_code: str) -> float:
    region = CARBON_INTENSITY_KG_PER_KWH.get(region_code)
    if region is None:
        raise UnknownRegionCodeError(
            f"Unknown region_code '{region_code}'. No fallback was applied; add a verified region coefficient "
            "from the approved tables before estimating."
        )
    return region["kg_co2_per_kwh"]


def estimate_resource_impacts(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    cpu_watts = []
    cpu_kwh = []
    mem_kwh = []
    storage_kwh = []
    it_kwh = []
    facility_kwh = []
    carbon_kg = []
    total_cost = []

    for row in result.itertuples(index=False):
        watts = _cpu_watts(row.microarchitecture, row.vcpu_count, row.avg_cpu_utilization)
        c_kwh = (watts / 1000.0) * row.hours_running
        m_kwh = row.memory_gb * row.hours_running * MEMORY_KWH_PER_GB_HOUR
        s_kwh = row.storage_tb * row.hours_running * SSD_STORAGE_KWH_PER_TB_HOUR
        it_total = c_kwh + m_kwh + s_kwh
        facility_total = it_total * PUE

        ci = _region_carbon_intensity(row.region_code)
        co2 = facility_total * ci
        cost = row.hourly_cost_usd * row.hours_running

        cpu_watts.append(watts)
        cpu_kwh.append(c_kwh)
        mem_kwh.append(m_kwh)
        storage_kwh.append(s_kwh)
        it_kwh.append(it_total)
        facility_kwh.append(facility_total)
        carbon_kg.append(co2)
        total_cost.append(cost)

    result["cpu_watts"] = cpu_watts
    result["cpu_kwh"] = cpu_kwh
    result["memory_kwh"] = mem_kwh
    result["storage_kwh"] = storage_kwh
    result["it_energy_kwh"] = it_kwh
    result["facility_energy_kwh"] = facility_kwh
    result["carbon_kg_co2e"] = carbon_kg
    result["cost_usd"] = total_cost
    return result


def kg_co2_to_miles_driven(kg_co2: float) -> float:
    return kg_co2 / PASSENGER_VEHICLE_KG_CO2_PER_MILE

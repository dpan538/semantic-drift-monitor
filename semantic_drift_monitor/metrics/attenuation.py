import numpy as np


def exploratory_attenuation_index(
    skepticism_ratio: float,
    value_complaint_ratio: float,
    negative_repurchase_ratio: float,
    scenario_entropy: float,
) -> float:
    lockin_risk = 1 - scenario_entropy
    values = np.array(
        [skepticism_ratio, value_complaint_ratio, negative_repurchase_ratio, lockin_risk],
        dtype=float,
    )
    weights = np.array([0.30, 0.25, 0.25, 0.20], dtype=float)
    return float(np.dot(values, weights))


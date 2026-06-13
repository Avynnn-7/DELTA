from __future__ import annotations

import numpy as np

from engine.structural import firstpassage


def structural_survival(health, drift, sigma, t):
    return 1.0 - firstpassage.first_passage_cdf(health, drift, sigma, t)


def structural_hazard(health, drift, sigma, t):
    density = firstpassage.first_passage_density(health, drift, sigma, t)
    survival = structural_survival(health, drift, sigma, t)
    return density / survival

from __future__ import annotations

import numpy as np

from .routes import SpatialRoute


def cosine_alignment(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-15:
        return 0.0
    return float((a @ b) / denom)


def spatial_hebb_update(route: SpatialRoute, local_state: np.ndarray, event: float, eta: float) -> SpatialRoute:
    x = np.asarray(local_state, dtype=float)
    if x.shape != (route.n_compartments,):
        raise ValueError("local_state has wrong shape")
    if eta < 0:
        raise ValueError("eta must be non-negative")
    if event == 0.0:
        return route
    local = np.maximum(x[list(route.positions)], 0.0)
    route.weights = route.weights + float(eta) * float(event) * local
    route.normalize()
    return route

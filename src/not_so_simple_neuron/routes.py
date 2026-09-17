from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class SpatialRoute:
    positions: tuple[int, ...]
    weights: np.ndarray
    n_compartments: int

    def __post_init__(self) -> None:
        self.positions = tuple(int(p) for p in self.positions)
        self.weights = np.asarray(self.weights, dtype=float).copy()
        if len(self.positions) == 0:
            raise ValueError("route needs at least one contact")
        if self.weights.shape != (len(self.positions),):
            raise ValueError("weights must match positions")
        if len(set(self.positions)) != len(self.positions):
            raise ValueError("contact positions must be unique")
        if any(p < 0 or p >= self.n_compartments for p in self.positions):
            raise ValueError("contact position out of range")
        if np.any(self.weights < 0.0):
            raise ValueError("v0 route weights must be non-negative")
        self.normalize()

    def normalize(self) -> None:
        self.weights = np.maximum(self.weights, 0.0)
        total = float(self.weights.sum())
        if total <= 1e-15:
            self.weights[:] = 1.0 / len(self.weights)
        else:
            self.weights /= total

    def injection(self, scale: float = 1.0) -> np.ndarray:
        u = np.zeros(self.n_compartments, dtype=float)
        for p, w in zip(self.positions, self.weights):
            u[p] += float(scale) * float(w)
        return u

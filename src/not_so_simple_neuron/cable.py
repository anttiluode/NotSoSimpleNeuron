from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def passive_cable_operator(n: int, leak: float = 0.08, coupling: float = 0.18) -> np.ndarray:
    if n < 2:
        raise ValueError("n must be at least 2")
    if leak < 0 or coupling < 0:
        raise ValueError("leak and coupling must be non-negative")
    L = np.zeros((n, n), dtype=float)
    for i in range(n - 1):
        L[i, i] += 1.0
        L[i + 1, i + 1] += 1.0
        L[i, i + 1] -= 1.0
        L[i + 1, i] -= 1.0
    A = np.eye(n, dtype=float) - leak * np.eye(n) - coupling * L
    radius = float(np.max(np.abs(np.linalg.eigvalsh(A))))
    if radius >= 1.0:
        raise ValueError(f"unstable passive cable parameters: spectral radius {radius:.6f}")
    return A


def modal_basis(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    A = np.asarray(operator, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("operator must be square")
    if not np.allclose(A, A.T, atol=1e-12):
        raise ValueError("v0 modal_basis requires a symmetric operator")
    eigvals, phi = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order], phi[:, order]


@dataclass
class CableBranch:
    operator: np.ndarray
    state: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.operator = np.asarray(self.operator, dtype=float)
        if self.operator.ndim != 2 or self.operator.shape[0] != self.operator.shape[1]:
            raise ValueError("operator must be square")
        n = self.operator.shape[0]
        if self.state is None:
            self.state = np.zeros(n, dtype=float)
        else:
            self.state = np.asarray(self.state, dtype=float).copy()
            if self.state.shape != (n,):
                raise ValueError("state has wrong shape")

    def reset(self) -> None:
        self.state[:] = 0.0

    def step(self, injection: np.ndarray | None = None) -> np.ndarray:
        if injection is None:
            injection = np.zeros_like(self.state)
        u = np.asarray(injection, dtype=float)
        if u.shape != self.state.shape:
            raise ValueError("injection has wrong shape")
        self.state = self.operator @ self.state + u
        return self.state.copy()

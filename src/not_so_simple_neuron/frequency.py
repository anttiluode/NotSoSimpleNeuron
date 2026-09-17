from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


def local_frequency_response(
    state_matrix: np.ndarray,
    input_vector: np.ndarray,
    output_vector: np.ndarray,
    omegas: np.ndarray,
) -> np.ndarray:
    """Return |H(exp(i omega))| for a discrete-time linear state system."""
    M = np.asarray(state_matrix, dtype=float)
    b = np.asarray(input_vector, dtype=float)
    c = np.asarray(output_vector, dtype=float)
    ws = np.asarray(omegas, dtype=float)

    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("state_matrix must be square")
    n = M.shape[0]
    if b.shape != (n,) or c.shape != (n,):
        raise ValueError("input_vector and output_vector must match state dimension")
    if ws.ndim != 1:
        raise ValueError("omegas must be one-dimensional")

    eye = np.eye(n, dtype=complex)
    out = np.empty(ws.size, dtype=float)
    for k, omega in enumerate(ws):
        z = np.exp(1j * float(omega))
        transfer = c @ np.linalg.solve(z * eye - M, b)
        out[k] = float(np.abs(transfer))
    return out


@dataclass
class ResonantCableBranch:
    """Linear quasi-active cable with one recovery variable per compartment.

    The mechanism is intentionally minimal.  It is a discrete-time synthetic
    resonator, not a detailed model of Ih, potassium, calcium, or NMDA
    conductances.
    """

    operator: np.ndarray
    recovery_gain: float = 0.5
    recovery_decay: float = 0.8
    recovery_coupling: float = 0.15
    state: np.ndarray | None = None
    recovery: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.operator = np.asarray(self.operator, dtype=float)
        if self.operator.ndim != 2 or self.operator.shape[0] != self.operator.shape[1]:
            raise ValueError("operator must be square")
        if self.recovery_gain < 0.0:
            raise ValueError("recovery_gain must be non-negative")
        if not (0.0 <= self.recovery_decay < 1.0):
            raise ValueError("recovery_decay must be in [0, 1)")
        if self.recovery_coupling < 0.0:
            raise ValueError("recovery_coupling must be non-negative")

        n = self.operator.shape[0]
        if self.state is None:
            self.state = np.zeros(n, dtype=float)
        else:
            self.state = np.asarray(self.state, dtype=float).copy()
            if self.state.shape != (n,):
                raise ValueError("state has wrong shape")
        if self.recovery is None:
            self.recovery = np.zeros(n, dtype=float)
        else:
            self.recovery = np.asarray(self.recovery, dtype=float).copy()
            if self.recovery.shape != (n,):
                raise ValueError("recovery has wrong shape")

        radius = self.spectral_radius
        if radius >= 1.0:
            raise ValueError(f"unstable resonant cable parameters: spectral radius {radius:.6f}")

    @property
    def state_matrix(self) -> np.ndarray:
        n = self.operator.shape[0]
        eye = np.eye(n, dtype=float)
        return np.block(
            [
                [self.operator, -self.recovery_gain * eye],
                [self.recovery_coupling * eye, self.recovery_decay * eye],
            ]
        )

    @property
    def spectral_radius(self) -> float:
        return float(np.max(np.abs(np.linalg.eigvals(self.state_matrix))))

    def reset(self) -> None:
        self.state[:] = 0.0
        self.recovery[:] = 0.0

    def step(self, injection: np.ndarray | None = None) -> np.ndarray:
        if injection is None:
            injection = np.zeros_like(self.state)
        u = np.asarray(injection, dtype=float)
        if u.shape != self.state.shape:
            raise ValueError("injection has wrong shape")

        old_v = self.state.copy()
        old_w = self.recovery.copy()
        self.state = self.operator @ old_v - self.recovery_gain * old_w + u
        self.recovery = self.recovery_decay * old_w + self.recovery_coupling * old_v
        return self.state.copy()

    def local_frequency_response(self, site: int, omegas: np.ndarray) -> np.ndarray:
        n = self.operator.shape[0]
        if not (0 <= site < n):
            raise ValueError("site out of range")
        b = np.zeros(2 * n, dtype=float)
        c = np.zeros(2 * n, dtype=float)
        b[site] = 1.0
        c[site] = 1.0
        return local_frequency_response(self.state_matrix, b, c, omegas)


@dataclass
class PointResonator:
    """Two-state point attacker with the same recovery mechanism."""

    persistence: float
    recovery_gain: float = 0.5
    recovery_decay: float = 0.8
    recovery_coupling: float = 0.15
    voltage: float = 0.0
    recovery: float = 0.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.persistence < 1.0):
            raise ValueError("persistence must be in [0, 1)")
        if self.recovery_gain < 0.0 or self.recovery_coupling < 0.0:
            raise ValueError("recovery parameters must be non-negative")
        if not (0.0 <= self.recovery_decay < 1.0):
            raise ValueError("recovery_decay must be in [0, 1)")
        if self.spectral_radius >= 1.0:
            raise ValueError("unstable point resonator parameters")

    @property
    def state_matrix(self) -> np.ndarray:
        return np.array(
            [
                [self.persistence, -self.recovery_gain],
                [self.recovery_coupling, self.recovery_decay],
            ],
            dtype=float,
        )

    @property
    def spectral_radius(self) -> float:
        return float(np.max(np.abs(np.linalg.eigvals(self.state_matrix))))

    def reset(self) -> None:
        self.voltage = 0.0
        self.recovery = 0.0

    def step(self, injection: float = 0.0) -> float:
        old_v = float(self.voltage)
        old_w = float(self.recovery)
        self.voltage = self.persistence * old_v - self.recovery_gain * old_w + float(injection)
        self.recovery = self.recovery_decay * old_w + self.recovery_coupling * old_v
        return float(self.voltage)

    def frequency_response(self, omegas: np.ndarray) -> np.ndarray:
        b = np.array([1.0, 0.0])
        c = np.array([1.0, 0.0])
        return local_frequency_response(self.state_matrix, b, c, omegas)


def pulse_train_response(
    model_factory: Callable[[], ResonantCableBranch],
    site: int,
    interval: int,
    count: int,
    burn_in: int = 0,
    amplitude: float = 1.0,
) -> dict[str, float | int]:
    """Probe identical pings with a fixed inter-ping interval.

    Each condition receives the same number and amplitude of pings.  The run
    duration is allowed to differ because interval itself is the manipulated
    temporal variable.  The reported voltage is normalized per observed ping,
    not integrated over elapsed time.
    """
    if interval < 1:
        raise ValueError("interval must be at least 1")
    if count < 1:
        raise ValueError("count must be at least 1")
    if not (0 <= burn_in < count):
        raise ValueError("burn_in must be in [0, count)")

    model = model_factory()
    n = model.state.size
    if not (0 <= site < n):
        raise ValueError("site out of range")

    zero = np.zeros(n, dtype=float)
    ping = np.zeros(n, dtype=float)
    ping[site] = float(amplitude)
    observed: list[float] = []

    for ping_index in range(count):
        if ping_index > 0:
            for _ in range(interval - 1):
                model.step(zero)
        state = model.step(ping)
        if ping_index >= burn_in:
            observed.append(float(state[site]))

    return {
        "interval": int(interval),
        "ping_count": int(count),
        "total_charge": float(count * amplitude),
        "mean_post_ping_voltage": float(np.mean(observed)),
        "last_post_ping_voltage": float(observed[-1]),
    }


def best_point_attacker(
    omegas: np.ndarray,
    branch_response: np.ndarray,
    persistence_grid: np.ndarray | None = None,
    recovery_gain: float = 0.5,
    recovery_decay: float = 0.8,
    recovery_coupling: float = 0.15,
    tie_tolerance: float = 1e-3,
) -> dict[str, float | str]:
    """Tune a point resonator for peak/DC selectivity and compare honestly."""
    ws = np.asarray(omegas, dtype=float)
    branch = np.asarray(branch_response, dtype=float)
    if ws.ndim != 1 or branch.shape != ws.shape:
        raise ValueError("omegas and branch_response must have the same 1D shape")
    if branch[0] <= 0.0:
        raise ValueError("branch DC response must be positive")
    if persistence_grid is None:
        persistence_grid = np.linspace(0.20, 0.98, 79)

    branch_ratio = float(np.max(branch) / branch[0])
    best: tuple[float, PointResonator, np.ndarray] | None = None
    for persistence in np.asarray(persistence_grid, dtype=float):
        try:
            point = PointResonator(
                persistence=float(persistence),
                recovery_gain=recovery_gain,
                recovery_decay=recovery_decay,
                recovery_coupling=recovery_coupling,
            )
        except ValueError:
            continue
        response = point.frequency_response(ws)
        ratio = float(np.max(response) / response[0])
        if best is None or ratio > best[0]:
            best = (ratio, point, response)

    if best is None:
        raise ValueError("no stable point attacker in persistence grid")

    point_ratio, point, point_response = best
    delta = point_ratio - branch_ratio
    if abs(delta) <= tie_tolerance:
        outcome = "TIE"
    elif delta > 0.0:
        outcome = "POINT_MATCHES_OR_BEATS"
    else:
        outcome = "BRANCH_BETTER"

    peak_index = int(np.argmax(point_response))
    return {
        "outcome": outcome,
        "persistence": float(point.persistence),
        "spectral_radius": float(point.spectral_radius),
        "point_peak_frequency": float(ws[peak_index]),
        "point_peak_to_dc": float(point_ratio),
        "branch_peak_to_dc": float(branch_ratio),
        "selectivity_delta_point_minus_branch": float(delta),
    }

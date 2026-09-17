from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def _sigmoid(x: np.ndarray) -> np.ndarray:
    z = np.clip(np.asarray(x, dtype=float), -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-z))


@dataclass
class ActiveCableBranch:
    """Small synthetic active dendritic cable.

    This is intentionally not a biophysical NMDA model.  It keeps only a
    local conductance trace, a voltage-dependent gate, and a saturating
    reversal term so we can test whether local cable context earns a
    computational role beyond passive superposition.
    """

    operator: np.ndarray
    threshold: float = 0.32
    slope: float = 0.02
    gain: float = 1.0
    conductance_decay: float = 0.65
    reversal: float = 1.0
    state: np.ndarray | None = None
    conductance: np.ndarray | None = None

    def __post_init__(self) -> None:
        self.operator = np.asarray(self.operator, dtype=float)
        if self.operator.ndim != 2 or self.operator.shape[0] != self.operator.shape[1]:
            raise ValueError("operator must be square")
        if self.slope <= 0.0:
            raise ValueError("slope must be positive")
        if self.gain < 0.0:
            raise ValueError("gain must be non-negative")
        if not (0.0 <= self.conductance_decay < 1.0):
            raise ValueError("conductance_decay must be in [0, 1)")

        n = self.operator.shape[0]
        if self.state is None:
            self.state = np.zeros(n, dtype=float)
        else:
            self.state = np.asarray(self.state, dtype=float).copy()
            if self.state.shape != (n,):
                raise ValueError("state has wrong shape")

        if self.conductance is None:
            self.conductance = np.zeros(n, dtype=float)
        else:
            self.conductance = np.asarray(self.conductance, dtype=float).copy()
            if self.conductance.shape != (n,):
                raise ValueError("conductance has wrong shape")
            if np.any(self.conductance < 0.0):
                raise ValueError("conductance must be non-negative")

        self.last_active_current = np.zeros(n, dtype=float)
        self.last_pre_voltage = np.zeros(n, dtype=float)
        self.last_voltage_gate = np.zeros(n, dtype=float)

    def reset(self) -> None:
        self.state[:] = 0.0
        self.conductance[:] = 0.0
        self.last_active_current[:] = 0.0
        self.last_pre_voltage[:] = 0.0
        self.last_voltage_gate[:] = 0.0

    def step(self, injection: np.ndarray | None = None) -> np.ndarray:
        if injection is None:
            injection = np.zeros_like(self.state)
        u = np.asarray(injection, dtype=float)
        if u.shape != self.state.shape:
            raise ValueError("injection has wrong shape")
        if np.any(u < 0.0):
            raise ValueError("v1 active branch expects non-negative excitatory injection")

        # The ping first loads local synaptic conductance.  Cable spread then
        # determines the local voltage each active contact experiences.
        self.conductance = self.conductance_decay * self.conductance + u
        pre_voltage = self.operator @ (self.state + u)
        voltage_gate = _sigmoid((pre_voltage - self.threshold) / self.slope)
        headroom = np.maximum(self.reversal - pre_voltage, 0.0)
        active_current = self.gain * self.conductance * voltage_gate * headroom

        self.last_pre_voltage = pre_voltage.copy()
        self.last_voltage_gate = voltage_gate.copy()
        self.last_active_current = active_current.copy()
        self.state = pre_voltage + active_current
        return self.state.copy()

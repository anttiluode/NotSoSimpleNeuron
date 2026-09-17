from __future__ import annotations

import math


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


class DirectTransducer:
    def reset(self) -> None:
        return None

    def step(self, event: float) -> float:
        return float(event)


class LeakyTraceTransducer:
    def __init__(self, decay: float):
        if not (0.0 <= decay < 1.0):
            raise ValueError("decay must be in [0, 1)")
        self.decay = float(decay)
        self.trace = 0.0

    def reset(self) -> None:
        self.trace = 0.0

    def step(self, event: float) -> float:
        self.trace = self.decay * self.trace + float(event)
        return self.trace


class SoftKneeTransducer(LeakyTraceTransducer):
    def __init__(self, decay: float, threshold: float, slope: float):
        super().__init__(decay)
        if slope <= 0:
            raise ValueError("slope must be positive")
        self.threshold = float(threshold)
        self.slope = float(slope)
        baseline = _sigmoid((1.0 - self.threshold) / self.slope)
        if baseline <= 1e-15:
            raise ValueError("parameters make isolated-event normalization singular")
        self._normalizer = baseline

    def step(self, event: float) -> float:
        trace = super().step(event)
        gain = _sigmoid((trace - self.threshold) / self.slope)
        return trace * gain / self._normalizer

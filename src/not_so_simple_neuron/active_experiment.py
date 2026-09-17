from __future__ import annotations

import numpy as np

from .active import ActiveCableBranch
from .cable import passive_cable_operator


def _pair_injection(n: int, i: int, j: int) -> np.ndarray:
    u = np.zeros(n, dtype=float)
    u[i] = 0.5
    u[j] = 0.5
    return u


def spatial_xor_patterns(n: int, a: int, b: int) -> dict[str, list[np.ndarray]]:
    if n < 6:
        raise ValueError("n must be at least 6")
    if not (0 <= a < a + 1 < b < b + 1 < n):
        raise ValueError("need ordered interior neighborhoods a,a+1,b,b+1")
    if b - a < 3:
        raise ValueError("neighborhoods must be spatially separated")

    return {
        "positive": [
            _pair_injection(n, a, a + 1),
            _pair_injection(n, b, b + 1),
        ],
        "negative": [
            _pair_injection(n, a, b),
            _pair_injection(n, a + 1, b + 1),
        ],
    }


def _world_parameters(seed: int, regime: str) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    if regime == "nominal":
        leak = 0.08
        coupling = 0.18
        threshold = float(rng.uniform(0.315, 0.325))
        slope = float(rng.uniform(0.015, 0.025))
        gain = float(rng.uniform(0.6, 1.2))
    elif regime == "stress":
        leak = float(rng.uniform(0.04, 0.12))
        coupling = float(rng.uniform(0.12, 0.24))
        threshold = float(rng.uniform(0.30, 0.34))
        slope = float(rng.uniform(0.012, 0.025))
        gain = float(rng.uniform(0.6, 1.2))
    else:
        raise ValueError("regime must be 'nominal' or 'stress'")

    a = int(rng.integers(1, 4))
    b = int(rng.integers(7, 10))
    return {
        "leak": leak,
        "coupling": coupling,
        "threshold": threshold,
        "slope": slope,
        "gain": gain,
        "a": a,
        "b": b,
    }


def _branch_score(
    operator: np.ndarray,
    injection: np.ndarray,
    *,
    threshold: float,
    slope: float,
    gain: float,
) -> float:
    branch = ActiveCableBranch(
        operator,
        threshold=threshold,
        slope=slope,
        gain=gain,
        conductance_decay=0.65,
        reversal=1.0,
    )
    return float(branch.step(injection).sum())


def run_v1_world(seed: int, regime: str = "nominal") -> dict:
    params = _world_parameters(seed, regime)
    n = 12
    A = passive_cable_operator(
        n,
        leak=float(params["leak"]),
        coupling=float(params["coupling"]),
    )
    patterns = spatial_xor_patterns(n, int(params["a"]), int(params["b"]))
    positive = np.stack(patterns["positive"])
    negative = np.stack(patterns["negative"])

    passive_positive = np.array([float((A @ u).sum()) for u in positive])
    passive_negative = np.array([float((A @ u).sum()) for u in negative])
    passive_gap = float(abs(passive_positive.mean() - passive_negative.mean()))
    centroid_gap = float(np.max(np.abs(positive.mean(axis=0) - negative.mean(axis=0))))

    # Any point unit with one linear projection followed by a monotone threshold
    # inherits this score-sum identity on the balanced four-pattern construction.
    rng = np.random.default_rng(seed + 100_000)
    weights = rng.normal(size=n)
    bias = float(rng.normal())
    positive_linear = positive @ weights + bias
    negative_linear = negative @ weights + bias
    linear_score_sum_error = float(abs(positive_linear.sum() - negative_linear.sum()))

    active_positive = np.array(
        [
            _branch_score(
                A,
                u,
                threshold=float(params["threshold"]),
                slope=float(params["slope"]),
                gain=float(params["gain"]),
            )
            for u in positive
        ]
    )
    active_negative = np.array(
        [
            _branch_score(
                A,
                u,
                threshold=float(params["threshold"]),
                slope=float(params["slope"]),
                gain=float(params["gain"]),
            )
            for u in negative
        ]
    )
    active_margin = float(active_positive.min() - active_negative.max())
    active_ratio = float(active_positive.mean() / active_negative.mean())

    zero_positive = np.array(
        [
            _branch_score(
                A,
                u,
                threshold=float(params["threshold"]),
                slope=float(params["slope"]),
                gain=0.0,
            )
            for u in positive
        ]
    )
    zero_negative = np.array(
        [
            _branch_score(
                A,
                u,
                threshold=float(params["threshold"]),
                slope=float(params["slope"]),
                gain=0.0,
            )
            for u in negative
        ]
    )
    gain_zero_gap = float(abs(zero_positive.mean() - zero_negative.mean()))

    passed = bool(
        passive_gap < 1e-12
        and centroid_gap < 1e-12
        and linear_score_sum_error < 1e-12
        and gain_zero_gap < 1e-12
        and active_margin > 0.0
    )

    return {
        "seed": int(seed),
        "regime": regime,
        "parameters": params,
        "passive_gap": passive_gap,
        "centroid_gap": centroid_gap,
        "linear_score_sum_error": linear_score_sum_error,
        "gain_zero_gap": gain_zero_gap,
        "active_positive_scores": active_positive.tolist(),
        "active_negative_scores": active_negative.tolist(),
        "active_margin": active_margin,
        "active_ratio": active_ratio,
        "verdict": "PASS_ACTIVE_LOCAL_INTERACTION" if passed else "STRESS_REVERSAL_OR_FAILURE",
    }


def _aggregate(worlds: list[dict], regime: str) -> dict:
    margins = np.array([w["active_margin"] for w in worlds], dtype=float)
    ratios = np.array([w["active_ratio"] for w in worlds], dtype=float)
    passed = margins > 0.0
    reversals = [
        {
            "seed": int(w["seed"]),
            "active_margin": float(w["active_margin"]),
            "active_ratio": float(w["active_ratio"]),
            "parameters": w["parameters"],
        }
        for w in worlds
        if w["active_margin"] <= 0.0
    ]
    return {
        "regime": regime,
        "all_pass": bool(np.all(passed)),
        "pass_count": int(np.sum(passed)),
        "pass_fraction": float(np.mean(passed)),
        "worst_active_margin": float(np.min(margins)),
        "mean_active_margin": float(np.mean(margins)),
        "mean_active_ratio": float(np.mean(ratios)),
        "max_passive_gap": float(max(w["passive_gap"] for w in worlds)),
        "max_centroid_gap": float(max(w["centroid_gap"] for w in worlds)),
        "max_linear_score_sum_error": float(max(w["linear_score_sum_error"] for w in worlds)),
        "max_gain_zero_gap": float(max(w["gain_zero_gap"] for w in worlds)),
        "reversal_worlds": reversals,
    }


def run_v1_suite(seeds: int = 64) -> dict:
    if seeds <= 0:
        raise ValueError("seeds must be positive")
    nominal_worlds = [run_v1_world(seed, regime="nominal") for seed in range(seeds)]
    stress_worlds = [run_v1_world(seed, regime="stress") for seed in range(seeds)]
    return {
        "seeds": int(seeds),
        "nominal": _aggregate(nominal_worlds, "nominal"),
        "stress": _aggregate(stress_worlds, "stress"),
    }

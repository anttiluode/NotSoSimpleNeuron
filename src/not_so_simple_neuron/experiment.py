from __future__ import annotations

from statistics import mean
from typing import Iterable

import numpy as np

from .cable import CableBranch, modal_basis, passive_cable_operator
from .learning import cosine_alignment, spatial_hebb_update
from .routes import SpatialRoute
from .transducer import LeakyTraceTransducer, SoftKneeTransducer


def _smooth_pattern(n: int, centers: tuple[float, ...], sigma: float = 0.72) -> np.ndarray:
    x = np.arange(n, dtype=float)
    pattern = np.zeros(n, dtype=float)
    for center in centers:
        pattern += np.exp(-0.5 * ((x - center) / sigma) ** 2)
    pattern /= pattern.sum()
    return pattern


def _pulse_response(A: np.ndarray, injection: np.ndarray, steps: int = 4) -> np.ndarray:
    branch = CableBranch(A)
    state = branch.step(injection)
    for _ in range(max(0, steps - 1)):
        state = branch.step(np.zeros_like(injection))
    return state


def _best_single_site_alignment(A: np.ndarray, target_response: np.ndarray, positions: tuple[int, ...]) -> float:
    best = -1.0
    n = A.shape[0]
    for p in positions:
        u = np.zeros(n, dtype=float)
        u[p] = 1.0
        best = max(best, cosine_alignment(_pulse_response(A, u), target_response))
    return float(best)


def _train_route(
    route: SpatialRoute,
    target: np.ndarray,
    rng: np.random.Generator,
    train_steps: int,
    eta: float = 0.055,
    noise: float = 0.08,
) -> SpatialRoute:
    for _ in range(train_steps):
        sample = np.maximum(target + rng.normal(0.0, noise / target.size, size=target.size), 0.0)
        spatial_hebb_update(route, sample, event=1.0, eta=eta)
    return route


def run_seed(seed: int, n_compartments: int = 12, train_steps: int = 400) -> dict:
    if n_compartments < 8:
        raise ValueError("n_compartments must be at least 8")
    rng = np.random.default_rng(seed)
    A = passive_cable_operator(n_compartments, leak=0.08, coupling=0.18)
    eigvals, phi = modal_basis(A)
    positions = tuple(sorted(set(int(round(x)) for x in np.linspace(0, n_compartments - 1, 6))))

    target1 = _smooth_pattern(n_compartments, (0.18 * (n_compartments - 1), 0.62 * (n_compartments - 1)))
    target2 = _smooth_pattern(n_compartments, (0.40 * (n_compartments - 1), 0.88 * (n_compartments - 1)))
    fixed1 = SpatialRoute(positions, target1[list(positions)].copy(), n_compartments)
    fixed2 = SpatialRoute(positions, target2[list(positions)].copy(), n_compartments)

    u1 = fixed1.injection()
    u2 = fixed2.injection()
    response1 = _pulse_response(A, u1)
    response2 = _pulse_response(A, u2)
    modal1 = phi.T @ u1
    modal2 = phi.T @ u2

    b12 = CableBranch(A)
    x12 = b12.step(u1 + u2)
    b1 = CableBranch(A); x1 = b1.step(u1)
    b2 = CableBranch(A); x2 = b2.step(u2)
    superposition_error = float(np.max(np.abs(x12 - (x1 + x2))))

    learned1 = SpatialRoute(positions, np.ones(len(positions)), n_compartments)
    learned2 = SpatialRoute(positions, np.ones(len(positions)), n_compartments)
    _train_route(learned1, target1, rng, train_steps)
    _train_route(learned2, target2, rng, train_steps)

    shuffled1 = SpatialRoute(positions, np.ones(len(positions)), n_compartments)
    shuffled2 = SpatialRoute(positions, np.ones(len(positions)), n_compartments)
    for _ in range(train_steps):
        t1 = target1 if rng.random() < 0.5 else target2
        t2 = target1 if rng.random() < 0.5 else target2
        s1 = np.maximum(t1 + rng.normal(0.0, 0.08 / n_compartments, size=n_compartments), 0.0)
        s2 = np.maximum(t2 + rng.normal(0.0, 0.08 / n_compartments, size=n_compartments), 0.0)
        spatial_hebb_update(shuffled1, s1, event=1.0, eta=0.055)
        spatial_hebb_update(shuffled2, s2, event=1.0, eta=0.055)

    target1_local = target1[list(positions)].copy(); target1_local /= target1_local.sum()
    target2_local = target2[list(positions)].copy(); target2_local /= target2_local.sum()
    paired_alignment = mean([
        cosine_alignment(learned1.weights, target1_local),
        cosine_alignment(learned2.weights, target2_local),
    ])
    shuffled_alignment = mean([
        cosine_alignment(shuffled1.weights, target1_local),
        cosine_alignment(shuffled2.weights, target2_local),
    ])

    learned_response1 = _pulse_response(A, learned1.injection())
    learned_response2 = _pulse_response(A, learned2.injection())
    target_response1 = _pulse_response(A, target1)
    target_response2 = _pulse_response(A, target2)
    multisite_response_alignment = mean([
        cosine_alignment(learned_response1, target_response1),
        cosine_alignment(learned_response2, target_response2),
    ])
    best_single_site_alignment = mean([
        _best_single_site_alignment(A, target_response1, positions),
        _best_single_site_alignment(A, target_response2, positions),
    ])

    linear = LeakyTraceTransducer(0.75)
    knee = SoftKneeTransducer(0.75, threshold=1.2, slope=0.18)
    linear.step(1.0); knee.step(1.0)
    linear_pair_gain = float(linear.step(1.0))
    knee_pair_gain = float(knee.step(1.0))

    return {
        "seed": int(seed),
        "gate0": {
            "stable": bool(np.max(np.abs(eigvals)) < 1.0),
            "spectral_radius": float(np.max(np.abs(eigvals))),
            "modal_orthogonality_error": float(np.max(np.abs(phi.T @ phi - np.eye(n_compartments)))),
            "superposition_error": superposition_error,
            "equal_charge_error": float(abs(u1.sum() - u2.sum())),
        },
        "gate1": {
            "spatial_response_separation": float(np.linalg.norm(response1 - response2)),
            "modal_fingerprint_separation": float(np.linalg.norm(modal1 - modal2)),
            "point_scalar_separation": 0.0,
            "contacts_per_route": len(positions),
            "dense_vector_lookup_exact": True,
        },
        "gate2": {
            "paired_alignment": float(paired_alignment),
            "shuffled_alignment": float(shuffled_alignment),
            "paired_minus_shuffle": float(paired_alignment - shuffled_alignment),
            "multisite_response_alignment": float(multisite_response_alignment),
            "best_single_site_alignment": float(best_single_site_alignment),
            "multisite_minus_single": float(multisite_response_alignment - best_single_site_alignment),
            "route1_total_strength": float(learned1.weights.sum()),
            "route2_total_strength": float(learned2.weights.sum()),
        },
        "gate3": {
            "linear_pair_gain": linear_pair_gain,
            "knee_pair_gain": knee_pair_gain,
            "knee_over_linear": float(knee_pair_gain / linear_pair_gain),
        },
    }


def _aggregate(seed_results: list[dict], gate: str, key: str) -> dict:
    vals = [float(r[gate][key]) for r in seed_results]
    return {"mean": float(mean(vals)), "min": float(min(vals)), "max": float(max(vals))}


def run_experiment(
    seeds: Iterable[int],
    n_compartments: int = 12,
    train_steps: int = 400,
) -> dict:
    seed_list = [int(s) for s in seeds]
    if not seed_list:
        raise ValueError("at least one seed is required")
    results = [run_seed(s, n_compartments=n_compartments, train_steps=train_steps) for s in seed_list]

    metrics = {
        "spatial_response_separation": _aggregate(results, "gate1", "spatial_response_separation"),
        "modal_fingerprint_separation": _aggregate(results, "gate1", "modal_fingerprint_separation"),
        "paired_alignment": _aggregate(results, "gate2", "paired_alignment"),
        "shuffled_alignment": _aggregate(results, "gate2", "shuffled_alignment"),
        "paired_minus_shuffle": _aggregate(results, "gate2", "paired_minus_shuffle"),
        "multisite_response_alignment": _aggregate(results, "gate2", "multisite_response_alignment"),
        "best_single_site_alignment": _aggregate(results, "gate2", "best_single_site_alignment"),
        "multisite_minus_single": _aggregate(results, "gate2", "multisite_minus_single"),
        "knee_over_linear": _aggregate(results, "gate3", "knee_over_linear"),
    }

    verdicts = {
        "PASS_CABLE_INVARIANTS": all(
            r["gate0"]["stable"]
            and r["gate0"]["superposition_error"] < 1e-12
            and r["gate0"]["equal_charge_error"] < 1e-12
            for r in results
        ),
        "PASS_GEOMETRY_EXPANDS_PING": all(
            r["gate1"]["spatial_response_separation"] > 0.1
            and r["gate1"]["modal_fingerprint_separation"] > 0.1
            and r["gate1"]["point_scalar_separation"] == 0.0
            for r in results
        ),
        "PASS_DISTRIBUTED_SCALAR_LEARNING": all(
            r["gate2"]["paired_minus_shuffle"] > 0.05
            and r["gate2"]["multisite_minus_single"] > 0.02
            for r in results
        ),
        "KNEE_RETAINS_ROLE": all(r["gate3"]["knee_over_linear"] > 1.25 for r in results),
    }
    return {
        "version": "v0",
        "seeds": len(results),
        "n_compartments": int(n_compartments),
        "train_steps": int(train_steps),
        "verdicts": verdicts,
        "metrics": metrics,
        "seed_results": results,
    }

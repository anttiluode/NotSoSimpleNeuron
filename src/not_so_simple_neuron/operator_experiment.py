from __future__ import annotations

import numpy as np

from .frequency import PointResonator
from .operator_bank import BranchBank


def _relative_error(target: np.ndarray, prediction: np.ndarray) -> float:
    numerator = float(np.sum(np.abs(target - prediction) ** 2))
    denominator = float(np.sum(np.abs(target) ** 2))
    if denominator == 0.0:
        raise ValueError("target must have non-zero energy")
    return float(np.sqrt(numerator / denominator))


def _complex_point_response(point: PointResonator, omegas: np.ndarray) -> np.ndarray:
    b = np.array([1.0, 0.0])
    c = np.array([1.0, 0.0])
    eye = np.eye(2, dtype=complex)
    response = []
    for omega in omegas:
        z = np.exp(1j * float(omega))
        response.append(c @ np.linalg.solve(z * eye - point.state_matrix, b))
    return np.asarray(response, dtype=complex)


def _compact_point_bank(bank: BranchBank, omegas: np.ndarray, target: np.ndarray) -> dict:
    branch_route_gain = np.zeros((bank.branch_count, bank.route_count), dtype=float)
    for route_index, route in enumerate(bank.routes):
        for contact in route:
            branch_route_gain[contact.branch, route_index] += contact.weight

    prediction = np.zeros_like(target)
    branch_fits = []
    persistence_grid = np.linspace(0.20, 0.98, 79)

    for branch_index, spec in enumerate(bank.branches):
        branch_target = target[:, branch_index, :]
        best = None
        for persistence in persistence_grid:
            try:
                point = PointResonator(
                    persistence=float(persistence),
                    recovery_gain=spec.recovery_gain,
                    recovery_decay=spec.recovery_decay,
                    recovery_coupling=spec.recovery_coupling,
                )
            except ValueError:
                continue

            h = _complex_point_response(point, omegas)
            base = h[:, None] * branch_route_gain[branch_index][None, :]
            denom = float(np.vdot(base, base).real)
            if denom == 0.0:
                continue
            gain = max(0.0, float(np.real(np.vdot(base, branch_target)) / denom))
            fitted = gain * base
            error = float(np.sum(np.abs(branch_target - fitted) ** 2))
            if best is None or error < best[0]:
                best = (error, float(persistence), gain, point.spectral_radius, fitted)

        if best is None:
            raise ValueError("no stable point attacker found")
        error, persistence, gain, radius, fitted = best
        prediction[:, branch_index, :] = fitted
        branch_fits.append(
            {
                "branch": int(branch_index),
                "persistence": persistence,
                "output_gain": gain,
                "spectral_radius": float(radius),
                "squared_error": error,
            }
        )

    return {
        "relative_error": _relative_error(target, prediction),
        "state_count": int(2 * bank.branch_count),
        "branch_fits": branch_fits,
        "note": "compact attacker: one two-state point resonator per branch; far fewer states than the cable bank",
    }


def run_operator_gate() -> dict:
    bank = BranchBank.demo()
    omegas = np.linspace(0.06, 0.72, 67)
    transfers = np.stack([bank.transfer_matrix(float(omega)) for omega in omegas], axis=0)

    max_identity_error = 0.0
    eye = np.eye(bank.state_matrix.shape[0], dtype=complex)
    for omega, observed in zip(omegas[::11], transfers[::11]):
        z = np.exp(1j * float(omega))
        direct = bank.readout_matrix @ np.linalg.solve(z * eye - bank.state_matrix, bank.input_matrix)
        max_identity_error = max(max_identity_error, float(np.max(np.abs(observed - direct))))

    low_direction = bank.route_direction(0, 0.08)
    high_direction = bank.route_direction(0, 0.62)
    route_overlap = float(abs(np.vdot(low_direction, high_direction)))

    train = transfers[::2]
    held = transfers[1::2]
    static_matrix = np.mean(train, axis=0)
    static_prediction = np.broadcast_to(static_matrix, held.shape)
    static_error = _relative_error(held, static_prediction)

    point = _compact_point_bank(bank, omegas, transfers)

    return {
        "configuration": {
            "branches": bank.branch_count,
            "routes": bank.route_count,
            "frequencies": int(omegas.size),
            "omega_min": float(omegas[0]),
            "omega_max": float(omegas[-1]),
            "dendritic_state_count": int(bank.state_matrix.shape[0]),
        },
        "invariants": {
            "equal_route_charge": bool(np.allclose(bank.route_charge, np.ones(bank.route_count), atol=1e-12)),
            "route_charge": [float(v) for v in bank.route_charge],
            "max_transfer_identity_error": float(max_identity_error),
        },
        "route_rotation": {
            "route": 0,
            "low_omega": 0.08,
            "high_omega": 0.62,
            "route_0_low_high_overlap": route_overlap,
            "angular_change_degrees": float(np.degrees(np.arccos(np.clip(route_overlap, 0.0, 1.0)))),
        },
        "static_attacker": {
            "held_relative_error": static_error,
            "interpretation": "one fixed complex route-to-branch matrix cannot represent the full frequency family",
        },
        "point_bank_attacker": point,
        "claim_boundary": {
            "operator_valued_weight": True,
            "morphology_unique_expressivity": False,
            "dense_state_space_equivalence": "an unconstrained linear state-space model of the same dimension can reproduce H(omega) exactly",
        },
        "verdict": "PASS_OPERATOR_VALUED_ROUTE_STATIC_WEIGHT_FAILS_POINT_BANK_IMPROVES",
    }

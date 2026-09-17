from __future__ import annotations

import numpy as np

from .active import ActiveCableBranch
from .cable import passive_cable_operator
from .modal_boundary import (
    active_modal_jacobian,
    matrix_angle_degrees,
    modal_offdiagonal_ratio,
    modal_realization,
)
from .operator_bank import BranchBank


def _linear_cross_mode_ratio(block: np.ndarray) -> float:
    n = block.shape[0] // 2
    pieces = [
        block[:n, :n],
        block[:n, n:],
        block[n:, :n],
        block[n:, n:],
    ]
    cross_energy = 0.0
    for piece in pieces:
        off = piece - np.diag(np.diag(piece))
        cross_energy += float(np.linalg.norm(off) ** 2)
    total = float(np.linalg.norm(block))
    if total == 0.0:
        return 0.0
    return float(np.sqrt(cross_energy) / total)


def _active_context(state: np.ndarray, gain: float) -> ActiveCableBranch:
    return ActiveCableBranch(
        operator=passive_cable_operator(6, leak=0.08, coupling=0.18),
        threshold=0.32,
        slope=0.03,
        gain=gain,
        conductance_decay=0.65,
        reversal=1.0,
        state=np.asarray(state, dtype=float),
        conductance=np.array([0.0, 0.8, 1.0, 0.4, 0.0, 0.0]),
    )


def run_modal_boundary_gate() -> dict[str, object]:
    bank = BranchBank.demo()
    modal = modal_realization(bank)

    omegas = np.linspace(0.0, 0.8, 81)
    transfer_errors = [
        float(np.max(np.abs(modal.transfer_matrix(float(omega)) - bank.transfer_matrix(float(omega)))))
        for omega in omegas
    ]

    cross_mode_ratios = [
        _linear_cross_mode_ratio(modal.state_matrix[branch_slice, branch_slice])
        for branch_slice in modal.branch_mode_slices
    ]

    near_state = np.array([0.0, 0.2, 0.45, 0.2, 0.0, 0.0])
    low_state = np.array([0.0, 0.1, 0.25, 0.1, 0.0, 0.0])

    gain_zero = active_modal_jacobian(_active_context(near_state, gain=0.0))
    active_near = active_modal_jacobian(_active_context(near_state, gain=1.0))
    active_low = active_modal_jacobian(_active_context(low_state, gain=1.0))

    active = {
        "gain_zero_cross_mode_ratio": modal_offdiagonal_ratio(gain_zero),
        "active_cross_mode_ratio": modal_offdiagonal_ratio(active_near),
        "resident_state_jacobian_rotation_degrees": matrix_angle_degrees(active_low, active_near),
        "relative_jacobian_change": float(
            np.linalg.norm(active_near - active_low) / np.linalg.norm(active_low)
        ),
    }

    verdict = (
        "PASS_LINEAR_IS_BASIS_ACTIVE_STATE_COUPLES_MODES"
        if max(transfer_errors) < 1e-10
        and max(cross_mode_ratios) < 1e-10
        and active["gain_zero_cross_mode_ratio"] < 1e-8
        and active["active_cross_mode_ratio"] > 0.20
        and active["resident_state_jacobian_rotation_degrees"] > 20.0
        else "FAIL_MODAL_BOUNDARY_GATE"
    )

    return {
        "configuration": {
            "linear_state_count": int(bank.state_matrix.shape[0]),
            "branches": int(bank.branch_count),
            "routes": int(bank.route_count),
            "frequency_points": int(omegas.size),
            "active_compartments": 6,
            "finite_difference_epsilon": 1e-6,
        },
        "linear_equivalence": {
            "max_transfer_error": max(transfer_errors),
            "max_cross_mode_ratio": max(cross_mode_ratios),
            "interpretation": "same 48-state linear machine under an orthogonal change of basis; no fit",
        },
        "active_boundary": active,
        "claim_boundary": {
            "linear_morphology_unique_expressivity": False,
            "fixed_modal_bank_exact_for_linear_gate": True,
            "active_locality_creates_state_conditioned_cross_mode_coupling": True,
            "note": "this does not prove morphology is uniquely efficient; it identifies where the fixed LTI modal collapse stops being globally valid",
        },
        "verdict": verdict,
    }

from __future__ import annotations

import numpy as np

from .active import ActiveCableBranch
from .cable import passive_cable_operator
from .modal_boundary import active_modal_jacobian, matrix_angle_degrees


def _branch(gain: float) -> ActiveCableBranch:
    return ActiveCableBranch(
        operator=passive_cable_operator(6, leak=0.08, coupling=0.18),
        threshold=0.32,
        slope=0.03,
        gain=gain,
        conductance_decay=0.65,
        reversal=1.0,
        state=np.array([0.0, 0.05, 0.10, 0.05, 0.0, 0.0]),
    )


def _event(position: int, amplitude: float = 0.4) -> np.ndarray:
    event = np.zeros(6, dtype=float)
    event[position] = amplitude
    return event


def _run_sequence(gain: float, first: np.ndarray, second: np.ndarray) -> np.ndarray:
    branch = _branch(gain)
    branch.step(first)
    branch.step(second)
    return branch.state.copy()


def _after_first(gain: float, event: np.ndarray) -> ActiveCableBranch:
    branch = _branch(gain)
    branch.step(event)
    return branch


def _commutator_ratio(first: np.ndarray, second: np.ndarray) -> float:
    commutator = first @ second - second @ first
    scale = 0.5 * (float(np.linalg.norm(first @ second)) + float(np.linalg.norm(second @ first)))
    if scale == 0.0:
        return 0.0
    return float(np.linalg.norm(commutator) / scale)


def run_order_gate() -> dict[str, object]:
    """Separate ordinary linear sequence memory from state-conditioned operator order.

    A fixed linear cable can already distinguish A->B from B->A because the
    first event receives one extra propagation/decay step.  That fact is kept
    as the gain-zero control rather than mislabeled noncommutativity.

    The active test asks two stricter questions:
      1. does local voltage-dependent state add an order interaction beyond the
         gain-zero sequence difference?
      2. after A versus B arrives first, do the resulting local Jacobians fail
         to commute even though the gain-zero Jacobian remains fixed?
    """
    event_a = _event(1)
    event_b = _event(2)

    active_ab = _run_sequence(1.0, event_a, event_b)
    active_ba = _run_sequence(1.0, event_b, event_a)
    control_ab = _run_sequence(0.0, event_a, event_b)
    control_ba = _run_sequence(0.0, event_b, event_a)

    active_difference = active_ab - active_ba
    control_difference = control_ab - control_ba

    active_after_a = _after_first(1.0, event_a)
    active_after_b = _after_first(1.0, event_b)
    control_after_a = _after_first(0.0, event_a)
    control_after_b = _after_first(0.0, event_b)

    active_j_a = active_modal_jacobian(active_after_a)
    active_j_b = active_modal_jacobian(active_after_b)
    control_j_a = active_modal_jacobian(control_after_a)
    control_j_b = active_modal_jacobian(control_after_b)

    active = {
        "sequence_order_gap": float(np.linalg.norm(active_difference)),
        "nonlinear_order_excess_norm": float(np.linalg.norm(active_difference - control_difference)),
        "commutator_ratio": _commutator_ratio(active_j_a, active_j_b),
        "first_event_operator_angle_degrees": matrix_angle_degrees(active_j_a, active_j_b),
        "first_event_relative_operator_change": float(
            np.linalg.norm(active_j_a - active_j_b) / np.linalg.norm(active_j_a)
        ),
    }
    control = {
        "gain_zero_sequence_order_gap": float(np.linalg.norm(control_difference)),
        "gain_zero_commutator_ratio": _commutator_ratio(control_j_a, control_j_b),
        "gain_zero_first_event_operator_angle_degrees": matrix_angle_degrees(control_j_a, control_j_b),
    }

    verdict = (
        "PASS_STATE_CONDITIONED_EVENT_ORDER"
        if control["gain_zero_commutator_ratio"] < 1e-8
        and active["commutator_ratio"] > 0.05
        and active["first_event_operator_angle_degrees"] > 5.0
        and active["sequence_order_gap"] > 1.5 * control["gain_zero_sequence_order_gap"]
        and active["nonlinear_order_excess_norm"] > 0.10
        else "FAIL_STATE_CONDITIONED_EVENT_ORDER"
    )

    return {
        "configuration": {
            "compartments": 6,
            "event_a_position": 1,
            "event_b_position": 2,
            "event_amplitude": 0.4,
            "initial_state": [0.0, 0.05, 0.10, 0.05, 0.0, 0.0],
            "threshold": 0.32,
            "slope": 0.03,
            "conductance_decay": 0.65,
            "leak": 0.08,
            "coupling": 0.18,
        },
        "control": control,
        "active": active,
        "claim_boundary": {
            "linear_sequence_order_can_exist": True,
            "raw_ab_vs_ba_difference_alone_proves_noncommutativity": False,
            "active_state_changes_local_operator": True,
            "active_first_event_operators_fail_to_commute": active["commutator_ratio"] > 0.05,
            "note": "This is a deterministic synthetic mechanism witness. It does not establish that biological dendrites use this exact gate or that morphology is uniquely required for order-sensitive computation.",
        },
        "verdict": verdict,
    }

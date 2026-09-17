from __future__ import annotations

import numpy as np

from .active import ActiveCableBranch
from .cable import passive_cable_operator


N = 6
INITIAL_STATE = np.array([0.0, 0.05, 0.10, 0.05, 0.0, 0.0], dtype=float)


def _event(position: int, amplitude: float = 0.4) -> np.ndarray:
    u = np.zeros(N, dtype=float)
    u[position] = amplitude
    return u


def _initial_snapshot() -> np.ndarray:
    return np.concatenate([INITIAL_STATE, np.zeros(N, dtype=float)])


def _branch(gain: float, snapshot: np.ndarray) -> ActiveCableBranch:
    s = np.asarray(snapshot, dtype=float)
    if s.shape != (2 * N,):
        raise ValueError("snapshot must contain voltage and conductance state")
    return ActiveCableBranch(
        operator=passive_cable_operator(N, leak=0.08, coupling=0.18),
        threshold=0.32,
        slope=0.03,
        gain=gain,
        conductance_decay=0.65,
        reversal=1.0,
        state=s[:N],
        conductance=s[N:],
    )


def _step_snapshot(gain: float, snapshot: np.ndarray, event: np.ndarray) -> np.ndarray:
    branch = _branch(gain, snapshot)
    branch.step(np.asarray(event, dtype=float))
    return np.concatenate([branch.state, branch.conductance])


def _sequence_snapshot(gain: float, snapshot: np.ndarray, events: tuple[np.ndarray, ...]) -> np.ndarray:
    out = np.asarray(snapshot, dtype=float).copy()
    for event in events:
        out = _step_snapshot(gain, out, event)
    return out


def _step_jacobian(gain: float, snapshot: np.ndarray, event: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    x = np.asarray(snapshot, dtype=float)
    baseline = _step_snapshot(gain, x, event)
    jac = np.empty((x.size, x.size), dtype=float)
    for column in range(x.size):
        perturbed = x.copy()
        perturbed[column] += epsilon
        jac[:, column] = (_step_snapshot(gain, perturbed, event) - baseline) / epsilon
    return jac


def _sequence_jacobian(
    gain: float,
    snapshot: np.ndarray,
    events: tuple[np.ndarray, ...],
    epsilon: float = 1e-6,
) -> np.ndarray:
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    x = np.asarray(snapshot, dtype=float)
    baseline = _sequence_snapshot(gain, x, events)
    jac = np.empty((x.size, x.size), dtype=float)
    for column in range(x.size):
        perturbed = x.copy()
        perturbed[column] += epsilon
        jac[:, column] = (_sequence_snapshot(gain, perturbed, events) - baseline) / epsilon
    return jac


def _relative_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    denom = float(np.linalg.norm(actual))
    if denom == 0.0:
        return float(np.linalg.norm(actual - predicted))
    return float(np.linalg.norm(actual - predicted) / denom)


def _gap_ratio(first: np.ndarray, second: np.ndarray) -> float:
    scale = 0.5 * (float(np.linalg.norm(first)) + float(np.linalg.norm(second)))
    if scale == 0.0:
        return 0.0
    return float(np.linalg.norm(first - second) / scale)


def _single_fixed_operator_error(first: np.ndarray, second: np.ndarray) -> float:
    """Best one-matrix least-squares representative of two equally weighted operators."""
    fixed = 0.5 * (first + second)
    numerator = np.sqrt(float(np.linalg.norm(first - fixed) ** 2 + np.linalg.norm(second - fixed) ** 2))
    denominator = np.sqrt(float(np.linalg.norm(first) ** 2 + np.linalg.norm(second) ** 2))
    if denominator == 0.0:
        return float(numerator)
    return float(numerator / denominator)


def _condition(gain: float) -> dict[str, float]:
    x0 = _initial_snapshot()
    event_a = _event(1)
    event_b = _event(2)

    after_a = _step_snapshot(gain, x0, event_a)
    after_b = _step_snapshot(gain, x0, event_b)

    j_a0 = _step_jacobian(gain, x0, event_a)
    j_b0 = _step_jacobian(gain, x0, event_b)
    j_b_after_a = _step_jacobian(gain, after_a, event_b)
    j_a_after_b = _step_jacobian(gain, after_b, event_a)

    predicted_ab = j_b_after_a @ j_a0
    predicted_ba = j_a_after_b @ j_b0
    actual_ab = _sequence_jacobian(gain, x0, (event_a, event_b))
    actual_ba = _sequence_jacobian(gain, x0, (event_b, event_a))

    return {
        "sequence_jacobian_gap_ratio": _gap_ratio(actual_ab, actual_ba),
        "chain_rule_relative_error": max(
            _relative_error(actual_ab, predicted_ab),
            _relative_error(actual_ba, predicted_ba),
        ),
        "single_fixed_operator_relative_error": _single_fixed_operator_error(actual_ab, actual_ba),
        "ab_operator_norm": float(np.linalg.norm(actual_ab)),
        "ba_operator_norm": float(np.linalg.norm(actual_ba)),
    }


def run_composition_gate() -> dict[str, object]:
    """Test whether event operations compose through state-conditioned local Jacobians.

    The gain-zero branch retains ordinary state/history but has one fixed
    derivative with respect to the full resident state [voltage, conductance].
    Therefore A->B and B->A may end at different states, yet their two-step
    Jacobians with respect to the starting state are the same.

    In the active branch, the first event changes the local susceptibility seen
    by the second event. The two-step derivative should then depend on order,
    while the chain rule using the context-specific one-step Jacobians should
    still reconstruct each two-step operator.
    """
    control = _condition(0.0)
    active = _condition(1.0)

    verdict = (
        "PASS_STATE_CONDITIONED_OPERATOR_COMPOSITION"
        if control["sequence_jacobian_gap_ratio"] < 1e-8
        and active["sequence_jacobian_gap_ratio"] > 0.05
        and control["chain_rule_relative_error"] < 1e-6
        and active["chain_rule_relative_error"] < 1e-4
        and active["single_fixed_operator_relative_error"] > 0.02
        else "FAIL_STATE_CONDITIONED_OPERATOR_COMPOSITION"
    )

    return {
        "configuration": {
            "compartments": N,
            "extended_state_size": 2 * N,
            "event_a_position": 1,
            "event_b_position": 2,
            "event_amplitude": 0.4,
            "initial_voltage": INITIAL_STATE.tolist(),
            "initial_conductance": [0.0] * N,
            "threshold": 0.32,
            "slope": 0.03,
            "conductance_decay": 0.65,
            "leak": 0.08,
            "coupling": 0.18,
            "finite_difference_epsilon": 1e-6,
        },
        "control": control,
        "active": active,
        "claim_boundary": {
            "different_final_states_alone_are_not_the_claim": True,
            "gain_zero_keeps_history_but_uses_one_fixed_local_operator": True,
            "active_sequence_uses_context_specific_operator_composition": True,
            "chain_rule_is_a_consistency_check_not_a_novel_theorem": True,
            "note": "This deterministic synthetic witness shows that the current active branch requires context-specific local Jacobians to describe sequence response. It does not establish unique dendritic expressivity or biological implementation.",
        },
        "verdict": verdict,
    }

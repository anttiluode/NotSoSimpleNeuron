import numpy as np

from not_so_simple_neuron.active import ActiveCableBranch
from not_so_simple_neuron.cable import passive_cable_operator


def pair_injection(n: int, i: int, j: int) -> np.ndarray:
    u = np.zeros(n, dtype=float)
    u[i] = 0.5
    u[j] = 0.5
    return u


def test_nearby_equal_charge_pair_recruits_more_active_current_than_crossed_pair():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    near = pair_injection(12, 2, 3)
    far = pair_injection(12, 2, 8)

    near_branch = ActiveCableBranch(A)
    far_branch = ActiveCableBranch(A)
    near_state = near_branch.step(near)
    far_state = far_branch.step(far)

    assert np.isclose(near.sum(), far.sum())
    assert near_branch.last_active_current.sum() > 4.0 * far_branch.last_active_current.sum()
    assert near_state.sum() > far_state.sum() + 0.25


def test_gain_zero_removes_active_close_far_total_response_difference():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    near = pair_injection(12, 2, 3)
    far = pair_injection(12, 2, 8)

    near_branch = ActiveCableBranch(A, gain=0.0)
    far_branch = ActiveCableBranch(A, gain=0.0)

    assert np.isclose(near_branch.step(near).sum(), far_branch.step(far).sum(), atol=1e-12)


def test_conductance_trace_persists_then_decays_after_ping():
    A = passive_cable_operator(12)
    branch = ActiveCableBranch(A, conductance_decay=0.65)
    u = pair_injection(12, 2, 3)

    branch.step(u)
    first = branch.conductance.copy()
    branch.step(np.zeros(12))
    second = branch.conductance.copy()

    assert np.all(second <= first + 1e-15)
    assert np.allclose(second, 0.65 * first)


def test_reset_clears_voltage_conductance_and_active_current():
    A = passive_cable_operator(12)
    branch = ActiveCableBranch(A)
    branch.step(pair_injection(12, 2, 3))
    branch.reset()

    assert np.allclose(branch.state, 0.0)
    assert np.allclose(branch.conductance, 0.0)
    assert np.allclose(branch.last_active_current, 0.0)

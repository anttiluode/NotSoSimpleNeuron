import numpy as np

from not_so_simple_neuron.operator_bank import BranchBank, RouteContact


def test_branch_bank_transfer_matrix_matches_direct_state_space():
    bank = BranchBank.demo()
    omega = 0.31

    H = bank.transfer_matrix(omega)

    z = np.exp(1j * omega)
    direct = bank.readout_matrix @ np.linalg.solve(
        z * np.eye(bank.state_matrix.shape[0], dtype=complex) - bank.state_matrix,
        bank.input_matrix,
    )

    assert H.shape == (bank.branch_count, bank.route_count)
    assert np.allclose(H, direct, atol=1e-12)


def test_same_route_rotates_branch_mixture_with_frequency():
    bank = BranchBank.demo()

    low = bank.route_direction(route=0, omega=0.08)
    high = bank.route_direction(route=0, omega=0.62)
    overlap = abs(np.vdot(low, high))

    assert overlap < 0.92


def test_equal_charge_routes_remain_normalized():
    bank = BranchBank.demo()
    assert np.allclose(bank.route_charge, np.ones(bank.route_count), atol=1e-12)


def test_route_contact_rejects_negative_weight():
    try:
        RouteContact(branch=0, position=0, weight=-0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative route contact weight must be rejected")

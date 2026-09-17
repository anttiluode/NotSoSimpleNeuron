import numpy as np

from not_so_simple_neuron.active import ActiveCableBranch
from not_so_simple_neuron.cable import passive_cable_operator
from not_so_simple_neuron.operator_bank import BranchBank
from not_so_simple_neuron.modal_boundary import (
    active_modal_jacobian,
    matrix_angle_degrees,
    modal_offdiagonal_ratio,
    modal_realization,
)


def test_modal_realization_matches_branch_bank_transfer_exactly():
    bank = BranchBank.demo()
    modal = modal_realization(bank)

    assert modal.state_matrix.shape == bank.state_matrix.shape
    assert modal.input_matrix.shape == bank.input_matrix.shape
    assert modal.readout_matrix.shape == bank.readout_matrix.shape

    errors = []
    for omega in np.linspace(0.0, 0.8, 81):
        z = np.exp(1j * float(omega))
        eye = np.eye(modal.state_matrix.shape[0], dtype=complex)
        H_modal = modal.readout_matrix @ np.linalg.solve(
            z * eye - modal.state_matrix,
            modal.input_matrix,
        )
        errors.append(float(np.max(np.abs(H_modal - bank.transfer_matrix(float(omega))))))

    assert max(errors) < 1e-10


def test_linear_modal_realization_has_no_cross_mode_coupling_within_each_branch():
    bank = BranchBank.demo()
    modal = modal_realization(bank)

    for branch_slice in modal.branch_mode_slices:
        block = modal.state_matrix[branch_slice, branch_slice]
        n = block.shape[0] // 2
        vv = block[:n, :n]
        vw = block[:n, n:]
        wv = block[n:, :n]
        ww = block[n:, n:]

        assert np.max(np.abs(vv - np.diag(np.diag(vv)))) < 1e-12
        assert np.max(np.abs(vw - np.diag(np.diag(vw)))) < 1e-12
        assert np.max(np.abs(wv - np.diag(np.diag(wv)))) < 1e-12
        assert np.max(np.abs(ww - np.diag(np.diag(ww)))) < 1e-12


def _active_context(state, gain=1.0):
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


def test_local_active_gate_breaks_independent_modal_sections():
    state = np.array([0.0, 0.2, 0.45, 0.2, 0.0, 0.0])

    passive_control = active_modal_jacobian(_active_context(state, gain=0.0))
    active = active_modal_jacobian(_active_context(state, gain=1.0))

    assert modal_offdiagonal_ratio(passive_control) < 1e-8
    assert modal_offdiagonal_ratio(active) > 0.20


def test_active_effective_operator_rotates_with_resident_state():
    low = active_modal_jacobian(_active_context([0.0, 0.1, 0.25, 0.1, 0.0, 0.0]))
    near_gate = active_modal_jacobian(_active_context([0.0, 0.2, 0.45, 0.2, 0.0, 0.0]))

    assert matrix_angle_degrees(low, near_gate) > 20.0

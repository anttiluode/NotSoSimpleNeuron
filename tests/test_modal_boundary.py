import numpy as np

from not_so_simple_neuron.operator_bank import BranchBank
from not_so_simple_neuron.modal_boundary import modal_realization


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

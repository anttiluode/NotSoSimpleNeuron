from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .operator_bank import BranchBank


@dataclass(frozen=True)
class ModalRealization:
    """Exact modal-coordinate realization of a linear/quasi-active branch bank."""

    state_matrix: np.ndarray
    input_matrix: np.ndarray
    readout_matrix: np.ndarray
    physical_from_modal: np.ndarray
    branch_mode_slices: tuple[slice, ...]

    def transfer_matrix(self, omega: float) -> np.ndarray:
        z = np.exp(1j * float(omega))
        eye = np.eye(self.state_matrix.shape[0], dtype=complex)
        return self.readout_matrix @ np.linalg.solve(
            z * eye - self.state_matrix,
            self.input_matrix,
        )


def _block_diag(blocks: list[np.ndarray]) -> np.ndarray:
    size = sum(block.shape[0] for block in blocks)
    out = np.zeros((size, size), dtype=float)
    offset = 0
    for block in blocks:
        n = block.shape[0]
        out[offset : offset + n, offset : offset + n] = block
        offset += n
    return out


def modal_realization(bank: BranchBank) -> ModalRealization:
    """Rewrite a BranchBank in independent cable-mode coordinates.

    Each passive cable operator is symmetric, so its orthonormal eigenvectors
    diagonalize the voltage dynamics.  Applying the same spatial basis to the
    recovery variables turns every quasi-active branch into independent
    two-state modal sections.  This is a pure change of coordinates, not a fit.
    """
    transforms: list[np.ndarray] = []
    branch_slices: list[slice] = []
    offset = 0

    for spec, branch_state in zip(bank.branches, bank._state_matrices):
        operator = np.asarray(spec.operator, dtype=float)
        if not np.allclose(operator, operator.T, atol=1e-12):
            raise ValueError("modal_realization requires symmetric branch operators")

        _, phi = np.linalg.eigh(operator)
        n = operator.shape[0]
        zeros = np.zeros_like(phi)
        transform = np.block([[phi, zeros], [zeros, phi]])

        if transform.shape != branch_state.shape:
            raise ValueError("branch state shape does not match modal transform")

        transforms.append(transform)
        branch_slices.append(slice(offset, offset + 2 * n))
        offset += 2 * n

    physical_from_modal = _block_diag(transforms)
    modal_from_physical = physical_from_modal.T

    state_matrix = modal_from_physical @ bank.state_matrix @ physical_from_modal
    input_matrix = modal_from_physical @ bank.input_matrix
    readout_matrix = bank.readout_matrix @ physical_from_modal

    return ModalRealization(
        state_matrix=state_matrix,
        input_matrix=input_matrix,
        readout_matrix=readout_matrix,
        physical_from_modal=physical_from_modal,
        branch_mode_slices=tuple(branch_slices),
    )

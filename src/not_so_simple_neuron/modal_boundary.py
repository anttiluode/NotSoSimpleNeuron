from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .active import ActiveCableBranch
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
    diagonalize the voltage dynamics. Applying the same spatial basis to the
    recovery variables turns every quasi-active branch into independent
    two-state modal sections. This is a pure change of coordinates, not a fit.
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


def _active_next_voltage(branch: ActiveCableBranch, state: np.ndarray) -> np.ndarray:
    """Evaluate one zero-input active step from a fixed resident context."""
    probe = ActiveCableBranch(
        operator=branch.operator,
        threshold=branch.threshold,
        slope=branch.slope,
        gain=branch.gain,
        conductance_decay=branch.conductance_decay,
        reversal=branch.reversal,
        state=np.asarray(state, dtype=float),
        conductance=np.asarray(branch.conductance, dtype=float),
    )
    return probe.step(np.zeros_like(probe.state))


def active_modal_jacobian(branch: ActiveCableBranch, epsilon: float = 1e-6) -> np.ndarray:
    """Local voltage Jacobian expressed in the passive cable eigenbasis.

    Conductance context and all mechanism parameters are held fixed while the
    resident voltage state is perturbed. In the gain-zero control this reduces
    to the passive cable operator and is diagonal in the cable eigenbasis. A
    local state-dependent active term can create cross-mode coupling.
    """
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    operator = np.asarray(branch.operator, dtype=float)
    if not np.allclose(operator, operator.T, atol=1e-12):
        raise ValueError("active_modal_jacobian requires a symmetric cable operator")

    state = np.asarray(branch.state, dtype=float)
    baseline = _active_next_voltage(branch, state)
    jacobian = np.empty((state.size, state.size), dtype=float)
    for column in range(state.size):
        perturbed = state.copy()
        perturbed[column] += epsilon
        jacobian[:, column] = (_active_next_voltage(branch, perturbed) - baseline) / epsilon

    _, phi = np.linalg.eigh(operator)
    return phi.T @ jacobian @ phi


def modal_offdiagonal_ratio(matrix: np.ndarray) -> float:
    """Frobenius fraction carried by cross-mode terms."""
    M = np.asarray(matrix)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("matrix must be square")
    norm = float(np.linalg.norm(M))
    if norm == 0.0:
        return 0.0
    off = M - np.diag(np.diag(M))
    return float(np.linalg.norm(off) / norm)


def matrix_angle_degrees(first: np.ndarray, second: np.ndarray) -> float:
    """Angle between two flattened local operators."""
    a = np.asarray(first).reshape(-1)
    b = np.asarray(second).reshape(-1)
    if a.shape != b.shape:
        raise ValueError("matrices must have matching shapes")
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        raise ValueError("matrix angle is undefined for a zero matrix")
    cosine = float(np.real(np.vdot(a, b)) / denom)
    cosine = float(np.clip(cosine, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)))

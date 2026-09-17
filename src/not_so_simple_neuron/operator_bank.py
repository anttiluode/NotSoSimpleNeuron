from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .cable import passive_cable_operator
from .frequency import ResonantCableBranch


@dataclass(frozen=True)
class RouteContact:
    """One ordinary scalar synaptic contact owned by a route."""

    branch: int
    position: int
    weight: float

    def __post_init__(self) -> None:
        if self.branch < 0:
            raise ValueError("branch must be non-negative")
        if self.position < 0:
            raise ValueError("position must be non-negative")
        if self.weight < 0.0:
            raise ValueError("weight must be non-negative")


@dataclass(frozen=True)
class BranchSpec:
    operator: np.ndarray
    recovery_gain: float
    recovery_decay: float
    recovery_coupling: float
    readout_position: int = 0


class BranchBank:
    """Block-diagonal bank of quasi-active dendritic branches.

    Routes are sparse sets of scalar contacts.  The resulting external transfer
    is a complex matrix H(omega) from route amplitudes to branch readouts.
    """

    def __init__(self, branches: Sequence[BranchSpec], routes: Sequence[Sequence[RouteContact]]):
        if not branches:
            raise ValueError("at least one branch is required")
        if not routes:
            raise ValueError("at least one route is required")

        self.branches = list(branches)
        self.routes = [list(route) for route in routes]
        self._state_matrices: list[np.ndarray] = []
        self._sizes: list[int] = []

        for spec in self.branches:
            operator = np.asarray(spec.operator, dtype=float)
            if operator.ndim != 2 or operator.shape[0] != operator.shape[1]:
                raise ValueError("each branch operator must be square")
            n = operator.shape[0]
            if not (0 <= spec.readout_position < n):
                raise ValueError("readout_position out of range")
            model = ResonantCableBranch(
                operator=operator,
                recovery_gain=spec.recovery_gain,
                recovery_decay=spec.recovery_decay,
                recovery_coupling=spec.recovery_coupling,
            )
            self._state_matrices.append(model.state_matrix)
            self._sizes.append(n)

        for route in self.routes:
            if not route:
                raise ValueError("routes must own at least one contact")
            for contact in route:
                if contact.branch >= len(self.branches):
                    raise ValueError("route contact branch out of range")
                if contact.position >= self._sizes[contact.branch]:
                    raise ValueError("route contact position out of range")

        self.state_matrix = self._block_diag(self._state_matrices)
        self.input_matrix = self._build_input_matrix()
        self.readout_matrix = self._build_readout_matrix()

    @staticmethod
    def _block_diag(blocks: Sequence[np.ndarray]) -> np.ndarray:
        size = sum(block.shape[0] for block in blocks)
        out = np.zeros((size, size), dtype=float)
        offset = 0
        for block in blocks:
            n = block.shape[0]
            out[offset : offset + n, offset : offset + n] = block
            offset += n
        return out

    @property
    def branch_count(self) -> int:
        return len(self.branches)

    @property
    def route_count(self) -> int:
        return len(self.routes)

    @property
    def route_charge(self) -> np.ndarray:
        return np.array([sum(contact.weight for contact in route) for route in self.routes], dtype=float)

    def _branch_state_offset(self, branch: int) -> int:
        return sum(matrix.shape[0] for matrix in self._state_matrices[:branch])

    def _build_input_matrix(self) -> np.ndarray:
        B = np.zeros((self.state_matrix.shape[0], self.route_count), dtype=float)
        for route_index, route in enumerate(self.routes):
            for contact in route:
                offset = self._branch_state_offset(contact.branch)
                B[offset + contact.position, route_index] += contact.weight
        return B

    def _build_readout_matrix(self) -> np.ndarray:
        C = np.zeros((self.branch_count, self.state_matrix.shape[0]), dtype=float)
        for branch_index, spec in enumerate(self.branches):
            offset = self._branch_state_offset(branch_index)
            C[branch_index, offset + spec.readout_position] = 1.0
        return C

    def transfer_matrix(self, omega: float) -> np.ndarray:
        z = np.exp(1j * float(omega))
        eye = np.eye(self.state_matrix.shape[0], dtype=complex)
        return self.readout_matrix @ np.linalg.solve(z * eye - self.state_matrix, self.input_matrix)

    def route_direction(self, route: int, omega: float) -> np.ndarray:
        if not (0 <= route < self.route_count):
            raise ValueError("route out of range")
        vector = self.transfer_matrix(omega)[:, route]
        norm = float(np.linalg.norm(vector))
        if norm == 0.0:
            raise ValueError("route has zero transfer at this frequency")
        return vector / norm

    @classmethod
    def demo(cls) -> "BranchBank":
        """Deterministic four-branch witness used by the v2 operator gate."""
        branch_params = [
            # leak, coupling, recovery_gain, recovery_decay, recovery_coupling
            (0.07, 0.16, 0.45, 0.72, 0.10),
            (0.08, 0.18, 0.50, 0.80, 0.15),
            (0.09, 0.20, 0.55, 0.84, 0.18),
            (0.10, 0.22, 0.60, 0.88, 0.20),
        ]
        branches = [
            BranchSpec(
                operator=passive_cable_operator(6, leak=leak, coupling=coupling),
                recovery_gain=recovery_gain,
                recovery_decay=recovery_decay,
                recovery_coupling=recovery_coupling,
                readout_position=0,
            )
            for leak, coupling, recovery_gain, recovery_decay, recovery_coupling in branch_params
        ]

        routes = [
            [
                RouteContact(0, 3, 0.25),
                RouteContact(1, 3, 0.25),
                RouteContact(2, 3, 0.25),
                RouteContact(3, 3, 0.25),
            ],
            [
                RouteContact(0, 1, 0.35),
                RouteContact(1, 4, 0.25),
                RouteContact(2, 2, 0.25),
                RouteContact(3, 5, 0.15),
            ],
            [
                RouteContact(0, 5, 0.15),
                RouteContact(1, 2, 0.20),
                RouteContact(2, 4, 0.30),
                RouteContact(3, 1, 0.35),
            ],
        ]
        return cls(branches=branches, routes=routes)

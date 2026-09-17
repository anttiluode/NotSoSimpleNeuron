import numpy as np

from not_so_simple_neuron.cable import CableBranch, modal_basis, passive_cable_operator
from not_so_simple_neuron.routes import SpatialRoute


def test_passive_cable_operator_is_stable():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    eigvals = np.linalg.eigvalsh(A)
    assert np.max(np.abs(eigvals)) < 1.0


def test_modal_basis_is_orthonormal_and_reconstructs_operator():
    A = passive_cable_operator(10, leak=0.07, coupling=0.16)
    eigvals, phi = modal_basis(A)
    assert np.allclose(phi.T @ phi, np.eye(10), atol=1e-12)
    assert np.allclose(A, phi @ np.diag(eigvals) @ phi.T, atol=1e-12)


def test_linear_cable_obeys_superposition():
    A = passive_cable_operator(8, leak=0.1, coupling=0.15)
    u = np.zeros(8); u[[1, 4]] = [0.3, 0.7]
    v = np.zeros(8); v[[2, 6]] = [0.6, 0.4]
    b_uv = CableBranch(A); x_uv = b_uv.step(u + v)
    b_u = CableBranch(A); x_u = b_u.step(u)
    b_v = CableBranch(A); x_v = b_v.step(v)
    assert np.allclose(x_uv, x_u + x_v)


def test_routes_normalize_equal_total_charge_but_keep_position():
    r1 = SpatialRoute((1, 3, 7), np.array([2.0, 1.0, 1.0]), 10)
    r2 = SpatialRoute((2, 5, 8), np.array([1.0, 1.0, 2.0]), 10)
    assert np.isclose(r1.injection().sum(), 1.0)
    assert np.isclose(r2.injection().sum(), 1.0)
    assert not np.allclose(r1.injection(), r2.injection())

import numpy as np

from not_so_simple_neuron.learning import spatial_hebb_update
from not_so_simple_neuron.routes import SpatialRoute


def test_inactive_route_does_not_change():
    route = SpatialRoute((0, 2, 4), np.ones(3), 6)
    before = route.weights.copy()
    spatial_hebb_update(route, np.array([0., 1., 0., 1., 0., 1.]), event=0.0, eta=0.1)
    assert np.allclose(route.weights, before)


def test_update_preserves_nonnegative_unit_mass():
    route = SpatialRoute((0, 2, 4), np.ones(3), 6)
    spatial_hebb_update(route, np.array([0.9, 0., 0.2, 0., 0.1, 0.]), event=1.0, eta=0.2)
    assert np.all(route.weights >= 0.0)
    assert np.isclose(route.weights.sum(), 1.0)


def test_repeated_pairing_moves_weight_toward_locally_active_contact():
    route = SpatialRoute((0, 2, 4), np.ones(3), 6)
    state = np.array([1.0, 0.0, 0.1, 0.0, 0.05, 0.0])
    for _ in range(60):
        spatial_hebb_update(route, state, event=1.0, eta=0.05)
    assert route.weights[0] > 0.75
    assert route.weights[0] > route.weights[1] > route.weights[2]

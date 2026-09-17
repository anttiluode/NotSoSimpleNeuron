import numpy as np

from not_so_simple_neuron.cable import passive_cable_operator
from not_so_simple_neuron.frequency import (
    PointResonator,
    ResonantCableBranch,
    best_point_attacker,
    local_frequency_response,
    pulse_train_response,
)


def test_passive_local_transfer_peaks_at_dc():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    site = 5
    omegas = np.linspace(0.0, np.pi, 257)
    b = np.zeros(12)
    b[site] = 1.0
    response = local_frequency_response(A, b, b, omegas)

    assert int(np.argmax(response)) == 0
    assert np.all(np.diff(response) <= 1e-10)


def test_nominal_quasi_active_branch_has_nonzero_resonant_peak():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    branch = ResonantCableBranch(A)
    omegas = np.linspace(0.0, np.pi, 257)
    response = branch.local_frequency_response(site=5, omegas=omegas)
    peak_index = int(np.argmax(response))

    assert branch.spectral_radius < 1.0
    assert peak_index > 0
    assert omegas[peak_index] > 0.15
    assert omegas[peak_index] < 0.40
    assert response[peak_index] > 1.25 * response[0]


def test_same_site_equal_count_ping_trains_differ_by_interval():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)

    fast = pulse_train_response(
        lambda: ResonantCableBranch(A), site=5, interval=4, count=24, burn_in=8
    )
    slow = pulse_train_response(
        lambda: ResonantCableBranch(A), site=5, interval=14, count=24, burn_in=8
    )

    assert fast["ping_count"] == slow["ping_count"] == 24
    assert np.isclose(fast["total_charge"], slow["total_charge"])
    assert abs(fast["mean_post_ping_voltage"] - slow["mean_post_ping_voltage"]) > 0.05


def test_tuned_point_attacker_reports_outcome_instead_of_being_forced_to_lose():
    A = passive_cable_operator(12, leak=0.08, coupling=0.18)
    branch = ResonantCableBranch(A)
    omegas = np.linspace(0.0, np.pi, 257)
    branch_response = branch.local_frequency_response(site=5, omegas=omegas)

    attack = best_point_attacker(omegas, branch_response)

    assert 0.0 < attack["persistence"] < 1.0
    assert attack["spectral_radius"] < 1.0
    assert attack["outcome"] in {"POINT_MATCHES_OR_BEATS", "BRANCH_BETTER", "TIE"}
    assert attack["point_peak_to_dc"] > 1.0
    assert attack["branch_peak_to_dc"] > 1.0


def test_point_resonator_reset_clears_both_states():
    point = PointResonator(persistence=0.9)
    point.step(1.0)
    point.step(0.0)
    point.reset()

    assert point.voltage == 0.0
    assert point.recovery == 0.0

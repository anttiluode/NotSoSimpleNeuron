import numpy as np

from not_so_simple_neuron.active_experiment import run_v1_suite, run_v1_world, spatial_xor_patterns


def test_spatial_xor_patterns_are_equal_charge_and_have_identical_centroids():
    patterns = spatial_xor_patterns(12, a=2, b=8)
    positive = np.stack(patterns["positive"])
    negative = np.stack(patterns["negative"])

    assert positive.shape == (2, 12)
    assert negative.shape == (2, 12)
    assert np.allclose(positive.sum(axis=1), 1.0)
    assert np.allclose(negative.sum(axis=1), 1.0)
    assert np.allclose(positive.mean(axis=0), negative.mean(axis=0), atol=1e-12)


def test_linear_point_score_sum_identity_blocks_perfect_threshold_separation():
    patterns = spatial_xor_patterns(12, a=2, b=8)
    positive = np.stack(patterns["positive"])
    negative = np.stack(patterns["negative"])
    weights = np.array([0.4, -0.9, 1.3, -0.2, 0.7, 0.1, -1.1, 0.8, -0.5, 1.6, 0.2, -0.3])
    bias = 0.37

    positive_scores = positive @ weights + bias
    negative_scores = negative @ weights + bias

    assert np.isclose(positive_scores.sum(), negative_scores.sum(), atol=1e-12)


def test_one_nominal_v1_world_passes_all_controls():
    result = run_v1_world(0, regime="nominal")

    assert result["passive_gap"] < 1e-12
    assert result["centroid_gap"] < 1e-12
    assert result["linear_score_sum_error"] < 1e-12
    assert result["gain_zero_gap"] < 1e-12
    assert result["active_margin"] > 0.0
    assert result["active_ratio"] > 1.0
    assert result["verdict"] == "PASS_ACTIVE_LOCAL_INTERACTION"


def test_64_world_v1_suite_keeps_nominal_gate_and_stress_boundary():
    receipt = run_v1_suite(seeds=64)
    nominal = receipt["nominal"]
    stress = receipt["stress"]

    assert receipt["seeds"] == 64
    assert nominal["all_pass"] is True
    assert nominal["worst_active_margin"] > 0.20
    assert nominal["mean_active_ratio"] > 1.20
    assert nominal["max_passive_gap"] < 1e-12
    assert nominal["max_gain_zero_gap"] < 1e-12

    # The broad range is deliberately not tuned into a universal success.
    assert 0.90 < stress["pass_fraction"] < 1.0
    assert stress["worst_active_margin"] < 0.0
    assert len(stress["reversal_worlds"]) >= 1
    assert stress["max_passive_gap"] < 1e-12
    assert stress["max_gain_zero_gap"] < 1e-12

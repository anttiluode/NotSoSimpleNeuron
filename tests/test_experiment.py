from not_so_simple_neuron.experiment import run_experiment, run_seed


def test_run_seed_reports_all_v0_gates():
    r = run_seed(3, n_compartments=12, train_steps=300)
    assert r["gate0"]["stable"]
    assert r["gate0"]["superposition_error"] < 1e-12
    assert r["gate1"]["point_scalar_separation"] == 0.0
    assert 1 < r["gate1"]["contacts_per_route"] < 12
    assert r["gate1"]["spatial_response_separation"] > 0.1
    assert r["gate1"]["modal_fingerprint_separation"] > 0.1
    assert r["gate2"]["paired_alignment"] > r["gate2"]["shuffled_alignment"] + 0.05
    assert r["gate2"]["multisite_response_alignment"] > r["gate2"]["best_single_site_alignment"] + 0.02
    assert abs(r["gate2"]["route1_total_strength"] - 1.0) < 1e-12
    assert abs(r["gate2"]["route2_total_strength"] - 1.0) < 1e-12
    assert r["gate3"]["knee_pair_gain"] > r["gate3"]["linear_pair_gain"] * 1.25


def test_experiment_aggregates_seed_results_deterministically():
    a = run_experiment(range(8), n_compartments=12, train_steps=250)
    b = run_experiment(range(8), n_compartments=12, train_steps=250)
    assert a == b
    assert a["seeds"] == 8
    assert a["verdicts"]["PASS_CABLE_INVARIANTS"]
    assert a["verdicts"]["PASS_GEOMETRY_EXPANDS_PING"]
    assert a["verdicts"]["PASS_DISTRIBUTED_SCALAR_LEARNING"]
    assert a["verdicts"]["KNEE_RETAINS_ROLE"]

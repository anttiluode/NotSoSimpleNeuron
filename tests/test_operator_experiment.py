from not_so_simple_neuron.operator_experiment import run_operator_gate


def test_operator_gate_records_frequency_dependent_weight_and_attackers():
    receipt = run_operator_gate()

    assert receipt["invariants"]["equal_route_charge"] is True
    assert receipt["invariants"]["max_transfer_identity_error"] < 1e-12
    assert receipt["route_rotation"]["route_0_low_high_overlap"] < 0.5
    assert receipt["static_attacker"]["held_relative_error"] > 0.5
    assert receipt["point_bank_attacker"]["relative_error"] < receipt["static_attacker"]["held_relative_error"]
    assert receipt["point_bank_attacker"]["relative_error"] > 0.0

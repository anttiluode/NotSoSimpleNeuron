from not_so_simple_neuron.composition_experiment import run_composition_gate


def test_composition_gate_distinguishes_fixed_memory_from_state_conditioned_operator_composition():
    receipt = run_composition_gate()

    assert receipt["control"]["sequence_jacobian_gap_ratio"] < 1e-8
    assert receipt["active"]["sequence_jacobian_gap_ratio"] > 0.05
    assert receipt["control"]["chain_rule_relative_error"] < 1e-6
    assert receipt["active"]["chain_rule_relative_error"] < 1e-4
    assert receipt["active"]["single_fixed_operator_relative_error"] > 0.02
    assert receipt["verdict"] == "PASS_STATE_CONDITIONED_OPERATOR_COMPOSITION"

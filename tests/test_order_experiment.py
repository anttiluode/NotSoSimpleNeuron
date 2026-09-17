from not_so_simple_neuron.order_experiment import run_order_gate


def test_order_gate_separates_linear_memory_from_state_conditioned_operator_order():
    receipt = run_order_gate()

    assert receipt["control"]["gain_zero_commutator_ratio"] < 1e-8
    assert receipt["active"]["commutator_ratio"] > 0.05
    assert receipt["active"]["first_event_operator_angle_degrees"] > 5.0
    assert receipt["active"]["sequence_order_gap"] > 1.5 * receipt["control"]["gain_zero_sequence_order_gap"]
    assert receipt["active"]["nonlinear_order_excess_norm"] > 0.10
    assert receipt["verdict"] == "PASS_STATE_CONDITIONED_EVENT_ORDER"

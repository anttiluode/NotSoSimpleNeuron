from not_so_simple_neuron.modal_boundary_experiment import run_modal_boundary_gate


def test_modal_boundary_receipt_freezes_linear_equivalence_and_active_break():
    receipt = run_modal_boundary_gate()

    assert receipt["linear_equivalence"]["max_transfer_error"] < 1e-10
    assert receipt["linear_equivalence"]["max_cross_mode_ratio"] < 1e-10
    assert receipt["active_boundary"]["gain_zero_cross_mode_ratio"] < 1e-8
    assert receipt["active_boundary"]["active_cross_mode_ratio"] > 0.20
    assert receipt["active_boundary"]["resident_state_jacobian_rotation_degrees"] > 20.0
    assert receipt["verdict"] == "PASS_LINEAR_IS_BASIS_ACTIVE_STATE_COUPLES_MODES"

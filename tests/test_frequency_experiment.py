from not_so_simple_neuron.frequency_experiment import run_frequency_gate


def test_frequency_gate_separates_low_pass_from_resonance_and_reports_attacker():
    receipt = run_frequency_gate()

    assert receipt["verdict"] == "PASS_TEMPORAL_ADDRESSING_POINT_NOT_NEEDED_FOR_CLAIM"
    assert receipt["passive"]["peak_frequency"] == 0.0
    assert receipt["resonant"]["peak_frequency"] > 0.15
    assert receipt["resonant"]["peak_to_dc"] > 1.5

    # Same number of same-site pings: passive accumulation prefers the dense
    # train, while the recovery variable creates a band-preferring reversal.
    assert receipt["ping_probe"]["passive_fast_minus_preferred"] > 0.30
    assert receipt["ping_probe"]["resonant_preferred_minus_fast"] > 0.10
    assert receipt["ping_probe"]["equal_total_charge"] is True

    # A tuned two-state point resonator is a real attacker, not a straw man.
    assert receipt["point_attacker"]["outcome"] in {
        "POINT_MATCHES_OR_BEATS",
        "BRANCH_BETTER",
        "TIE",
    }

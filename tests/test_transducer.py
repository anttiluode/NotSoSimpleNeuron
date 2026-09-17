import numpy as np

from not_so_simple_neuron.transducer import DirectTransducer, LeakyTraceTransducer, SoftKneeTransducer


def test_all_transducers_match_first_isolated_unit_event():
    ts = [DirectTransducer(), LeakyTraceTransducer(0.75), SoftKneeTransducer(0.75, 1.2, 0.18)]
    vals = [t.step(1.0) for t in ts]
    assert np.allclose(vals, [1.0, 1.0, 1.0], atol=1e-12)


def test_soft_knee_amplifies_close_pair_relative_to_linear_trace():
    lin = LeakyTraceTransducer(0.75)
    knee = SoftKneeTransducer(0.75, 1.2, 0.18)
    lin.step(1.0); knee.step(1.0)
    pair_lin = lin.step(1.0)
    pair_knee = knee.step(1.0)
    assert pair_knee > pair_lin * 1.25

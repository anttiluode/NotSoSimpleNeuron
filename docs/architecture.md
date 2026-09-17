# Minimal architecture under test

The current synthetic neuron is intentionally decomposed into independently attackable mechanisms: sparse spatial route contacts, passive cable transport, optional quasi-active recovery dynamics, optional local voltage-dependent conductance, and later soma/AIS stages. This decomposition exists so each added biological-looking mechanism can be removed or replaced without changing the rest of the experiment.

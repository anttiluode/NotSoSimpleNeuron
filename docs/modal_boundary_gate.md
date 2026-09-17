# Modal boundary gate

This gate asks a deliberately adversarial question:

> Is the linear/quasi-active dendritic branch bank doing anything that a degree-matched modal/point realization cannot do?

## Linear result: exact collapse

For each symmetric passive cable operator `A = Phi Lambda Phi.T`, apply the same orthogonal basis `Phi` to voltage and recovery state. The quasi-active branch becomes a collection of independent two-state modal sections.

Across the four-branch, 48-state v2 machine and 81 frequencies:

- maximum transfer error between the physical cable bank and the modal realization: **4.56e-15**;
- maximum cross-mode coupling ratio in the modal state matrix: **4.53e-16**.

No parameters are fitted. This is an orthogonal similarity transform.

So the linear boundary is now explicit:

> **The v2 branch bank has no morphology-unique linear expressivity. It is exactly the same 48-state LTI system written in physical cable coordinates or independent modal coordinates.**

## Active result: local state couples modes

The second half freezes one six-compartment active branch. Synaptic conductance pattern, cable, and all mechanism parameters are held fixed. Only resident voltage state changes.

We numerically linearize one zero-input update with respect to resident voltage and express that local Jacobian in the passive cable eigenbasis.

Frozen results:

- gain-zero cross-mode ratio: **2.30e-11**;
- active cross-mode ratio near the voltage gate: **0.582296**;
- angle between the active local Jacobian in a low-state context and a near-gate context: **34.3168 degrees**;
- relative Jacobian change: **1.16429**.

This identifies the boundary cleanly. In the gain-zero control the eigenmodes remain independent. Once the local voltage-dependent mechanism engages, a spatially local operation becomes cross-mode coupling in modal coordinates, and the effective local operator changes with resident state.

The earned statement is therefore narrower than "morphology computes more":

> **A fixed modal bank exactly reproduces the linear dendrite; local state-dependent spatial chemistry is where that one fixed modal decomposition stops describing the whole machine globally.**

This still does not prove a morphology efficiency advantage. A sufficiently rich nonlinear non-morphological model may reproduce the same family. The next gate must compare state-conditioned operator families under matched learnable-parameter and state budgets.

Frozen receipt: `results/modal_boundary.json`.

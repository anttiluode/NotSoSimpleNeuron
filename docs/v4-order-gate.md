# v4 order gate

## Question

Does event order change the active branch for a reason stronger than ordinary linear dynamical memory?

A fixed linear cable can already produce different final states for `A -> B` and `B -> A`, because the first event receives an extra propagation/decay step. Therefore a raw sequence difference is not evidence that the local operator itself changed.

## Stronger test

Use the existing six-compartment active branch and compare two equal events at adjacent positions.

Measure:

1. the raw sequence-order gap for gain zero and active gain;
2. the active residual after subtracting the gain-zero order difference;
3. the local numerical Jacobian after A is first versus after B is first;
4. the normalized commutator

```text
[J_A, J_B] = J_A J_B - J_B J_A
```

The gain-zero control should have the same fixed local operator after either first event, so its commutator should be numerical zero. The active branch passes only if the first event changes the local Jacobian enough that the two local operators differ and fail to commute.

## Frozen result

See `results/order_gate.json`.

- gain-zero sequence-order gap: `0.1160782081`
- active sequence-order gap: `0.2710397609`
- active nonlinear order excess: `0.1603751457`
- gain-zero commutator ratio: `7.86e-12`
- active commutator ratio: `0.1293391844`
- gain-zero operator angle: `0.0 deg`
- active first-event operator angle: `12.93466864 deg`

Verdict: `PASS_STATE_CONDITIONED_EVENT_ORDER`.

## Claim boundary

This demonstrates a deterministic synthetic mechanism: the first event changes the active local operator encountered by the second. It does not establish that biological dendrites use this exact mechanism, that morphology is uniquely required for order-sensitive computation, or that a broad noncommutative-algebra interpretation has been established.

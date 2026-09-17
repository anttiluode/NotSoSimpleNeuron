# Active Branch Gate Design

## Question

Can a short dendritic cable earn a computational role beyond passive spatial expansion by adding one local voltage-dependent nonlinear mechanism?

The v1 gate must distinguish **local coincidence** from matched total input. It must not rely on route identity, learned labels, or a different total charge.

## Minimal active mechanism

Keep the v0 passive cable operator `A`. Add a synthetic NMDA-like conductance trace `g` at each cable compartment.

For one step with injection `u`:

```text
g <- conductance_decay * g + u
v_pre <- A @ (x + u)
mg_gate <- sigmoid((v_pre - threshold) / slope)
I_active <- gain * g * mg_gate * max(reversal - v_pre, 0)
x <- v_pre + I_active
```

This is deliberately not a biophysical NMDA model. It preserves three mechanically relevant ingredients only:

1. local transmitter/conductance history;
2. voltage-dependent gating;
3. a saturating reversal term that prevents unbounded positive feedback.

The conductance trace gives a short memory while the voltage gate makes nearby coincident contacts interact through cable spread.

## XOR-like spatial test

Choose four interior contact positions `a, a+1, b, b+1` with two well separated local neighborhoods.

The positive class is two within-neighborhood pairs:

```text
(a, a+1)
(b, b+1)
```

The negative class is two crossed pairs:

```text
(a, b)
(a+1, b+1)
```

Every pattern contains two `0.5` pings, so total injected charge is exactly one.

The class centroids are identical: every one of the four positions contributes exactly once to each class. Therefore a single point neuron of the form `f(w @ u + bias)` with a monotone threshold cannot strictly separate all four patterns. The sum of the two positive linear scores equals the sum of the two negative linear scores, so putting both positives above one threshold and both negatives below it is impossible.

The active cable should classify all four using the same scalar readout: total branch response after one active step. Nearby contacts raise each other's local cable voltage enough to open the voltage gate; crossed contacts do not.

## Controls

- **Passive total-response control:** passive cable total response must be identical for all four equal-charge patterns up to numerical tolerance.
- **Linear point control:** positive and negative input centroids must match exactly, and the score-sum identity above must hold for arbitrary test weights.
- **No-active-current ablation:** setting `gain=0` must remove the close/far separation in total branch response.
- **Position translation:** the same mechanism must work for multiple interior choices of `a,b`.
- **Parameter worlds:** the gate must survive 64 deterministic worlds varying passive leak/coupling and active threshold/slope/gain within a fixed predeclared range.

## Frozen v1 success rule

For every one of 64 deterministic worlds:

1. passive total-response close/far gap `< 1e-12`;
2. active minimum positive score is greater than active maximum negative score;
3. class centroids match within `1e-12`;
4. gain-zero ablation has close/far gap `< 1e-12`.

Aggregate receipt records the worst active margin and mean active close/far ratio.

## Interpretation limit

Passing v1 would establish only this synthetic mechanism claim:

> local cable pooling plus a voltage-dependent conductance can create a cheap nonlinear spatial coincidence feature that a single linear-threshold point unit cannot perfectly reproduce.

It would not establish that biological dendrites use this exact rule, that dendrites are generally superior to multilayer point networks, or that the mechanism is novel in computational neuroscience.

## Next gate

Only after v1 passes do we build a bank/ring of several branches and allow one route to own contacts across branches.
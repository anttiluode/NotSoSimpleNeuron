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

## Nominal gate and stress sweep

A scratch calculation before production implementation exposed an important boundary in the originally proposed broad parameter sweep: when coupling is weak and threshold is low, both nearby and crossed patterns can open the voltage gate. Once both are saturated, the lower-voltage crossed pattern can receive *more* current because it has more reversal headroom. That is a real property of this mechanism, not a nuisance to tune away.

Therefore v1 has two receipts:

### Nominal 64-world gate

The passive cable is fixed at `leak=0.08`, `coupling=0.18`. Across deterministic seeds we vary:

- threshold `[0.315, 0.325]`;
- slope `[0.015, 0.025]`;
- gain `[0.6, 1.2]`;
- the two translated interior neighborhoods.

All 64 nominal worlds must satisfy:

1. passive close/far total-response gap `< 1e-12`;
2. active minimum positive score `>` active maximum negative score;
3. class centroid gap `< 1e-12`;
4. gain-zero close/far gap `< 1e-12`.

### Broad 64-world stress sweep

We deliberately vary beyond the clean operating regime:

- leak `[0.04, 0.12]`;
- coupling `[0.12, 0.24]`;
- threshold `[0.30, 0.34]`;
- slope `[0.012, 0.025]`;
- gain `[0.6, 1.2]`.

This sweep is **characterization, not a pass-all gate**. The receipt records pass fraction, worst margin, and the parameters of any reversal worlds. We keep those failures because they identify when local voltage selectivity collapses into saturation/reversal-headroom behavior.

## Interpretation limit

Passing the nominal gate would establish only this synthetic mechanism claim:

> local cable pooling plus a voltage-dependent conductance can create a cheap nonlinear spatial coincidence feature that a single linear-threshold point unit cannot perfectly reproduce, over a finite operating regime.

The broad stress sweep explicitly prevents the stronger claim that the mechanism is universally adjacency-selective.

It would not establish that biological dendrites use this exact rule, that dendrites are generally superior to multilayer point networks, or that the mechanism is novel in computational neuroscience. A two-layer point network can implement the same kind of interaction; the question here is whether putting the nonlinearity locally on the branch gives our synthetic architecture a useful factorization.

## Next gate

Only after v1 is characterized do we build a bank/ring of several branches and allow one route to own contacts across branches.
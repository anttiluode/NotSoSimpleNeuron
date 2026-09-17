# v1 — Local active branch

v0 showed that several scalar synapses at different cable positions can turn one tiny route event into a distributed spatial/modal response.

v1 asks the next question:

> Can the branch do more than linear expansion? Can **where two pings meet** change the result even when total input is matched?

## The minimal active mechanism

`ActiveCableBranch` adds one synthetic NMDA-like current to the passive cable. It is intentionally not a channel-accurate model.

```text
conductance <- decay * conductance + ping
pre_voltage <- A @ (state + ping)
voltage_gate <- sigmoid((pre_voltage - threshold) / slope)
active_current <- gain * conductance * voltage_gate * max(reversal - pre_voltage, 0)
state <- pre_voltage + active_current
```

Three ingredients matter:

- the route leaves a short local conductance trace;
- cable voltage controls whether that local conductance opens strongly;
- the reversal term saturates the extra current instead of allowing unlimited positive feedback.

For nearby simultaneous contacts, cable spread raises the voltage at both active contacts. Crossed/far contacts carry the same total charge but do not depolarize one another as strongly.

## The balanced spatial-XOR construction

Pick two local neighborhoods:

```text
A: a -- a+1
B: b -- b+1
```

Positive patterns are the two local pairs:

```text
(a, a+1)
(b, b+1)
```

Negative patterns cross the neighborhoods:

```text
(a, b)
(a+1, b+1)
```

Every pattern contains exactly two 0.5 pings.

The construction is balanced: every physical input position appears exactly once in each class. Therefore the positive and negative input centroids are identical.

For any single linear point score

```text
s(u) = w @ u + bias
```

the sum of the two positive scores is exactly the sum of the two negative scores. If both positives were above one threshold while both negatives were below it, those two sums would have to be simultaneously greater and smaller. So a single linear projection plus threshold cannot perfectly solve all four patterns.

A two-layer point network can solve it. That is an important limit: v1 is **not** a unique-expressivity result. It asks whether placing the nonlinearity locally on the cable gives a useful architectural factorization.

## Frozen 64-world receipt

Nominal worlds keep the passive cable at `leak=0.08`, `coupling=0.18`, translate the neighborhoods, and vary active threshold, slope and gain.

- nominal pass count: **64 / 64**;
- worst nominal active margin: **0.302040**;
- mean nominal active margin: **0.429997**;
- mean nominal close/cross response ratio: **1.431748**;
- passive close/cross total-response gap: **0**;
- gain-zero close/cross gap: **0**;
- centroid gap: **0**.

So in the declared operating regime, the local active branch converts spatial coincidence into a scalar feature while matched passive and gain-zero systems cannot.

## The failure is part of the result

The broad stress sweep deliberately varies cable leak/coupling as well as threshold, slope and gain.

It passes **63 / 64** worlds, not 64 / 64.

The reversal world is seed 25:

```text
leak      = 0.0528577
coupling  = 0.1200374
threshold = 0.3086639
slope     = 0.0167844
gain      = 0.6012157
```

Its active margin is **-0.0116691**.

Why? Coupling is weak and threshold is low enough that both local and crossed patterns substantially open the voltage gate. Once the gate is saturated for both, the lower-voltage crossed case has more distance to the synthetic reversal potential and can receive slightly more current.

That failure is useful. The mechanism is not simply "nearby is always bigger." It has an operating regime:

```text
far below voltage knee < nearby around/above knee
```

If both are below the knee, little nonlinear separation occurs. If both saturate above it, reversal headroom can erase or even invert the effect.

## What this adds to the machine

v0:

```text
route positions -> distributed linear state
```

v1:

```text
route positions
      +
local cable voltage
      +
local conductance history
      ->
state-dependent nonlinear interaction
```

So the branch no longer merely stores or expands a vector. It can create a local relational feature: **these two touches happened close enough, at the same time, in the right electrical state.**

That is the first place where the dendrite begins to look like a computational subunit rather than a fancy weight representation.

## Next

The next gate is a small bank/ring of short active branches feeding one soma. One source route will be allowed to own scalar contacts across several branches. The question becomes whether a learned item can be represented as a sparse pattern of touches over the dendritic field while each branch independently performs local nonlinear filtering before the soma mixes them.

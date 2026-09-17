# Frequency Addressing Gate Design

## Question

Where is the information in a nearly binary route event if the event itself carries almost no amplitude code?

This gate tests the smallest temporal answer: information can live in **when identical pings arrive**, and receiver dynamics can decode that timing. It deliberately separates three claims that must not be conflated:

1. a passive cable has multiple decay times and therefore rate/frequency selectivity;
2. adding one recovery state per compartment can create a genuine non-zero-frequency subthreshold resonance;
3. neither fact by itself proves that dendritic morphology is computationally necessary, so a tuned point-resonator attacker is mandatory.

## Models

### Passive cable

Reuse the v0 operator

```text
v[t+1] = A v[t] + u[t]
```

For a periodic small-signal input at angular frequency `omega`, measure the local complex transfer magnitude

```text
H(omega) = C (exp(i omega) I - A)^-1 B
```

at the same injection/readout compartment. The passive control must peak at DC; it may show different low-pass corners but must not be called resonant.

### Quasi-active resonant cable

Add exactly one local recovery variable per compartment:

```text
v[t+1] = A v[t] - g_w w[t] + u[t]
w[t+1] = alpha w[t] + beta v[t]
```

The combined linear state matrix must have spectral radius below one. With the frozen nominal parameters, the local transfer curve must have a maximum at non-zero frequency and a peak above its DC gain.

This is a synthetic quasi-active mechanism, not a detailed `I_h`, potassium, calcium, or NMDA model.

### Point attacker

Use the same two-state equations but remove morphology:

```text
v[t+1] = a v[t] - g_w w[t] + u[t]
w[t+1] = alpha w[t] + beta v[t]
```

Allow `a` to be tuned over a fixed grid. The point model is allowed to match or beat the branch's single-site band selectivity. The receipt records the outcome rather than requiring a dendritic win.

## Ping experiment

Alongside the analytic frequency sweep, drive the same cable compartment with identical positive pings. Two trains have the same ping amplitude and the same number of pings but different inter-ping intervals. Report the response per ping after burn-in. This is the intuitive demonstration that timing changes resident state even when spatial address and total event count are unchanged.

## Frozen claims

The gate passes if all of the following hold:

- passive local transfer is maximal at zero frequency;
- the quasi-active branch is stable;
- the quasi-active branch has a reproducible non-zero resonant peak at nominal parameters;
- identical same-site ping trains with different intervals produce different receiver states;
- the tuned point attacker result is reported explicitly as `POINT_MATCHES_OR_BEATS`, `BRANCH_BETTER`, or `TIE` rather than hidden.

The gate does **not** claim biological eigenfrequency learning, not claim that spikes encode only rate, and not claim a dendritic advantage over a point resonator.

## Relationship to v0 and the active-branch gate

v0 established spatial addressing:

```text
where a ping lands -> modal mixture
```

This gate adds temporal addressing:

```text
when the ping lands -> which receiver timescales are driven
```

The next active-branch gate remains separate: local voltage-dependent conductance asks whether spatial coincidence creates nonlinear interactions beyond passive/quasi-active linear filtering.

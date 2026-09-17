# NotSoSimpleNeuron

> **A tiny routed event can acquire meaning from where it lands, when it lands, what local state it encounters, and what happened immediately before it.**

This repository starts from a question that fell out of [`SimpleNeuron`](https://github.com/anttiluode/SimpleNeuron):

> If an axonal event is nearly binary, how could it steer a receiver along a high-dimensional direction?

The answer has become deliberately more precise as attackers remove weaker stories. A route is not being treated as a magic vector-valued synapse. It is a sparse physical access pattern into receiver dynamics. The effective transformation can depend on spatial landing pattern, event timing, resident state, and event order.

The project currently has seven separate gates:

1. **distributed spatial route** — several ordinary scalar contacts on one passive cable;
2. **temporal addressing** — timing is decoded by receiver dynamics, although a point resonator beats the single-site cable;
3. **active local interaction** — nearby equal-charge inputs recruit a local voltage-dependent interaction that passive superposition cannot;
4. **operator-valued route** — one unchanged route exposes different effective branch-state directions across frequency;
5. **modal boundary** — the full linear/quasi-active cable bank is exactly a modal state-space realization, while local active state breaks the fixed modal decomposition;
6. **event-order gate** — the first event changes the local operator encountered by the second, producing noncommuting local Jacobians in the synthetic active branch;
7. **operator-composition gate** — the full two-event derivative is reconstructed by composing context-specific one-step Jacobians, while one fixed operator cannot represent both event orders.

Every extra mechanism gets a control or attacker. Negative boundaries stay in the result.

---

## v0 — distributed scalar contacts become a route-level vector

One route owns several ordinary non-negative scalar contacts at different positions on a passive dendritic cable:

```text
route r = {(position_j, weight_j)}
```

The branch evolves as

```text
x[t+1] = A @ x[t] + u_r q[t]
```

where `A` is a stable passive cable operator. In its eigenbasis,

```text
z = Phi.T @ u_r
```

so a sparse landing pattern acquires a modal fingerprint because of **where** its contacts land. The event does not carry the vector; the receiver supplies the expansion.

The local learning rule is intentionally simpler than Oja:

```text
w_j <- max(0, w_j + eta * event * x[position_j])
normalize route weights to sum to one
```

It is best described as **route-conditioned spatial Hebbian plasticity with a resource constraint**, not biological Oja learning or PCA.

Frozen 64-seed highlights from `results/v0.json`:

- spatial response separation: **0.278776**;
- modal-fingerprint separation: **0.932674**;
- learned multi-site response alignment: **0.980079**;
- best single-site attacker: **0.683739**;
- multi-site advantage: **+0.296340**;
- paired local weight-pattern alignment: **0.999930**;
- shuffled alignment: **0.711677**.

A dense vector lookup can reproduce a fixed injection exactly. The surviving claim is therefore narrow:

> **distributed scalar contacts plus a fixed cable provide a structured receiver-side expansion of a tiny routed event.**

---

## Frequency gate — timing is signal, but resonance alone does not earn morphology

A passive cable mode behaves approximately as

```text
z_n[t+1] = lambda_n z_n[t] + b_n q[t]
```

so each mode is a leaky temporal filter. Passive decay is not resonance: its response peaks at DC.

The frequency gate adds one synthetic recovery variable per compartment:

```text
v[t+1] = A v[t] - g_w w[t] + u[t]
w[t+1] = alpha w[t] + beta v[t]
```

The quasi-active cable develops a genuine non-zero response peak:

| Quantity | Result |
|---|---:|
| passive peak frequency | **0.000000 rad/step** |
| quasi-active peak frequency | **0.319068 rad/step** |
| quasi-active peak period | **19.6923 steps** |
| quasi-active peak/DC | **1.9191x** |

With the same landing site, same event amplitude, same 24 pings and same total charge, changing only the inter-ping interval reverses preference relative to the passive cable.

But the matched conceptual attacker matters more: a tuned two-state point resonator reaches **3.2023x peak/DC**, beating the single-site quasi-active cable's **1.9191x**.

So:

> **timing can carry information, but resonance by itself is not a dendrite-specific computational advantage.**

---

## v1 — local active state creates a spatial interaction

`ActiveCableBranch` adds a local excitatory conductance trace, voltage-dependent sigmoid gate and saturating reversal term. It is a synthetic NMDA-like mechanism, not a detailed receptor model.

The balanced construction compares nearby pairs against crossed pairs while holding total charge and class centroid fixed:

```text
positive: A+A1 or B+B1
negative: A+B  or A1+B1
```

The passive cable and gain-zero ablation have no class mean gap. The local active mechanism can distinguish the patterns because nearby inputs jointly raise local voltage and recruit more local conductance.

Frozen `results/v1.json`:

| Metric | nominal | stress |
|---|---:|---:|
| pass count | **64/64** | **63/64** |
| mean active margin | **0.429997** | **0.398905** |
| worst active margin | **0.302040** | **-0.011669** |
| max passive gap | **0** | **~1.1e-16** |

The one stress reversal is retained rather than tuned away.

---

## v2 — one route exposes a family of effective operators

The next machine uses **four short quasi-active branches around one readout**. A route owns sparse contacts across those branches. The combined linear state-space model is

```text
x[t+1] = A x[t] + b_r u[t]
y[t]   = C x[t]
```

and the route's frequency-dependent effective transformation is

```text
h_r(omega) = C (exp(i*omega) I - A)^-1 b_r
```

This is the useful sense in which the route has access to an **operator-valued weight**: the physical route is unchanged, but its effective branch-state direction depends on receiver dynamics and temporal frequency.

Frozen `results/operator_gate.json`:

- route-0 direction rotation between `omega=0.08` and `0.62`: **70.779°**;
- one static complex route-to-branch matrix, held-frequency relative error: **0.895145**;
- compact four-resonator / eight-state point bank relative error: **0.634528**;
- dendritic state count: **48** versus point-bank state count: **8**.

The compact point bank improves substantially but is not a fair same-state morphology attacker. More importantly, an unconstrained degree-matched linear state-space realization can reproduce the transfer exactly. v2 therefore does **not** establish unique linear expressivity.

The surviving statement is:

> **a fixed sparse route can expose different effective directions across time/frequency because it accesses a shared dynamical operator.**

---

## v3 — the exact modal boundary

v3 asks whether the 48-state linear/quasi-active branch bank is actually anything more than a state-space basis choice.

It is not.

Branch by branch, an orthogonal similarity transform converts the cable coordinates into independent modal sections. There is no fit and no optimizer. Across 81 frequencies:

- maximum transfer mismatch: **4.56e-15**;
- maximum cross-mode leakage in the transformed linear system: **4.53e-16**.

So within floating-point precision:

```text
linear/quasi-active dendritic bank
        ==
modal resonator bank
under a change of coordinates
```

That kills the stronger claim that linear cable morphology itself gives unique expressivity.

The boundary changes when the existing local voltage-dependent gate is turned on. Numerical linearization of the same physical branch gives:

- gain-zero cross-mode ratio: **2.30e-11**;
- active cross-mode ratio: **0.582296**;
- changing only resident voltage state rotates the local Jacobian by **34.317°**;
- relative Jacobian change: **1.164292**.

This is the sharper result:

```text
fixed linear machine:       x -> A -> next x
active state-dependent one: x -> J(x) -> next x -> new J(x)
```

A fixed modal bank is globally exact for the first case. In the second case, physical locality creates state-conditioned cross-mode coupling.

This still does not prove that morphology is uniquely efficient. It identifies where the exact fixed-LTI equivalence stops applying.

---

## v4 — A then B is not merely B then A with labels swapped

A raw `A -> B` versus `B -> A` difference is **not** enough to claim noncommutativity. Even a fixed linear dynamical cable is order-sensitive because the first event receives one extra propagation/decay step.

So v4 keeps that as the gain-zero control and asks two stricter questions:

1. does the active branch add an order interaction beyond the linear sequence difference?
2. after A versus B arrives first, do the resulting local Jacobians themselves fail to commute?

For local Jacobians `J_A` and `J_B`, the diagnostic is

```text
[J_A, J_B] = J_A J_B - J_B J_A
```

Frozen deterministic `results/order_gate.json`:

| Quantity | Gain-zero control | Active branch |
|---|---:|---:|
| sequence-order gap | **0.116078** | **0.271040** |
| commutator ratio | **7.86e-12** | **0.129339** |
| first-event operator angle | **0.000°** | **12.935°** |

Additional active measurements:

- active/control sequence-gap ratio: **2.335x**;
- nonlinear order excess norm: **0.160375**;
- first-event relative operator change: **0.247862**.

The gain-zero machine therefore has ordinary dynamical sequence memory but a fixed local operator. The active machine adds a state-conditioned operator change: event A changes the local machine encountered by B differently from event B changing the machine encountered by A.

The earned claim is deliberately concrete:

> **in this synthetic active branch, event order changes the effective computation because the first event changes the local operator seen by the second.**

This is a deterministic mechanism witness. It does not establish that real dendrites implement this exact gate, and it does not establish that dendritic morphology is uniquely required for order-sensitive computation.

---

## v5 — event sequences compose state-conditioned operators

v4 showed that the first event changes the local Jacobian. v5 asks the stricter follow-up: can the **two-event transformation itself** be reconstructed as a composition of the one-step local operators encountered along that particular history?

The state for this gate is the full synthetic branch state,

```text
s = [voltage, conductance]
```

so the conductance trace is not silently frozen. For A then B, the local chain-rule prediction is

```text
J_AB = J_B(after A) @ J_A(initial)
```

and analogously for B then A.

The gain-zero control still keeps dynamical history. A->B and B->A can therefore end at different voltages, but the derivative of the fixed linear machine with respect to its full starting state should not depend on event labels/order. The active branch is different: the first event changes the susceptibility encountered by the second.

Frozen deterministic `results/composition_gate.json`:

| Quantity | Gain-zero control | Active branch |
|---|---:|---:|
| A->B vs B->A two-step Jacobian gap ratio | **7.20e-11** | **0.601361** |
| chain-rule reconstruction error | **7.07e-11** | **9.55e-7** |
| best single fixed operator error across both orders | **3.60e-11** | **0.299312** |

The active A->B and B->A operator norms are **2.704966** and **3.277752**. Their difference is therefore not a tiny numerical perturbation, yet each history-specific two-step operator is reconstructed by composing the local Jacobians along that history to roughly one part in a million.

This earns a more precise statement than “history matters”:

> **in this synthetic active branch, a routed event sequence is locally described by composition of state-conditioned operations; one fixed local matrix does not represent both histories.**

The chain rule itself is of course not a discovery. It is the consistency check that tells us *where the computation is*: the first event moves the resident state, that state changes the next local operator, and the resulting operators compose along the trajectory.

This still does not establish unique dendritic expressivity. A sufficiently general nonlinear state-space model can implement state-conditioned Jacobians too. The remaining morphology question is therefore about **factorization, locality, parameter/state economy, and learnability**, not existence of nonlinear sequence computation.

---

## What carries the load now?

The project began by asking what replaces a conventional scalar/vector "weight" when the travelling event itself is tiny.

The current decomposition is:

```text
route identity
    |
    +-- spatial contact pattern          where
    +-- ping timing                      when
    +-- shared receiver dynamics         transfer family
    +-- resident local state             current susceptibility
    +-- immediately previous events      operator context
    |
    v
effective operation on the present machine
```

A useful shorthand is no longer `route -> weight`. It is closer to

```text
route r invokes O_r[x, history]
```

or, locally,

```text
H_r(omega | x) = C(x) (exp(i*omega) I - J(x))^-1 B_r(x)
```

That notation is a description of the synthetic machine, not a biological identity claim.

The important factorization is:

```text
small thing travels;
large state stays;
landing geometry expands;
timing selects dynamics;
local state changes the operator;
event order changes what the next event encounters;
sequence computation is the composition of those encountered operators.
```

---

## Next honest gates

The completed gates have progressively removed easy stories:

1. ~~distributed spatial route~~ — **DONE**;
2. ~~frequency addressing~~ — **DONE; point resonator wins the simple resonance comparison**;
3. ~~local active interaction~~ — **DONE**;
4. ~~branch bank / operator-valued route~~ — **DONE**;
5. ~~exact modal realization boundary~~ — **DONE; linear morphology is a basis/realization, not unique expressivity**;
6. ~~state-conditioned event order~~ — **DONE; active local Jacobians differ and fail to commute in the frozen fixture**;
7. ~~state-conditioned operator composition~~ — **DONE; history-specific local Jacobians compose the two-step maps while one fixed operator fails across orders**.

The next useful fight is to combine v1 and v2 rather than add decorative biology:

8. **distributed nonlinear branch bank** — let one sparse route touch several branches, each with local active state, and test whether the resulting state-conditioned operator family can be matched by a degree/parameter-matched non-spatial nonlinear state-space attacker;
9. **local inhibition** — only if gate 8 survives, add SOM-like branch gating and ask whether it selectively changes which local operator participates;
10. **perisomatic correction** — PV/basket-like control of the soma mixture without erasing branch state;
11. **spatial AIS** — proximal/distal AIS plus chandelier-like inhibition, explicitly testing whether landing position is functionally non-equivalent;
12. **growth-to-purity** — permit structural growth only when an added physical degree of freedom improves held-out separation against matched attackers.

The next scientific target is therefore not "more resonance." It is whether **physical locality makes a state-dependent operator cheaper or more naturally factorized than an equally capable non-spatial dynamical model**.

---

## Papers anchoring the exploration

- Yang, Murray & Wang (2016), **A dendritic disinhibitory circuit mechanism for pathway-specific gating**, *Nature Communications* 7:12815.
- Leterrier (2018), **The Axon Initial Segment: An Updated Viewpoint**, *Journal of Neuroscience* 38(9):2135-2145.
- Fréal & Hoogenraad (2025), **The dynamic axon initial segment: From neuronal polarity to network homeostasis**, *Neuron* 113.
- Brette (2025), **Theory of axo-axonic inhibition**, *PLOS Computational Biology* 21(4):e1013047.
- Koch & Poggio (1985), **A simple algorithm for solving the cable equation in dendritic trees of arbitrary geometry**, *Journal of Neuroscience Methods* 12(4):303-315.

These papers motivate mechanisms and controls; they are not treated as validation of this synthetic architecture.

---

## Run it

```bash
python -m pip install -e '.[test]'
pytest -q

python experiments/run_v0.py --seeds 64 --out results/v0_full.json
python experiments/run_frequency_gate.py --out results/frequency_gate_full.json
python experiments/run_v1.py --seeds 64 --out results/v1_full.json
python experiments/run_operator_gate.py --out results/operator_gate_full.json
python experiments/run_modal_boundary.py --out results/modal_boundary_full.json
python experiments/run_order_gate.py --out results/order_gate_full.json
python experiments/run_composition_gate.py --out results/composition_gate_full.json
```

CI runs Python 3.11 and 3.12 and executes smoke runs for all seven gates.

---

## Relationship to SimpleNeuron

`SimpleNeuron` used an explicit learned receiving vector `B[:, k]`:

```text
route k -> B_k -> resident state
```

`NotSoSimpleNeuron` asks how much of that effective vector can instead emerge from structured receiver dynamics:

```text
route k
   -> ordinary scalar contacts
   -> spatial landing pattern
   -> timing
   -> cable / recovery / active local state
   -> state-conditioned effective operation
```

The current evidence is intentionally mixed:

- **space matters** for distributing ordinary scalar contacts;
- **time matters**, but a point resonator can decode it too;
- **linear cable dynamics are exactly realizable in modal coordinates**;
- **local nonlinear state breaks the globally fixed modal decomposition**;
- **event order changes the local active operator in the frozen synthetic gate**;
- **history-specific operators compose consistently along a sequence, while one fixed operator fails across the two orders**;
- morphology still has **not** earned a universal computational advantage.

That is the standard this repository is meant to enforce.

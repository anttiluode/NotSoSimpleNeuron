# NotSoSimpleNeuron

> **A tiny routed event can acquire meaning from where it lands, when it lands, and what local state it encounters.**

This repo starts from a question that fell out of `SimpleNeuron`:

> If an axonal event is nearly binary, how could it steer a receiver along a high-dimensional direction?

The project now has three deliberately separate mechanism witnesses:

1. **spatial addressing** — one route owns several ordinary scalar contacts on a passive cable;
2. **temporal addressing** — the same landing site responds differently to different ping timing, and one recovery state creates genuine non-zero-frequency preference;
3. **active local interaction** — nearby equal-charge inputs recruit a local voltage-dependent conductance that crossed inputs do not.

The point is not to make a neuron complicated because biology is complicated. Every extra mechanism gets an attacker and has to earn a role.

---

## v0 — a route can be a distributed spatial vector

One route owns several ordinary non-negative scalar contacts at different positions on a passive dendritic cable:

```text
route r = {(position_j, weight_j)}
```

The route event carries only a scalar and the branch evolves as

```text
x[t+1] = A @ x[t] + u_r q[t]
```

where `A` is a stable passive cable operator. In the cable eigenbasis,

```text
z = Phi.T @ u_r
```

so a sparse landing pattern acquires a modal fingerprint because of **where** its contacts land. The event does not contain the vector; receiver geometry supplies the expansion.

### Important language

The v0 cable is a **passive damped cable**, not a literal resonant string. Its spatial modes have different decay factors. Passive dynamics can filter temporal patterns, but their local transfer is low-pass rather than genuinely band-resonant.

Likewise, v0 does **not** claim that one biological synapse stores a vector. Each contact stores one scalar. The route-level pattern is distributed across several contacts.

### Post-Oja-like spatial learning

The first learning rule is intentionally simpler than Oja's rule. When route `r` is active while the local branch has state `x`, each contact sees the common presynaptic event and only its local postsynaptic value:

```text
w_j <- max(0, w_j + eta * event * x[position_j])
normalize route weights to sum to one
```

This is best described as **route-conditioned spatial Hebbian plasticity with a homeostatic resource constraint**. It is not claimed to be biological Oja learning or PCA.

The useful interpretation is

```text
repeated route/state pairing
        |
        v
redistribute ordinary scalar synapses in space
        |
        v
later binary ping excites a learned cable response
```

### Frozen v0 result

`results/v0.json` is a frozen aggregate receipt from 64 deterministic seeds.

| Gate | Result |
|---|---:|
| Cable invariants | `PASS_CABLE_INVARIANTS` |
| Equal-charge spatial routes remain distinguishable | `PASS_GEOMETRY_EXPANDS_PING` |
| Distributed scalar learning beats shuffle + best single site | `PASS_DISTRIBUTED_SCALAR_LEARNING` |
| Soft temporal knee retains its narrow clustering role | `KNEE_RETAINS_ROLE` |

Selected 64-seed results:

- spatial response separation: **0.278776**;
- modal-fingerprint separation: **0.932674**;
- paired local weight-pattern alignment: **0.999930 mean**;
- shuffled alignment: **0.711677 mean**;
- paired minus shuffle: **+0.288253 mean**, **+0.169552 worst seed**;
- learned multi-site response alignment: **0.980079 mean**;
- best single landing-site attacker: **0.683739**;
- multi-site advantage over best single site: **+0.296340 mean**;
- soft-knee / linear close-pair gain: **3.85612x** with matched first-pulse gain.

The result is a constructed mechanism witness. Training supplies route-specific spatial states, and the local rule learns which of six candidate contact positions are repeatedly active. It does not show that real dendrites learn eigenmodes this way.

### v0 attackers

A **point scalar attacker** sees only total route charge. Both routes sum to one, so it sees no difference.

A **best single-site attacker** can choose the one contact position whose cable response best matches each target. It reaches `0.683739` mean alignment; six learned scalar contacts reach `0.980079`.

A **dense vector lookup** can reproduce any fixed injection exactly. Therefore the claim is not “dendrites compute something vectors cannot.” It is narrower:

> **spatially distributed scalar contacts plus a fixed cable give a structured receiver-side expansion of a tiny routed event.**

---

## Frequency gate — where is the signal if the ping is tiny?

A near-binary event can still participate in a rich signal because information can live in **when events arrive**.

In modal coordinates, a passive mode obeys approximately

```text
z_n[t+1] = lambda_n z_n[t] + b_n q[t]
```

so `lambda_n` sets a memory timescale. A passive cable is therefore not only a spatial expander; it is also a bank of leaky temporal filters addressed by landing position.

But passive decay is not resonance. Its local frequency response peaks at DC.

### Add one recovery state

The frequency gate adds exactly one synthetic recovery variable per compartment:

```text
v[t+1] = A v[t] - g_w w[t] + u[t]
w[t+1] = alpha w[t] + beta v[t]
```

This is a minimal quasi-active resonator, not a detailed model of `I_h`, potassium, calcium, or NMDA currents.

The frozen nominal branch has spectral radius **0.900555** and a real non-zero response peak:

| Quantity | Result |
|---|---:|
| passive peak frequency | **0.000000 rad/step** |
| passive peak/DC | **1.0000x** |
| quasi-active peak frequency | **0.319068 rad/step** |
| quasi-active peak period | **19.6923 steps** |
| quasi-active peak/DC | **1.9191x** |

`results/frequency_gate.json` also uses literal ping trains. Every condition receives **24 identical pings at the same compartment** and therefore exactly the same event count and total charge. Only inter-ping interval changes.

The passive cable prefers the dense train by accumulation:

```text
interval 4:  mean post-ping voltage 1.528779
interval 20: mean post-ping voltage 1.031269
fast - slow: +0.497510
```

The quasi-active receiver reverses that preference near its resonant period:

```text
interval 4:  mean post-ping voltage 0.879470
interval 20: mean post-ping voltage 1.026526
slow - fast: +0.147056
```

So the temporal statement survives:

> **the ping need not carry a frequency label; receiver state can decode the timing of repeated tiny events.**

### The point attacker wins this gate

This control matters more than the positive result.

A tuned **two-state point resonator** gets the same recovery mechanism but no cable geometry. It is allowed to tune its scalar persistence over a fixed grid.

| Model | peak/DC |
|---|---:|
| quasi-active cable, one landing/readout site | **1.9191x** |
| tuned two-state point attacker | **3.2023x** |

The point attacker therefore reports `POINT_MATCHES_OR_BEATS`.

That means **frequency resonance alone does not earn dendritic morphology**. Temporal addressing is a property of suitable receiver dynamics in general.

The stronger hypothesis now becomes spatio-temporal rather than merely resonant:

```text
route meaning
    =
where its contacts land
    x
when its pings arrive
    x
what local dynamics live at those sites
```

A dendrite gets another chance to matter when one route owns multiple contacts across locations or branches with different transfer functions, not when one compartment merely rings.

---

## v1 active branch — local spatial coincidence changes the computation

Frequency selection is kept separate from the active nonlinear gate.

`ActiveCableBranch` adds a local excitatory conductance trace, a voltage-dependent sigmoid gate, and a saturating reversal term. It is intentionally a synthetic NMDA-like mechanism, not a detailed receptor model.

The key test is a balanced spatial XOR construction on a 12-compartment cable:

```text
positive class: nearby pair A+A1 OR nearby pair B+B1
negative class: crossed pair A+B OR crossed pair A1+B1
```

All four patterns carry equal total charge. The two classes also have **exactly the same spatial centroid**. Consequently:

- the passive cable has no class mean gap;
- setting active gain to zero removes the gap;
- the balanced construction gives any one linear projection a score-sum identity, so a single linear score followed by a monotone threshold cannot perfectly solve the four-pattern problem.

The local active mechanism can distinguish nearby from crossed excitation because nearby inputs jointly raise local voltage and therefore recruit more local conductance.

### Frozen 64-world result

`results/v1.json` keeps both a nominal regime and a deliberately broader stress range.

| Metric | nominal | stress |
|---|---:|---:|
| pass count | **64/64** | **63/64** |
| mean active margin | **0.429997** | **0.398905** |
| worst active margin | **0.302040** | **-0.011669** |
| mean active ratio | **1.431748** | **1.403979** |
| max passive gap | **0** | **~1.1e-16** |
| max gain-zero gap | **0** | **~1.1e-16** |

The stress reversal is retained rather than tuned away: seed 25 crosses the boundary under low coupling/gain and gives active margin `-0.011669`.

So v1 establishes a limited claim:

> **local spatial state plus a voltage-dependent local mechanism can implement an interaction that disappears under passive superposition and under gain-zero ablation.**

It does not establish that this synthetic conductance is the best way to compute the task, nor that a richer point model could never reproduce it.

---

## What the machine is becoming

The three gates now give different jobs to different pieces:

```text
                 tiny routed events
                        |
                        v
             spatial contact pattern       <- v0: where
                        |
                        v
           local temporal dynamics         <- frequency gate: when
                        |
                        v
       local voltage-dependent interaction <- v1: current local context
                        |
                        v
                 branch states
                        |
                        v
                    SOMA MIX
                        |
                        v
                       AIS
                        |
                        v
                 tiny routed events
```

A useful shorthand is therefore

```text
small thing travels;
large state stays;
landing geometry expands;
timing selects dynamics;
local state changes susceptibility.
```

That is more interesting than “a synapse stores a vector,” but it is also more falsifiable.

---

## Next gates

The next additions stay ordered so complexity has to earn itself:

1. ~~**Distributed spatial route**~~ — several scalar contacts on one passive cable. **DONE: v0.**
2. ~~**Temporal/frequency addressing**~~ — passive low-pass versus quasi-active resonance versus point attacker. **DONE: point attacker wins the morphology comparison.**
3. ~~**Active local interaction**~~ — nearby/crossed equal-charge patterns versus passive and gain-zero controls. **DONE: 64/64 nominal, 63/64 stress.**
4. **Branch bank / dendrite ring** — several short cables around one soma; one route owns contacts across multiple branches.
5. **Spatio-spectral route** — give branches different local time constants/resonances and ask whether a sparse distributed route can exploit `where x when` more cheaply than a matched point/vector bank.
6. **Dendritic inhibition** — SOM-like local gating asks which branch/pathway is allowed into the mixture.
7. **Perisomatic correction** — PV/basket-like inhibition modifies the soma calculation without erasing branch state.
8. **Spatial AIS** — proximal/distal AIS compartments plus chandelier-like inhibition; test whether inhibitory landing position is functionally non-equivalent.
9. **Growth-to-purity** — only then permit structural growth, retaining added cable only when held-out separation improves against matched attackers.

The immediate next experiment should therefore combine the two things that independently survived: **distributed spatial contacts + temporal dynamics**. If a matched bank of point resonators still wins at equal state/parameter budget, the dendritic story gets cut back again.

---

## Papers anchoring the exploration

- Yang, Murray & Wang (2016), **A dendritic disinhibitory circuit mechanism for pathway-specific gating**, *Nature Communications* 7:12815. Dendritic branches as quasi-independent nonlinear processors; pathway clustering and branch-local disinhibition.
- Leterrier (2018), **The Axon Initial Segment: An Updated Viewpoint**, *Journal of Neuroscience* 38(9):2135-2145. AIS architecture, polarity and morphological plasticity.
- Fréal & Hoogenraad (2025), **The dynamic axon initial segment: From neuronal polarity to network homeostasis**, *Neuron* 113. AIS subcompartments, activity-dependent structural/molecular plasticity and axo-axonic innervation.
- Brette (2025), **Theory of axo-axonic inhibition**, *PLOS Computational Biology* 21(4):e1013047. Quantitative position-sensitive theory for chandelier/AIS inhibition.
- Koch & Poggio (1985), **A simple algorithm for solving the cable equation in dendritic trees of arbitrary geometry**, *Journal of Neuroscience Methods* 12(4):303-315. Transfer impedance in branched passive cables.

## Run it

```bash
python -m pip install -e '.[test]'
pytest -q

python experiments/run_v0.py --seeds 64 --out results/v0_full.json
python experiments/run_frequency_gate.py --out results/frequency_gate_full.json
python experiments/run_v1.py --seeds 64 --out results/v1_full.json
```

For CI-sized smoke runs:

```bash
python experiments/run_v0.py --seeds 4 --train-steps 120 --out /tmp/v0.json
python experiments/run_frequency_gate.py --out /tmp/frequency.json
python experiments/run_v1.py --seeds 4 --out /tmp/v1.json
```

## Relationship to SimpleNeuron

`SimpleNeuron` used an explicit learned receiving vector `B[:, k]`:

```text
route k -> B_k -> resident state
```

`NotSoSimpleNeuron` asks how much of that effective vector can instead emerge from structured receiver dynamics:

```text
route k
   -> scalar contacts {(position, weight)}
   -> ping timing
   -> local cable / recovery / active state
   -> effective high-dimensional steering and interaction
```

The current evidence says the answer is nuanced:

- **space matters** when one route distributes ordinary scalar contacts across several locations;
- **time matters**, but a point resonator can decode it too;
- **local nonlinear interaction matters** on the balanced nearby-versus-crossed construction;
- morphology has not yet earned a universal computational advantage.

That is exactly the standard this repo is meant to enforce.

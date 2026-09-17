# NotSoSimpleNeuron

> **A route does not have to carry a vector if it can own several scalar synapses at different places on a structure that expands location into dynamics.**

This repo starts from one small question that fell out of `SimpleNeuron`:

> If an axonal event is nearly binary, how could it steer a receiver along a high-dimensional direction?

The v0 answer is deliberately mechanical. One route owns **several ordinary non-negative scalar contacts** at different positions on a passive dendritic cable. The route event carries only a scalar. Its spatial landing pattern is

```text
route r = {(position_j, weight_j)}
```

and the branch evolves as

```text
x[t+1] = A @ x[t] + u_r q[t]
```

where `A` is a stable cable operator. In the cable eigenbasis,

```text
z = Phi.T @ u_r
```

so one sparse routed event acquires a **modal fingerprint** because of where its contacts land. The event does not contain the mode; the receiver geometry supplies the expansion.

## Important language

v0 is a **passive damped cable**, not a literal resonant string. Its eigenvectors are useful spatial modes with different decay factors. Genuine frequency-selective resonance belongs to a later active/quasi-active gate.

Likewise, v0 does **not** claim that a biological synapse stores a vector. Each contact stores one scalar. A route-level pattern is distributed across several contacts.

## v0 machine

```text
near-binary route event
          |
          v
  optional local knee
          |
          v
  six scalar contacts
   at different positions
          |
          v
   passive cable state
          |
          +--> spatial voltage pattern
          |
          +--> modal fingerprint
```

The route contacts are constrained to be non-negative and to sum to one. Equal-charge routes therefore differ only in **where** their strength is placed.

### Post-Oja-like spatial learning

The first learning rule is intentionally simpler than Oja's rule. When route `r` is active while the local branch has state `x`, each contact sees the same presynaptic route event and only its local postsynaptic value:

```text
w_j <- max(0, w_j + eta * event * x[position_j])
normalize route weights to sum to one
```

This is best described as **route-conditioned spatial Hebbian plasticity with a homeostatic resource constraint**. It is not claimed to be biological Oja learning or PCA.

The useful interpretation is:

```text
repeated route/state pairing
        |
        v
redistribute ordinary scalar synapses in space
        |
        v
later binary ping excites a learned cable response
```

## Frozen v0 result

`results/v0.json` is a frozen aggregate receipt from 64 deterministic seeds.

| Gate | Result |
|---|---:|
| Cable invariants | `PASS_CABLE_INVARIANTS` |
| Equal-charge spatial routes remain distinguishable | `PASS_GEOMETRY_EXPANDS_PING` |
| Distributed scalar learning beats shuffle + best single site | `PASS_DISTRIBUTED_SCALAR_LEARNING` |
| Soft temporal knee retains its narrow clustering role | `KNEE_RETAINS_ROLE` |

Selected 64-seed aggregate results:

- spatial response separation for the two equal-charge routes: **0.278776**;
- modal-fingerprint separation: **0.932674**;
- paired local weight-pattern alignment: **0.999930 mean**;
- route-label-shuffled alignment: **0.711677 mean**;
- paired minus shuffle: **+0.288253 mean**, **+0.169552 worst seed**;
- learned multi-site response alignment to its paired target: **0.980079 mean**;
- best single landing-site attacker: **0.683739**;
- multi-site advantage over best single site: **+0.296340 mean**;
- soft-knee / linear close-pair gain: **3.85612x** with matched first-pulse gain.

The result is a **constructed mechanism witness**. Training supplies route-specific spatial states, and the local rule learns which of six candidate contact positions are repeatedly active. It does not show that real dendrites learn eigenmodes this way.

## What the attackers say

The most important controls are part of the claim, not footnotes.

A **point scalar attacker** sees only total route charge. Both routes sum to one, so it sees no difference: separation is exactly zero.

A **best single-site attacker** is allowed to choose the one contact position whose cable response best matches each target. It reaches `0.683739` mean alignment; six learned scalar contacts reach `0.980079`.

A **dense vector lookup** can reproduce any fixed injection exactly. That is expected. Therefore the current claim is not “dendrites can compute something vectors cannot.” The claim is narrower:

> **spatially distributed scalar contacts plus a fixed cable give a structured receiver-side expansion of a tiny routed event.**

Whether that structure is useful enough to beat equally cheap vector machinery on real tasks remains open.

## Why this is interesting for the neuron picture

It gives a more concrete replacement for the vague phrase “the synapse learns a vector.”

```text
scalar synapse strengths
        +
contact positions
        +
receiver cable operator
        =
effective high-dimensional steering direction
```

This also makes multiple contacts from one route important rather than redundant. One source can “play” several positions of the same branch, and later versions can let one route distribute contacts across several dendrites.

## Next gates

The next additions are intentionally ordered so complexity has to earn itself:

1. **Active branch:** add an NMDA-like local plateau and test whether nearby/coincident routes create useful nonlinear interactions beyond passive superposition.
2. **Branch bank / dendrite ring:** several short cables around one soma; allow one route to own contacts across branches.
3. **Dendritic inhibition:** SOM-like local gating asks which branch/pathway gets into the mixture.
4. **Perisomatic correction:** PV/basket-like inhibition modifies the soma calculation without erasing branch state.
5. **Spatial AIS:** proximal/distal AIS compartments plus chandelier-like inhibition; test whether inhibitory landing position is functionally non-equivalent.
6. **Growth-to-purity:** only then allow branches to add cable when added length measurably improves separation against matched attackers.

The 2025 theory of axo-axonic inhibition is especially useful for Gate 5: Brette derives a position-sensitive threshold shift from synaptic conductance, driving force and axial resistance, giving us a quantitative synthetic target rather than a metaphor.

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
```

For a quick smoke run:

```bash
python experiments/run_v0.py --seeds 4 --train-steps 120 --out /tmp/not_so_simple_smoke.json
```

## Relationship to SimpleNeuron

`SimpleNeuron` used an explicit learned receiving vector `B[:, k]`:

```text
route k -> B_k -> resident state
```

`NotSoSimpleNeuron` asks whether part of that vector can instead be **implicit in morphology**:

```text
route k
   -> scalar contacts {(position, weight)}
   -> dendritic cable
   -> effective B_k / modal fingerprint
```

So the experiment is not “make the neuron biologically complicated.” It is exactly the opposite: find the smallest piece of spatial structure that earns a computational role.

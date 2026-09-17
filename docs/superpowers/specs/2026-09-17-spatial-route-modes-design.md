# NotSoSimpleNeuron v0 — Spatial Route Modes

## Question

Can a near-binary routed event acquire high-dimensional meaning without carrying a high-dimensional payload, by letting one route own several scalar synapses at different positions on a dendritic cable?

The proposed mechanism is:

```text
binary route event
      ↓
optional local temporal knee
      ↓
several scalar synapses at distinct cable locations
      ↓
passive cable dynamics
      ↓
spatial voltage pattern / modal fingerprint
```

The event does not carry an eigenmode. The receiver geometry expands a sparse spatial injection into a mixture of the cable's modes.

## Scope

v0 deliberately tests the smallest version of this claim. It does not yet claim biological calibration, literal dendritic resonance, NMDA plateaus, structural growth, learned axonal topology, SOM/PV gating, basket-cell correction, or spatial chandelier computation.

Those are later gates only if passive spatial routing earns a role first.

## Model

A branch is an `n`-compartment passive cable with discrete dynamics

```text
x[t+1] = A x[t] + u[t]
```

where `A = I - leak*I - coupling*L` and `L` is the path-graph Laplacian. Parameters must keep all eigenvalues inside the unit circle.

Because `A` is symmetric, its orthonormal eigenvectors `Phi` define a convenient modal basis. For an injection vector `u`, the modal fingerprint is

```text
z = Phi.T @ u
```

A route owns several contacts:

```text
route r = {(position_j, weight_j)}
```

and one event produces

```text
u_r[position_j] += weight_j
```

All v0 route weights are non-negative and L1-normalized, so routes compared in the core gate deliver equal total charge. This avoids pretending that one excitatory axon can directly write arbitrary signed eigenvectors.

## Learning

v0 uses a deliberately simple post-Oja-like local rule, not a claim of biological Oja learning.

When route `r` is active while the branch is in local state `x`, each contact updates from only the shared presynaptic route event and its local postsynaptic value:

```text
w_j <- max(0, w_j + eta * event * x[position_j])
```

followed by route-level L1 normalization. The normalization is a homeostatic resource constraint; it keeps total route strength fixed while redistributing it spatially.

Interpretation: repeated route/state pairing changes a distribution of scalar synapses. The cable, not the synapse, converts that distribution into a high-dimensional response.

## v0 gates

### Gate 0 — Cable invariants

- passive update is stable;
- modal basis is orthonormal;
- linear cable obeys superposition;
- equal-L1 routes deliver equal total injected charge.

### Gate 1 — Geometry expands the ping

Construct two routes with equal total strength but different multi-site spatial patterns. Their binary events must produce distinguishable spatial responses and distinguishable modal fingerprints.

A matched point-scalar attacker receives only total input charge, so the two routes are identical to it. A dense vector lookup attacker is allowed to match the cable response; if it does, the interpretation is compression/inductive structure, not greater expressivity.

### Gate 2 — Distributed scalar learning

Start route contacts with uniform strength. Pair each route repeatedly with a different smooth non-negative spatial state under noise. The local update should redistribute scalar weights toward locations characteristic of its paired state.

Success requires:

- paired route/state alignment substantially above a route-label shuffle;
- learned routes remain equal in total strength;
- later binary events through the learned contacts produce separable cable responses.

This establishes only that spatially distributed scalar plasticity can acquire route-specific receiver-side meaning in the toy cable.

### Gate 3 — Knee placement

Provide direct, leaky-trace, and soft-knee transducers with matched immediate gain for one isolated event. The transducer scales the route event before its spatial contact pattern is injected. The knee may stay only if clustered events obtain useful temporal selectivity beyond the matched linear trace.

This repeats a mechanism already isolated in `SimpleNeuron`; it is included here to place the nonlinearity correctly, not as the novelty claim.

## Attackers and interpretation

The critical attacker is the same-capacity point representation with route identity removed after equalizing total charge. If it performs identically, geometry has not earned a role.

A dense vector lookup is expected to reproduce any fixed learned cable injection. If it can, the honest claim is that dendritic geometry supplies a structured expansion from sparse scalar contacts, not that it creates functions impossible for vectors.

A single best landing site is also compared with the learned multi-site route. If one site matches the multi-site route, distributed ownership has not earned a role.

## Later gates

Only after v0 survives:

1. **Active branch:** add an NMDA-like local plateau and test whether spatial overlap/coincidence produces computation unavailable to the passive superposition baseline.
2. **Branch bank / dendrite ring:** several short cables feed one soma so branch identity and local mixtures can compete or cooperate.
3. **Dendritic inhibition:** test branch-local SOM-like inhibition as pathway selection.
4. **Perisomatic correction:** test PV/basket-like inhibition as modification of the soma mixture rather than erasure of dendritic state.
5. **Spatial AIS:** use a short proximal/distal AIS model and test whether inhibitory position is non-equivalent. Brette's 2025 resistive-coupling result supplies a quantitative attacker: threshold shift depends on synaptic conductance, driving force, and axial resistance to the relevant AIS position.
6. **Growth-to-purity:** allow a branch to add compartments only when extra cable length measurably improves a predefined separation objective against matched parameter-count attackers.

## Scientific language

Use `mode`, `modal fingerprint`, or `damped cable mode` for the passive system. Do not call the passive cable a literal resonant string. Reserve `resonance` for a later active/quasi-active model that actually has frequency-selective dynamics.

## References motivating the gates

- Rall-style cable theory and transfer impedance motivate position-dependent dendritic effects.
- Yang, Murray & Wang (2016), *A dendritic disinhibitory circuit mechanism for pathway-specific gating*, motivates branch-local nonlinear processing, clustering, and dendritic inhibition.
- Leterrier (2018) and Fréal & Hoogenraad (2025) motivate treating the AIS as a spatially organized, plastic compartment rather than a scalar threshold.
- Brette (2025), *Theory of axo-axonic inhibition*, motivates the later spatial AIS gate and predicts position-dependent axo-axonic threshold shifts.

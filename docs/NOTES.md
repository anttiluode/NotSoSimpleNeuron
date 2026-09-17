# Research notes

## What v0 established

The passive cable is a fixed linear operator. Equal-total-charge routes are distinguishable only because their scalar contacts occupy different positions. In modal coordinates this becomes a different coefficient vector for each route.

The local learning gate is intentionally a witness rather than a learning-theory claim: route/state pairing provides local positive activity at candidate contacts; Hebbian increments plus route-level L1 normalization redistribute a fixed resource across those contacts. Route-label shuffling removes the relation and lowers alignment.

## What v0 did not establish

- no biological calibration;
- no literal oscillatory dendritic resonance;
- no signed arbitrary eigenmode writing by one excitatory route;
- no structural growth;
- no topology learning;
- no evidence that geometry beats a dense vector lookup;
- no active dendritic channels;
- no soma/PV/SOM/AIS computation yet.

## Why six contacts instead of one contact per compartment

Using every compartment would make the route nearly identical to an explicit dense vector. v0 therefore exposes only six candidate contact positions on a 12-compartment branch. This is still a constructed sparse basis, but it forces the multi-site result to survive against a best-single-site attacker.

## Current mechanistic interpretation

A useful decomposition is

```text
route identity            -> which distributed contact pattern
scalar synaptic weights   -> how strongly each location is touched
cable geometry/operator   -> how those touches spread and mix
current branch state      -> what is already present
local nonlinearities      -> later state-dependent susceptibility
soma/perisomatic control  -> later mixture/correction
AIS                        -> later publication boundary
```

The key hypothesis for future work is that some of what `SimpleNeuron` stored explicitly in `B[:, k]` can be represented by `contact positions + scalar strengths + receiver dynamics`.

## Active-branch gate

The next strong test should preserve the passive cable as an attacker. Add a local NMDA-like state variable only at selected compartments. Nearby/coincident inputs should be capable of triggering a local plateau while equally energetic separated inputs remain subthreshold. If a point nonlinearity or simple event counter matches the task, the spatial active branch does not earn its complexity.

## AIS gate

Do not model chandelier input as a generic negative scalar. Brette (2025) gives a quantitative position-sensitive relation for threshold shift in the proximal axon. A later two- or multi-compartment AIS should first reproduce that relation, then ask whether multiple inhibitory landing positions add control beyond one adjustable threshold.

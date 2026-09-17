# v2 — operator-valued route

The branch-bank gate makes the “weight may be a matrix/operator” idea executable.

Four six-compartment quasi-active branches are assembled into one block-diagonal 48-state receiver operator. Three equal-charge routes each own sparse scalar contacts across the branches. For route amplitudes `u`, branch readouts are

```text
H(omega) = C (exp(i omega) I - A)^-1 B
```

where `A` is the assembled receiver dynamics, `B` is the sparse route/contact injection matrix, and `C` selects one readout voltage per branch.

The important point is that one physical route is not one fixed output vector. Its effective column is

```text
h_r(omega) = H(omega)[:, r]
```

and that column changes with input timing.

## Frozen receipt

`results/operator_gate.json` records the deterministic gate.

- four branches, three routes, 67 frequencies;
- every route has total contact weight exactly `1.0`;
- direct transfer identity error: `0.0`;
- route 0 low/high normalized overlap: `0.329213`;
- corresponding branch-mixture rotation: **70.779 degrees**;
- best single static complex route-to-branch matrix, fitted on alternating frequencies and evaluated on held frequencies: **0.895145 relative error**;
- compact dynamic point-bank attacker: **0.634528 relative error**.

The point attacker is intentionally strong enough to matter but intentionally reported with its limitation: it uses one two-state point resonator per branch, **8 states total**, while the cable bank has **48 states**. It improves substantially over one fixed matrix, so dynamics—not morphology alone—explain a large part of the effect. It does not reproduce the full operator family.

## What this establishes

A useful description is now

```text
scalar contacts + contact positions + receiver dynamics + input timing
    -> effective route operator
```

or, more compactly:

> **A synapse can remain scalar while a route has access to an operator.**

This is not unique linear expressivity. An unconstrained linear state-space system with the same state dimension can reproduce the same transfer family exactly. The current claim is about a structured physical factorization of the mapping, not about dendrites computing something matrices cannot.

## Next falsification

The next attacker should be genuinely budget matched. Give a non-morphological dynamic system the same state count and a comparable number of free parameters, then ask whether the sparse branch/contact factorization buys anything in adaptation, compositional reuse, sparsity, robustness, or interpretability. If it does not, morphology remains an explanatory implementation rather than a computational advantage.

# Operator-bank gate

## Scientific question

Can one sparse physical route expose different effective branch-state directions as ping frequency changes, when the receiver is a bank of short dendritic cables with different local dynamics?

The claim is deliberately narrower than “morphology beats point neurons.” The gate should establish that the external route-to-soma mapping is an operator-valued function of frequency,

`H(omega) = C (exp(i omega) I - A)^-1 B W R`,

and then ask what simpler attackers can reproduce it.

## Design

- Four short quasi-active cable branches, each with a slightly different recovery timescale/coupling.
- A block-diagonal receiver state operator assembled from those branch operators.
- Three routes. Each route owns a sparse set of ordinary scalar contacts across several branches/positions, normalized to equal total charge.
- Readout exposes one voltage from each branch, yielding a branch-mixture vector rather than one scalar soma score.
- Compute the complex transfer matrix `H(omega)` from route amplitudes to branch readouts over a frequency grid.

## Required controls

1. Same route, same contacts, same total input: changing only `omega` must rotate the normalized branch-mixture direction by a measurable amount.
2. A best constant/static route matrix fitted across all frequencies must leave non-zero relative error. This is the direct test that one scalar/vector “weight per route” is insufficient for the whole frequency family.
3. Report a compact dynamic point-bank attacker. A point-bank win is allowed and must not be tuned away; it would mean temporal addressing is not morphology-specific.
4. Keep the dense-state-space equivalence explicit: an unconstrained linear system of the same state dimension can reproduce the transfer exactly, so the claim is about structured factorization, not unique expressivity.

## Acceptance

- `H(omega)` equals direct state-space assembly to numerical precision.
- At least one route changes normalized branch-output direction substantially across the chosen low/mid/high frequencies.
- The best static matrix has clearly non-zero held-frequency relative error.
- Attacker outcome is recorded, whatever it is.

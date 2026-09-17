# Frequency addressing gate

This gate asks where signal can live when a routed event itself is nearly binary.

The experiment holds **landing site, ping amplitude, ping count, and total charge fixed** and changes only ping timing. A passive cable provides multiple decay times but remains low-pass. A synthetic quasi-active cable adds one recovery state per compartment and develops a non-zero-frequency preference.

Frozen receipt: `results/frequency_gate.json`.

## Result

- Passive local transfer peaks at DC (`peak/DC = 1.0`).
- Quasi-active local transfer peaks at `0.319068 rad/step`, corresponding to about `19.69` steps per cycle, with `peak/DC = 1.9191`.
- With 24 identical same-site pings, the passive cable prefers interval 4 over interval 20 by `+0.497510` mean post-ping voltage.
- The quasi-active cable reverses that preference: interval 20 exceeds interval 4 by `+0.147056`.
- A tuned two-state point resonator reaches `peak/DC = 3.2023`, beating the cable's `1.9191` on this single-site selectivity metric.

## Interpretation

Timing is a valid receiver-side addressing dimension: the event need not carry an explicit frequency label for its temporal pattern to select receiver dynamics.

The point attacker is equally important. This gate does **not** show that dendritic morphology is required for frequency decoding. The next morphology test must combine spatially distributed contacts with heterogeneous local temporal dynamics and compare that compound mechanism against a matched bank of point/vector resonators.

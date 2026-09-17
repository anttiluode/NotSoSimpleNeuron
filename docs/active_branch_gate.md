# Active local interaction gate

This gate asks whether a local voltage-dependent branch mechanism can distinguish spatially nearby excitation from crossed excitation when total charge and class centroid are matched.

The four-pattern construction is deliberately balanced:

```text
positive: (a,a+1) and (b,b+1)
negative: (a,b) and (a+1,b+1)
```

Every pattern has equal total input. The positive and negative classes have the same centroid. Passive response class gaps are zero to floating-point precision, and setting the active gain to zero removes the effect.

Frozen 64-world receipt: `results/v1.json`.

## Result

- Nominal regime: `64/64` worlds pass; mean active margin `0.429997`; worst margin `0.302040`.
- Stress regime: `63/64` worlds pass; mean active margin `0.398905`; one retained reversal at seed 25 with margin `-0.011669`.
- Passive, centroid, linear score-sum, and gain-zero controls remain at numerical zero.

## Interpretation

The synthetic local conductance demonstrates that spatially local state can matter computationally beyond passive superposition on this construction. The single stress reversal is part of the result, not a tuning target to hide.

This is a mechanism witness, not a claim that the model is a faithful NMDA receptor model or that no richer point architecture can implement the same input-output map.

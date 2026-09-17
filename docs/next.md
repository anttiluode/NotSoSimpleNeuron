# Next

The linear branch-bank question is now closed for the current model: the 48-state cable/recovery system has an exact 48-state modal realization under an orthogonal change of basis.

The next gate must therefore be **state-conditioned** rather than another fixed-LTI comparison.

Fix one signal route `R`. Use a second context route (or a branch-local gate) to set the resident state, then measure the effective local/operator map for `R` across contexts:

```text
context route -> resident state x_res
                         |
signal route R ----------+--> local active branch --> readout
                         |
                         +--> J_R(x_res) / H_R(omega; x_res)
```

Primary receipt: how much the signal route's effective operator/column rotates as resident state changes, with gain-zero/passive controls.

The attacker must now be a **nonlinear non-morphological model matched on state count and learnable-parameter count**. A fixed LTI resonator bank is no longer a sufficient control because the modal-boundary gate already proves the LTI case collapses exactly.

If state-conditioned rotation survives that matched nonlinear attacker, the next experiment should test **shared operator reuse across many routes** as a compression/sample-efficiency claim rather than unique expressivity.

# Active Branch Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and falsify-test the smallest local voltage-dependent dendritic nonlinearity that distinguishes nearby equal-charge input pairs from crossed pairs.

**Architecture:** Add a focused `active.py` module containing one `ActiveCableBranch` and pure helpers for voltage gating. Add a separate v1 experiment module so v0 receipts remain frozen. Scientific tests attack the mechanism with equal-charge passive, gain-zero, and linear-point controls before the implementation is accepted.

**Tech Stack:** Python 3.11/3.12, NumPy, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-active-branch-design.md`

## Global Constraints

- Keep v0 behavior and `results/v0.json` unchanged.
- No SciPy or machine-learning dependency.
- Active current is synthetic and must be described as NMDA-like, not biophysical NMDA.
- Every pattern uses exactly two 0.5 contacts.
- The v1 frozen receipt uses 64 deterministic parameter worlds.

---

### Task 1: Scientific tests first

**Files:**
- Create: `tests/test_active.py`
- Create: `tests/test_v1_experiment.py`

**Interfaces:**
- Consumes: `passive_cable_operator` from `cable.py`.
- Produces expected API: `ActiveCableBranch`, `spatial_xor_patterns`, `run_v1_world`, `run_v1_suite`.

- [ ] Write tests asserting passive equal-charge response equality, identical class centroids, point-score sum identity, active close/far separation, gain-zero ablation, and 64-world success.
- [ ] Push only tests and verify CI fails because the v1 API does not exist.

### Task 2: Minimal active cable

**Files:**
- Create: `src/not_so_simple_neuron/active.py`
- Modify: `src/not_so_simple_neuron/__init__.py`

**Interfaces:**
- `ActiveCableBranch(operator, threshold=0.32, slope=0.02, gain=1.0, conductance_decay=0.65, reversal=1.0)`
- `step(injection=None) -> ndarray`
- `reset() -> None`
- properties `state`, `conductance`, `last_active_current`.

- [ ] Implement validation and numerically stable sigmoid.
- [ ] Implement conductance trace, cable-prefiltered voltage, voltage gate, saturating active current, and reset.
- [ ] Run CI and verify active unit tests pass.

### Task 3: v1 experiment and receipt

**Files:**
- Create: `src/not_so_simple_neuron/active_experiment.py`
- Create: `experiments/run_v1.py`
- Create: `results/v1.json`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- `spatial_xor_patterns(n, a, b) -> dict[str, list[ndarray]]`
- `run_v1_world(seed) -> dict`
- `run_v1_suite(seeds=64) -> dict`

- [ ] Generate four balanced patterns from two local neighborhoods.
- [ ] Sample deterministic parameter worlds: leak `[0.04,0.12]`, coupling `[0.12,0.24]`, threshold `[0.30,0.34]`, slope `[0.012,0.025]`, gain `[0.6,1.2]`; use interior neighborhood anchors.
- [ ] Record passive gap, centroid gap, score-sum identity error, active margin, active ratio, and gain-zero gap.
- [ ] Freeze 64-seed JSON receipt.
- [ ] Add a four-seed v1 smoke command to CI.

### Task 4: Explain the result without overclaiming

**Files:**
- Modify: `README.md`
- Create: `docs/v1_active_branch.md`

- [ ] Explain the XOR-like spatial construction and why a single linear-threshold point unit cannot perfectly classify it.
- [ ] Report frozen v1 metrics.
- [ ] State that a two-layer point network can implement the same interaction; the claim is about where the nonlinearity lives, not unique expressivity.
- [ ] Keep branch-bank/SOM/PV/AIS work in the next-gates section.

### Task 5: Verification and integration

- [ ] Run the full pytest suite in GitHub CI on Python 3.11 and 3.12.
- [ ] Run the v0 and v1 smoke experiments in CI.
- [ ] Open PR, inspect changed files and CI, then merge only when green.

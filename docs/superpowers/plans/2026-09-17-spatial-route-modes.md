# Spatial Route Modes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal NumPy research model showing whether one near-binary route can acquire high-dimensional receiver-side meaning by owning several scalar synapses at different positions on a passive dendritic cable.

**Architecture:** A symmetric discrete passive cable supplies the spatial operator and modal basis. Each route owns non-negative scalar contacts at named cable positions; an optional temporal transducer scales the route event before injection. A local route-conditioned spatial plasticity rule redistributes fixed total route strength across contacts. Deterministic experiments compare learned multi-site routes with route-label shuffles, a single-site attacker, and a point-scalar attacker.

**Tech Stack:** Python 3.11+, NumPy, pytest, standard library JSON/argparse.

**Spec:** `docs/superpowers/specs/2026-09-17-spatial-route-modes-design.md`

## Global Constraints

- NumPy only at runtime.
- All core experiments deterministic from explicit seeds.
- Passive cable v0 must remain linear; nonlinear branch dynamics are a later gate.
- Route contact weights are non-negative and L1-normalized.
- Do not claim literal resonance for the passive cable; report damped modes/modal fingerprints.
- Dense vector lookup is an expressivity baseline, not an enemy to be hidden.

---

### Task 1: Passive cable and routes

**Files:**
- Create: `src/not_so_simple_neuron/cable.py`
- Create: `src/not_so_simple_neuron/routes.py`
- Create: `src/not_so_simple_neuron/__init__.py`
- Test: `tests/test_cable.py`

**Interfaces:**
- Produces: `passive_cable_operator(n, leak, coupling) -> np.ndarray`
- Produces: `modal_basis(operator) -> tuple[np.ndarray, np.ndarray]`
- Produces: `CableBranch(operator, state=None)` with `step(injection)` and `reset()`
- Produces: `SpatialRoute(positions, weights, n_compartments)` with `injection(scale=1.0)` and `normalize()`

- [ ] **Step 1: Write failing tests** for stable cable spectrum, orthonormal modal basis, linear superposition, route equal-charge normalization, and position-sensitive route injections.
- [ ] **Step 2: Run `pytest tests/test_cable.py -q`** and confirm failures are due to missing production modules.
- [ ] **Step 3: Implement the minimal cable and route objects.** Use `A = I - leak*I - coupling*L` with a path-graph Laplacian and reject unstable parameter combinations.
- [ ] **Step 4: Run `pytest tests/test_cable.py -q`** and require all Task 1 tests to pass.
- [ ] **Step 5: Commit** the tested cable/route implementation.

### Task 2: Spatial scalar plasticity

**Files:**
- Create: `src/not_so_simple_neuron/learning.py`
- Test: `tests/test_learning.py`

**Interfaces:**
- Consumes: `SpatialRoute`
- Produces: `spatial_hebb_update(route, local_state, event, eta) -> SpatialRoute`
- Produces: `cosine_alignment(a, b) -> float`

- [ ] **Step 1: Write failing tests** showing that inactive routes do not change, route total strength remains one, non-negative weights remain non-negative, and repeated pairing moves mass toward locally active contact positions.
- [ ] **Step 2: Run `pytest tests/test_learning.py -q`** and confirm expected failures.
- [ ] **Step 3: Implement the minimal local update:** `w_j += eta * event * max(local_state[position_j], 0)` followed by non-negative L1 normalization.
- [ ] **Step 4: Run `pytest tests/test_learning.py -q`** and then `pytest -q`.
- [ ] **Step 5: Commit** the learning rule and tests.

### Task 3: Temporal knee at the route/branch boundary

**Files:**
- Create: `src/not_so_simple_neuron/transducer.py`
- Test: `tests/test_transducer.py`

**Interfaces:**
- Produces: `DirectTransducer`, `LeakyTraceTransducer(decay)`, and `SoftKneeTransducer(decay, threshold, slope)` with `step(event) -> float` and `reset()`.

- [ ] **Step 1: Write failing tests** requiring all transducers to have matched immediate gain for one isolated unit event, while the soft knee amplifies a close pair relative to the matched linear trace.
- [ ] **Step 2: Run `pytest tests/test_transducer.py -q`** and verify red.
- [ ] **Step 3: Implement the three transducers** with the soft-knee output normalized so the first isolated unit event has gain one.
- [ ] **Step 4: Run `pytest tests/test_transducer.py -q`** and then the full suite.
- [ ] **Step 5: Commit** the transducer implementation.

### Task 4: Deterministic scientific gates

**Files:**
- Create: `src/not_so_simple_neuron/experiment.py`
- Create: `experiments/run_v0.py`
- Create: `tests/test_experiment.py`
- Create after verification: `results/v0.json`

**Interfaces:**
- Produces: `run_seed(seed, n_compartments=12, train_steps=400) -> dict`
- Produces: `run_experiment(seeds) -> dict`

- [ ] **Step 1: Write failing tests** for the result schema and gate semantics: cable invariants pass; fixed equal-charge spatial routes have nonzero response/modal separation while the point-scalar attacker has zero separation; learned paired alignment exceeds route-label shuffle; multi-site learned response beats a best-single-site reconstruction on the paired target; knee pair gain exceeds linear trace pair gain.
- [ ] **Step 2: Run `pytest tests/test_experiment.py -q`** and verify red.
- [ ] **Step 3: Implement deterministic route prototypes and training.** Use two smooth non-negative target states centered at opposite cable regions, identical allowed contact positions for both routes, uniform initial weights, additive small non-negative training noise, and explicit seed control.
- [ ] **Step 4: Implement attackers and metrics.** Point attacker sees only total route charge. Single-site attacker selects the allowed contact whose cable response best aligns to the target. Dense vector lookup is reported as a reference capable of exact injection matching and is not counted as a failure.
- [ ] **Step 5: Run `pytest tests/test_experiment.py -q`** and then `pytest -q`.
- [ ] **Step 6: Run `python experiments/run_v0.py --seeds 64 --out results/v0.json`** and freeze the deterministic receipt only after inspecting all aggregate metrics.
- [ ] **Step 7: Commit** the experiment, receipt, and tests.

### Task 5: Documentation and CI

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.github/workflows/ci.yml`
- Create: `docs/NOTES.md`

**Interfaces:**
- Documents the exact v0 claim, failures/limitations, equations, attackers, reproduction commands, and next gates.

- [ ] **Step 1: Write README and notes** that distinguish passive damped modes from literal resonance, explain that route geometry is a structured expansion rather than magic information creation, and state that a dense vector lookup can reproduce fixed responses.
- [ ] **Step 2: Add package/test configuration and CI** for Python 3.11 and 3.12.
- [ ] **Step 3: Run `python -m pip install -e '.[test]'`, `pytest -q`, and a small scientific smoke run.**
- [ ] **Step 4: Commit** documentation and CI.

### Task 6: Completion review

**Files:** none unless verification finds a defect.

- [ ] **Step 1: Re-run the full test suite and 64-seed receipt.**
- [ ] **Step 2: Compare the frozen receipt with a fresh run.** Require exact structure and numerically stable metrics.
- [ ] **Step 3: Review claims against the spec.** If multi-site learning does not beat the single-site attacker or paired alignment does not beat shuffle, document the negative result instead of moving thresholds.
- [ ] **Step 4: Open a pull request** from `sol/v0-spatial-modes` to `main` with the measured results and limitations.

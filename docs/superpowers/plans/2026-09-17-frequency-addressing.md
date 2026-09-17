# Frequency Addressing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a frozen frequency-addressing experiment that distinguishes passive low-pass filtering, genuine quasi-active resonance, and a tuned point-resonator attacker.

**Architecture:** Keep the existing passive cable unchanged. Add a focused `frequency.py` module containing the quasi-active cable, point attacker, transfer-function utilities, and identical-ping-train probe. Add a small `frequency_experiment.py` receipt layer and one CLI runner; do not mix these dynamics into the nonlinear `ActiveCableBranch` yet.

**Tech Stack:** Python 3.11+, NumPy, pytest.

**Spec:** `docs/superpowers/specs/2026-09-17-frequency-addressing-design.md`

## Global Constraints

- Same spatial landing site for all frequency comparisons.
- Passive cable must not be described as resonant.
- Quasi-active dynamics must be checked for discrete-time stability.
- The tuned point attacker is allowed to win; its result must be reported.
- Existing v0 behavior and tests must remain unchanged.

---

### Task 1: Define frequency gate tests

**Files:**
- Create: `tests/test_frequency.py`

**Interfaces:**
- Consumes: `passive_cable_operator` from `cable.py`.
- Produces required APIs: `ResonantCableBranch`, `PointResonator`, `local_frequency_response`, `pulse_train_response`, `best_point_attacker`.

- [ ] Write tests proving passive response peaks at DC, nominal quasi-active response peaks at non-zero frequency, identical same-site ping trains with different intervals diverge, and the point attacker returns an explicit outcome.
- [ ] Run only `tests/test_frequency.py` and verify RED because `not_so_simple_neuron.frequency` does not exist.

### Task 2: Implement linear frequency dynamics

**Files:**
- Create: `src/not_so_simple_neuron/frequency.py`

**Interfaces:**
- `ResonantCableBranch(operator, recovery_gain=0.3, recovery_decay=0.8, recovery_coupling=0.15)`
- `PointResonator(persistence, recovery_gain=0.3, recovery_decay=0.8, recovery_coupling=0.15)`
- `local_frequency_response(state_matrix, input_vector, output_vector, omegas)`
- `pulse_train_response(model_factory, site, interval, count, burn_in)`
- `best_point_attacker(omegas, branch_response, ...)`

- [ ] Implement the minimum stable state updates and transfer calculation needed by the tests.
- [ ] Run `tests/test_frequency.py` and verify GREEN.

### Task 3: Freeze the scientific receipt

**Files:**
- Create: `src/not_so_simple_neuron/frequency_experiment.py`
- Create: `experiments/run_frequency_gate.py`
- Create: `results/frequency_gate.json`
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- `run_frequency_gate(n=12, site=5, points=257) -> dict`

- [ ] Compute passive peak frequency, resonant peak frequency and peak/DC ratio, fast/slow identical-ping response difference, and best tuned point-attacker selectivity.
- [ ] Record whether the point attacker matches/beats, loses, or ties without changing the gate verdict.
- [ ] Add the frozen receipt and concise README interpretation.
- [ ] Add a CI smoke invocation.
- [ ] Run the full test suite plus the runner and verify all outputs.

### Task 4: Resume active-branch gate

**Files:**
- Existing: `src/not_so_simple_neuron/active.py`
- Create: `src/not_so_simple_neuron/active_experiment.py`
- Existing tests: `tests/test_active.py`, `tests/test_v1_experiment.py`

- [ ] Only after the frequency gate is green, continue the already-red active-branch tests.
- [ ] Keep frequency resonance and NMDA-like local conductance as separate mechanisms and receipts.

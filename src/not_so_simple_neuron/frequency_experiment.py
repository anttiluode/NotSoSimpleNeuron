from __future__ import annotations

import numpy as np

from .cable import CableBranch, passive_cable_operator
from .frequency import (
    ResonantCableBranch,
    best_point_attacker,
    local_frequency_response,
    pulse_train_response,
)


def run_frequency_gate(
    n: int = 12,
    site: int = 5,
    points: int = 257,
    fast_interval: int = 4,
    preferred_interval: int = 20,
    ping_count: int = 24,
    burn_in: int = 8,
) -> dict:
    if n < 2:
        raise ValueError("n must be at least 2")
    if not (0 <= site < n):
        raise ValueError("site out of range")
    if points < 3:
        raise ValueError("points must be at least 3")

    A = passive_cable_operator(n, leak=0.08, coupling=0.18)
    omegas = np.linspace(0.0, np.pi, points)

    local = np.zeros(n, dtype=float)
    local[site] = 1.0
    passive_response = local_frequency_response(A, local, local, omegas)
    passive_peak_index = int(np.argmax(passive_response))

    resonant = ResonantCableBranch(A)
    resonant_response = resonant.local_frequency_response(site=site, omegas=omegas)
    resonant_peak_index = int(np.argmax(resonant_response))
    resonant_ratio = float(resonant_response[resonant_peak_index] / resonant_response[0])

    passive_fast = pulse_train_response(
        lambda: CableBranch(A),
        site=site,
        interval=fast_interval,
        count=ping_count,
        burn_in=burn_in,
    )
    passive_preferred = pulse_train_response(
        lambda: CableBranch(A),
        site=site,
        interval=preferred_interval,
        count=ping_count,
        burn_in=burn_in,
    )
    resonant_fast = pulse_train_response(
        lambda: ResonantCableBranch(A),
        site=site,
        interval=fast_interval,
        count=ping_count,
        burn_in=burn_in,
    )
    resonant_preferred = pulse_train_response(
        lambda: ResonantCableBranch(A),
        site=site,
        interval=preferred_interval,
        count=ping_count,
        burn_in=burn_in,
    )

    point_attack = best_point_attacker(omegas, resonant_response)

    equal_charge = bool(
        np.isclose(passive_fast["total_charge"], passive_preferred["total_charge"])
        and np.isclose(resonant_fast["total_charge"], resonant_preferred["total_charge"])
        and np.isclose(passive_fast["total_charge"], resonant_fast["total_charge"])
    )
    passive_fast_minus_preferred = float(
        passive_fast["mean_post_ping_voltage"] - passive_preferred["mean_post_ping_voltage"]
    )
    resonant_preferred_minus_fast = float(
        resonant_preferred["mean_post_ping_voltage"] - resonant_fast["mean_post_ping_voltage"]
    )

    passed = bool(
        passive_peak_index == 0
        and resonant.spectral_radius < 1.0
        and resonant_peak_index > 0
        and resonant_ratio > 1.5
        and equal_charge
        and passive_fast_minus_preferred > 0.30
        and resonant_preferred_minus_fast > 0.10
    )

    return {
        "verdict": (
            "PASS_TEMPORAL_ADDRESSING_POINT_NOT_NEEDED_FOR_CLAIM"
            if passed
            else "FAIL_TEMPORAL_ADDRESSING"
        ),
        "configuration": {
            "compartments": int(n),
            "site": int(site),
            "frequency_points": int(points),
            "fast_interval": int(fast_interval),
            "preferred_interval": int(preferred_interval),
            "ping_count": int(ping_count),
            "burn_in": int(burn_in),
            "recovery_gain": float(resonant.recovery_gain),
            "recovery_decay": float(resonant.recovery_decay),
            "recovery_coupling": float(resonant.recovery_coupling),
        },
        "passive": {
            "peak_frequency": float(omegas[passive_peak_index]),
            "peak_gain": float(passive_response[passive_peak_index]),
            "dc_gain": float(passive_response[0]),
            "peak_to_dc": float(passive_response[passive_peak_index] / passive_response[0]),
        },
        "resonant": {
            "spectral_radius": float(resonant.spectral_radius),
            "peak_frequency": float(omegas[resonant_peak_index]),
            "peak_period_steps": float(2.0 * np.pi / omegas[resonant_peak_index]),
            "peak_gain": float(resonant_response[resonant_peak_index]),
            "dc_gain": float(resonant_response[0]),
            "peak_to_dc": resonant_ratio,
        },
        "ping_probe": {
            "equal_total_charge": equal_charge,
            "total_charge_each": float(resonant_fast["total_charge"]),
            "passive_fast": passive_fast,
            "passive_preferred": passive_preferred,
            "resonant_fast": resonant_fast,
            "resonant_preferred": resonant_preferred,
            "passive_fast_minus_preferred": passive_fast_minus_preferred,
            "resonant_preferred_minus_fast": resonant_preferred_minus_fast,
        },
        "point_attacker": point_attack,
        "interpretation": {
            "passive": "rate selectivity without resonance: local transfer peaks at DC",
            "quasi_active": "one recovery state creates a non-zero-frequency preference",
            "attacker": "point result is reported; a point win does not invalidate temporal addressing",
        },
    }

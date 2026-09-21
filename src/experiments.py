"""
experiments.py -- Monte Carlo CPBR(f) curve, saturation point, and (later)
hardening comparison, per Section 9.5/9.6 of the research guide.

This wraps your existing power_case.py / cyber_graph.py / propagation.py
pipeline. It does NOT change how a single run works -- it repeats it many
times per f value with different random seeds and reports mean +/- standard
error, which is what Section 4.5 actually asks for (CPBR is an *expectation*
over randomized detonation sets, not a single run).
"""

import csv
import os
import uuid

import numpy as np

from power_case import (
    load_power_case,
    apply_payload_power,
    damage_metric_power,
    mapping_rule_power,
    get_baseline_voltage_violations,
    get_unavailable_cyber_nodes,
)
from cyber_graph import build_cyber_graph
from propagation import simulate_propagation


def run_once(G_c, mu, seed, f, beta=0.3, seed_fraction=0.05, max_steps=40):
    """One full simulation: fresh baseline net, one propagation run, one
    damage measurement. Returns None if detonation never triggered (f was
    never reached within max_steps for this seed)."""
    net = load_power_case()
    baseline_load = net.load.p_mw.sum()
    baseline_violations = get_baseline_voltage_violations(net)

    infected, unavailable, det_step, det_lines, net = simulate_propagation(
        G_c, mu, net,
        beta=beta, seed_fraction=seed_fraction, max_steps=max_steps,
        detonate_at_fraction=f, seed=seed,
        apply_payload_fn=apply_payload_power,
        get_unavailable_fn=get_unavailable_cyber_nodes,
    )
    if det_step is None:
        return None

    damage = damage_metric_power(net, baseline_load, baseline_violations)
    return damage["unserved_fraction"]


def cpbr_curve(G_c, mu, f_values, n_monte_carlo=100, beta=0.3,
               seed_fraction=0.05, max_steps=40, base_seed=1000,
               log_path=None, verbose=True):
    """
    Returns (means, standard_errors, n_detonated) arrays, one entry per f.

    Each f value is run n_monte_carlo times with seeds base_seed, base_seed+1,
    ... base_seed+n_monte_carlo-1 -- the SAME seed sequence is reused across
    f values, so run i at f=0.2 and run i at f=0.5 share the same pre-
    detonation randomness up to the point their thresholds diverge. That
    makes the curve less noisy for a fixed compute budget than drawing an
    independent seed pool per f, and it's a defensible, explainable choice
    (state it in your Experimental Setup subsection).
    """
    means, ses, n_det_list = [], [], []

    for f in f_values:
        damages = []
        for i in range(n_monte_carlo):
            seed = base_seed + i
            d = run_once(G_c, mu, seed, f, beta, seed_fraction, max_steps)
            if d is not None:
                damages.append(d)
            if log_path is not None:
                log_run(
                    log_path,
                    f_target=f, seed=seed, beta=beta,
                    seed_fraction=seed_fraction,
                    unserved_fraction=d if d is not None else "",
                    detonated=d is not None,
                )

        damages = np.array(damages, dtype=float)
        n_det = len(damages)
        mean = float(damages.mean()) if n_det else float("nan")
        se = float(damages.std(ddof=1) / np.sqrt(n_det)) if n_det > 1 else 0.0

        means.append(mean)
        ses.append(se)
        n_det_list.append(n_det)

        if verbose:
            print(f"f={f:.2f}: detonated {n_det}/{n_monte_carlo} runs | "
                  f"mean unserved_fraction={mean:.4f} +/- {se:.4f} (SE)")

    return np.array(means), np.array(ses), np.array(n_det_list)


def find_saturation_point(f_values, mean_damages, epsilon=0.01):
    """
    f* = smallest f beyond which every subsequent slope stays below epsilon.
    epsilon is in damage-fraction per unit-f (e.g. 0.01 = "no more than 1
    percentage point of extra damage per 100 percentage points of extra
    infection" -- state and justify your epsilon in the paper, per Section 4.6).
    """
    f_values = np.asarray(f_values, dtype=float)
    mean_damages = np.asarray(mean_damages, dtype=float)
    valid = ~np.isnan(mean_damages)
    f_values, mean_damages = f_values[valid], mean_damages[valid]
    if len(f_values) < 2:
        return float("nan")

    slopes = np.diff(mean_damages) / np.diff(f_values)
    for i, s in enumerate(slopes):
        if all(s2 < epsilon for s2 in slopes[i:]):
            return float(f_values[i])
    return float(f_values[-1])


def log_run(path, **fields):
    """Append one row to a reproducibility CSV, per Section 9.6."""
    fields.setdefault("run_id", str(uuid.uuid4())[:8])
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)  # create results/ if it doesn't exist yet
    write_header = not os.path.exists(path)
    with open(path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fields.keys()))
        if write_header:
            w.writeheader()
        w.writerow(fields)


if __name__ == "__main__":
    # results/ is created next to src/ regardless of which directory you run
    # this from (e.g. `python src/experiments.py` from the project root, or
    # `python experiments.py` from inside src/ both work the same way).
    _here = os.path.dirname(os.path.abspath(__file__))
    _log_path = os.path.join(_here, "..", "results", "cpbr_runs.csv")

    net = load_power_case()
    G_c, mu = build_cyber_graph(net, mapping_rule_power, seed=42)

    f_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    means, ses, n_det = cpbr_curve(
        G_c, mu, f_values, n_monte_carlo=60,
        log_path=_log_path,
    )

    f_star = find_saturation_point(f_values, means, epsilon=0.01)
    print(f"\nEstimated saturation point f* = {f_star:.2f}")
    print(f"Run log written to: {os.path.abspath(_log_path)}")
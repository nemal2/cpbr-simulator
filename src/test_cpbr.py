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


# 1. Load physical power network
net = load_power_case()
baseline_load = net.load.p_mw.sum()
baseline_violations = get_baseline_voltage_violations(net)
print("Baseline load:", baseline_load, "MW")

# 2. Build cyber graph + mapping
G_c, mu = build_cyber_graph(net, mapping_rule_power, seed=42)
print("\nCyber nodes:", len(G_c.nodes))
print("Cyber edges:", len(G_c.edges))

# 3. Run propagation with the feedback loop wired in
print("\nStarting cyber propagation...\n")

infected, unavailable, detonation_step, detonated_lines, net = simulate_propagation(
    G_c, mu, net,
    beta=0.3, seed_fraction=0.05, max_steps=40, detonate_at_fraction=0.5, seed=42,
    apply_payload_fn=apply_payload_power,
    get_unavailable_fn=get_unavailable_cyber_nodes,
)

# 4. Report results
if detonation_step is None:
    print("\nNo detonation occurred.")
else:
    print("\nDetonation step:", detonation_step)
    print("\nPhysical lines targeted at detonation:", detonated_lines)
    print("\nTotal cyber nodes infected by end of run:", sorted(infected))
    print("\nCyber nodes made unavailable by the payload:", sorted(unavailable))

    damage = damage_metric_power(net, baseline_load, baseline_violations)

    print("\n==============================")
    print("CYBER-PHYSICAL ATTACK RESULT")
    print("==============================")
    print("\nUnserved load fraction:", damage["unserved_fraction"])
    print("Voltage violations:", damage["voltage_violations"])
    print("Overloaded lines:", damage["overloaded_lines"])
    print("Maximum line loading:", damage["max_line_loading"], "%")
    print("\nMinimum voltage (solved buses only):", net.res_bus.vm_pu.dropna().min())
    print("Maximum voltage (solved buses only):", net.res_bus.vm_pu.dropna().max())

    print("\n==============================")
    print("BUS RESULTS")
    print("==============================")
    print(net.res_bus[["vm_pu", "va_degree", "p_mw", "q_mvar"]])

    print("\n==============================")
    print("LINE RESULTS")
    print("==============================")
    print(net.res_line[["loading_percent", "p_from_mw", "p_to_mw"]])

# 5. Standalone sanity check (unaffected by anything above)
print("\n\n=== SANITY CHECK: single interior line outage ===")
sanity_net = load_power_case()
sanity_baseline_load = sanity_net.load.p_mw.sum()
sanity_baseline_violations = get_baseline_voltage_violations(sanity_net)
sanity_net = apply_payload_power(sanity_net, [6])
print(damage_metric_power(sanity_net, sanity_baseline_load, sanity_baseline_violations))
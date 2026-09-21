from power_case import load_power_case, mapping_rule_power
from cyber_graph import build_cyber_graph
from propagation import simulate_propagation


# Load physical power network
net = load_power_case()

# Build cyber graph + cyber-to-physical mapping
G_c, mu = build_cyber_graph(
    net,
    mapping_rule_power
)

print("Number of cyber nodes:", len(G_c.nodes))
print("Number of cyber edges:", len(G_c.edges))

print("\nCyber nodes:")
print(list(G_c.nodes))

print("\nCyber -> physical mapping:")
print(mu)

print("\nStarting propagation...\n")

history, infected, detonation_step = simulate_propagation(
    G_c,
    beta=0.3,
    seed_fraction=0.05,
    max_steps=40,
    detonate_at_fraction=0.5,
    seed=42
)

print("\nFinal infected nodes:")
print(infected)

print("\nDetonation step:")
print(detonation_step)

print("\nInfection history:")
print(history)
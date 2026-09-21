from power_case import (
    load_power_case,
    mapping_rule_power
)

from cyber_graph import build_cyber_graph


# -------------------------
# 1. Load physical network
# -------------------------

net = load_power_case()

print("IEEE 14-bus network loaded.")


# -------------------------
# 2. Build cyber network
# -------------------------

G_c, mu = build_cyber_graph(
    net,
    mapping_rule_power
)


# -------------------------
# 3. Show what we created
# -------------------------

print("\nCyber nodes:")
print(list(G_c.nodes))

print("\nCyber edges:")
print(list(G_c.edges))

print("\nCyber -> physical mapping:")
for cyber_node, physical_element in mu.items():
    print(
        cyber_node,
        "-> physical line",
        physical_element
    )
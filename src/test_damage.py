from power_case import load_power_case
import pandapower as pp

net = load_power_case()

print("================================")
print("POWER FLOW DIAGNOSTICS")
print("================================")

print("Converged:", getattr(net, "converged", None))

print("\nBUS CONFIGURATION")
print(net.bus[[
    "vn_kv",
    "in_service"
]])

print("\nEXTERNAL GRID")
print(net.ext_grid)

print("\nGENERATORS")
print(net.gen)

print("\nLOADS")
print(net.load[[
    "bus",
    "p_mw",
    "q_mvar",
    "in_service"
]])

print("\nLINES")
print(net.line[[
    "from_bus",
    "to_bus",
    "length_km",
    "r_ohm_per_km",
    "x_ohm_per_km",
    "in_service"
]])

print("\nBUS RESULTS")
print(net.res_bus[[
    "vm_pu",
    "va_degree",
    "p_mw",
    "q_mvar"
]])

print("\nLINE RESULTS")
print(net.res_line[[
    "loading_percent",
    "p_from_mw",
    "p_to_mw"
]])
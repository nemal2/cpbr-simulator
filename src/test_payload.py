import pandapower as pp

from power_case import load_power_case, apply_payload_power


# ---------------------------------
# 1. Baseline
# ---------------------------------

net = load_power_case()

print("Baseline power flow:")
print(net.res_bus[["vm_pu"]])


# ---------------------------------
# 2. Apply physical payload
# ---------------------------------

print("\nDisabling physical line 0...")

try:

    net = apply_payload_power(net, [0])

    print("\nAfter disabling line 0:")
    print(net.res_bus[["vm_pu"]])

    print("\nMinimum voltage:")
    print(net.res_bus.vm_pu.min())

    print("\nMaximum voltage:")
    print(net.res_bus.vm_pu.max())

except pp.LoadflowNotConverged:

    print("\nPower flow did NOT converge after the attack.")
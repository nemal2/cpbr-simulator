import pandapower as pp
from power_case import load_power_case


for line_idx in range(15):

    net = load_power_case()

    print(f"\nTesting line {line_idx}")

    # Disable one physical line
    net.line.at[line_idx, "in_service"] = False

    try:
        pp.runpp(net)

        print("  Power flow: CONVERGED")
        print(
            "  Minimum voltage:",
            net.res_bus.vm_pu.min()
        )
        print(
            "  Maximum voltage:",
            net.res_bus.vm_pu.max()
        )

    except Exception as e:
        print("  Power flow: FAILED")
        print("  Reason:", type(e).__name__)
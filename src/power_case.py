import pandapower as pp
import pandapower.networks as pn
import pandapower.topology as top
import networkx as nx


def load_power_case():
    net = pn.case14()
    pp.runpp(net)
    return net


def mapping_rule_power(net):
    return {
        f"cyber_line_{i}": line_idx
        for i, line_idx in enumerate(net.line.index)
    }


def apply_payload_power(net, detonated_lines):
    for line_idx in detonated_lines:
        if line_idx in net.line.index:
            net.line.at[line_idx, "in_service"] = False
    try:
        pp.runpp(net, enforce_q_lims=True)
    except pp.LoadflowNotConverged:
        pass
    return net


def get_baseline_voltage_violations(net_baseline):
    vm = net_baseline.res_bus.vm_pu.dropna()
    return int(((vm < 0.95) | (vm > 1.05)).sum())


def damage_metric_power(net, baseline_load, baseline_violations=0):
    if not getattr(net, "converged", True):
        return {
            "unserved_fraction": 1.0,
            "voltage_violations": len(net.bus) - baseline_violations,
            "overloaded_lines": 0,
            "max_line_loading": float("nan"),
        }

    served = net.res_load.p_mw.sum()
    unserved_fraction = max(0.0, 1 - served / baseline_load)

    vm = net.res_bus.vm_pu.dropna()
    raw_violations = int(((vm < 0.95) | (vm > 1.05)).sum())
    voltage_violations = max(0, raw_violations - baseline_violations)

    active_lines = net.line.index[net.line.in_service]
    loading = net.res_line.loc[active_lines, "loading_percent"].dropna()
    overloaded_lines = int((loading > 100).sum())
    max_line_loading = float(loading.max()) if len(loading) else 0.0

    return {
        "unserved_fraction": unserved_fraction,
        "voltage_violations": voltage_violations,
        "overloaded_lines": overloaded_lines,
        "max_line_loading": max_line_loading,
    }


def get_unavailable_cyber_nodes(net, mu):
    """
    Returns the set of cyber nodes whose mapped line now has at least one
    endpoint bus electrically disconnected from every slack/reference bus.
    This is the avail() gating term from Section 4.2/4.4 of your guide.
    """
    mg = top.create_nxgraph(net, respect_switches=True)
    slack_buses = set(net.ext_grid.bus)

    energized_buses = set()
    for component in nx.connected_components(mg):
        if component & slack_buses:
            energized_buses |= component

    unavailable = set()
    for cyber_node, line_idx in mu.items():
        from_bus = net.line.at[line_idx, "from_bus"]
        to_bus = net.line.at[line_idx, "to_bus"]
        if from_bus not in energized_buses or to_bus not in energized_buses:
            unavailable.add(cyber_node)
    return unavailable
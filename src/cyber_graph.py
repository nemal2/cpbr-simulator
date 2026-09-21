import networkx as nx
import random


def build_cyber_graph(physical_net, mapping_rule, seed=None):
    mu = mapping_rule(physical_net)

    G_c = nx.Graph()
    G_c.add_nodes_from(mu.keys())

    rng = random.Random(seed)

    # Shuffle ring order so cyber-adjacency isn't accidentally correlated
    # with which physical lines happen to be structurally critical
    # (e.g. the two lines touching the slack bus). A real OT network's
    # communication topology has no reason to mirror line-index order.
    nodes = list(mu.keys())
    rng.shuffle(nodes)

    for i in range(len(nodes)):
        G_c.add_edge(nodes[i], nodes[(i + 1) % len(nodes)])

    extra_edges = int(0.15 * len(nodes))
    for _ in range(extra_edges):
        u, v = rng.sample(nodes, 2)
        G_c.add_edge(u, v)

    return G_c, mu
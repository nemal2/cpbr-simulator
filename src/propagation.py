import random


def simulate_propagation(G_c, mu, net, beta=0.3, seed_fraction=0.05,
                          max_steps=40, detonate_at_fraction=0.5, seed=None,
                          apply_payload_fn=None, get_unavailable_fn=None):
    if seed is not None:
        random.seed(seed)

    nodes = sorted(G_c.nodes)
    n_initial = max(1, int(seed_fraction * len(nodes)))
    infected = set(random.sample(nodes, n_initial))
    unavailable = set()
    detonated = False
    detonation_step = None
    detonated_lines = None

    for t in range(max_steps):
        new_infections = set()
        for v in sorted(infected):
            if v in unavailable:
                continue
            for u in sorted(G_c.neighbors(v)):
                if u in infected or u in unavailable:
                    continue
                if random.random() < beta:
                    new_infections.add(u)
        infected.update(new_infections)

        frac = len(infected) / len(nodes)
        status = f"Step {t}: {len(infected)}/{len(nodes)} infected ({frac:.2%})"
        if unavailable:
            status += f" | {len(unavailable)} cyber nodes unavailable"
        print(status)

        if (not detonated) and detonate_at_fraction is not None and frac >= detonate_at_fraction:
            detonated = True
            detonation_step = t
            detonated_lines = sorted(mu[v] for v in infected)
            print(f"\n*** DETONATION at step {t} ({frac:.2%} infected) ***")
            print(f"Physical lines targeted: {detonated_lines}")

            net = apply_payload_fn(net, detonated_lines)
            unavailable = get_unavailable_fn(net, mu)
            print(f"Newly unavailable cyber nodes after payload: {sorted(unavailable)}\n")

        # Stop early once no further change is possible. Only count a node as
        # a "live spreader" if it is infected AND not unavailable -- an
        # unavailable infected node is skipped in the loop above and can
        # never actually transmit, so its neighbors must not be considered
        # when deciding whether the frontier is exhausted. (The previous
        # version checked neighbors of every infected node, including
        # unavailable ones, which meant it never actually detected
        # exhaustion once a payload had knocked any infected node out --
        # it silently ran to max_steps every time.)
        if not new_infections:
            live_spreaders = [v for v in infected if v not in unavailable]
            frontier_exhausted = all(
                u in infected or u in unavailable
                for v in live_spreaders
                for u in G_c.neighbors(v)
            )
            if frontier_exhausted:
                reason = "post-detonation" if detonated else "pre-detonation"
                print(f"(propagation stalled permanently at step {t}, {reason} -- stopping early)\n")
                break

    return infected, unavailable, detonation_step, detonated_lines, net
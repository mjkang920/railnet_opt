# critical_ga.py
import random, json, multiprocessing as mp
from functools import partial
from pathlib import Path

import numpy as np
import networkx as nx
from scipy.stats import norm, qmc
from deap import base as deap_base, creator as deap_creator, tools, algorithms
from deap.tools.emo import sortNondominated, assignCrowdingDist
from tqdm.auto import tqdm
from gurobipy import Model, GRB, quicksum

VERBOSE = True

# System function
def shortestpath_systemfunc(arcs, edges, arc_capacity, demand):
    G = nx.DiGraph()
    for e, (i, j) in edges.items():
        cap = float(arc_capacity.get(e, 0.0))
        if cap > 0.0:
            G.add_edge(i, j, capacity=cap, link_id=e)

    total_demand_pd = sum(
        float(info["amount"]) * float(info["distance"])
        for info in demand.values()
    )
    expected_loss = 0.0

    for k, info in demand.items():
        o, d = info["origin"], info["destination"]
        amt, base_dist = float(info["amount"]), float(info["distance"])
        if (o not in G) or (d not in G):
            expected_loss += amt * base_dist
            continue
        try:
            _ = nx.shortest_path(G, source=o, target=d)
        except nx.NetworkXNoPath:
            expected_loss += amt * base_dist

    return expected_loss, total_demand_pd


def MCNF_systemfunc(arcs, edges, arc_capacity, demand, max_distance, arc_distance, avg_velo,):
    edge_map = {v: k for k, v in edges.items()}

    # Piecewise points (minutes)
    T0, T1, T2, T3 = 15.0, 30.0, 60.0, 120.0
    DELTAS = [0.0, T0, T1, T2, T3]
    GAMMAS = [0.0, 0.25, 0.50, 0.75, 1.0]
    MCOUNT = len(DELTAS)

    # Minutes per meter
    ALPHA = 60.0 / (1000.0 * avg_velo)

    model = Model("MCNF")
    model.Params.OutputFlag = 0

    flow, unmet, delta, gamma, lam = {}, {}, {}, {}, {}
    nodes_set = set(n for a in arcs for n in a)

    for k in demand:
        unmet[k]  = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"u[{k}]")
        delta[k]  = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"delta[{k}]")
        gamma[k]  = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"gamma[{k}]")
        for m in range(MCOUNT):
            lam[k, m] = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"lam[{k},{m}]")
        for (i, j) in arcs:
            eid = edge_map.get((i, j))
            cap = float(arc_capacity.get(eid, 0.0))
            flow[k, i, j] = model.addVar(lb=0.0, ub=cap, vtype=GRB.CONTINUOUS, name=f"f[{k},{i},{j}]")

    model.update()

    out_o, dist_sum = {}, {}
    for k, info in demand.items():
        o = info["origin"]
        out_o[k] = quicksum(flow[k, i, j] for (i, j) in arcs if i == o)
        dist_sum[k] = quicksum(float(arc_distance[edge_map[(i, j)]]) * flow[k, i, j]
                               for (i, j) in arcs if (i, j) in edge_map)

    # Flow conservation
    for k, info in demand.items():
        o, d, amt = info["origin"], info["destination"], float(info["amount"])
        for n in nodes_set:
            inflow  = quicksum(flow[k, i, j] for (i, j) in arcs if j == n)
            outflow = quicksum(flow[k, i, j] for (i, j) in arcs if i == n)
            if n == o:
                model.addConstr(outflow - inflow == amt - unmet[k])
            elif n == d:
                model.addConstr(outflow - inflow == -amt + unmet[k])
            else:
                model.addConstr(outflow - inflow == 0.0)

    # Arc capacity
    for (i, j) in arcs:
        eid = edge_map.get((i, j))
        cap = float(arc_capacity.get(eid, 0.0))
        model.addConstr(quicksum(flow[k, i, j] for k in demand) <= cap)

    # Travel distance limit
    for k in demand:
        model.addConstr(dist_sum[k] <= float(max_distance[k]) * out_o[k])

    # Delay minutes and refund ratio
    for k, info in demand.items():
        d_plan = float(info["distance"])
        Dbar_k = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name=f"Dbar[{k}]")
        model.addConstr(Dbar_k >= dist_sum[k] - d_plan * out_o[k])
        model.addConstr(delta[k] == ALPHA * Dbar_k)

    for k in demand:
        model.addConstr(quicksum(lam[k, m] for m in range(MCOUNT)) == out_o[k])
        model.addConstr(delta[k] == quicksum(DELTAS[m] * lam[k, m] for m in range(MCOUNT)))
        model.addConstr(gamma[k] == quicksum(GAMMAS[m] * lam[k, m] for m in range(MCOUNT)))
        model.addSOS(GRB.SOS_TYPE2, [lam[k, m] for m in range(MCOUNT)], DELTAS)

    # Objective
    obj = quicksum(float(info["distance"]) * (unmet[k] + gamma[k]) for k, info in demand.items())
    model.setObjective(obj, GRB.MINIMIZE)
    model.optimize()

    if model.Status != GRB.OPTIMAL:
        return None, None

    expected_loss = float(model.ObjVal)
    total_demand_pd = sum(float(info["amount"]) * float(info["distance"]) for info in demand.values())

    if VERBOSE:
        print(f"Expected Loss={expected_loss:.6g}, Total Demand PD={total_demand_pd:.6g}")

    return expected_loss, total_demand_pd


def safe_pi(total_dem, eloss, tol=1e-12):
    if not total_dem or eloss is None or total_dem <= 0:
        return 0.0
    num = total_dem - eloss
    if abs(num) <= tol * max(1.0, total_dem):
        num = 0.0
    return float(np.clip(num / total_dem, 0.0, 1.0))


def evaluate_individual(ind_bits, delay_time, sys_name, ctx):
    """
    ctx 예시
    {
        "COMPONENT_IDS": ...,
        "probs": ...,
        "edges": ...,
        "intact_capacity": ...,
        "avg_velo": ...,
        "demand_dict": ...,
        "arcs": ...,
        "arc_distance": ...,
        "MCNF_systemfunc": ...,
    }
    """
    COMPONENT_IDS   = ctx["COMPONENT_IDS"]
    probs           = ctx["probs"]
    edges           = ctx["edges"]
    intact_capacity = ctx["intact_capacity"]
    avg_velo        = ctx["avg_velo"]
    demand_dict     = ctx["demand_dict"]
    arcs            = ctx["arcs"]
    arc_distance    = ctx["arc_distance"]
    mcnf_func       = ctx.get("MCNF_systemfunc", None)

    num_components = len(COMPONENT_IDS)
    if len(ind_bits) != num_components:
        raise ValueError("Invalid individual length")

    # beta
    failed_bases = [COMPONENT_IDS[i] for i, b in enumerate(ind_bits) if b == 0]
    pf_list = []
    for base_id in failed_bases:
        p_dict = probs.get(base_id) or probs.get(base_id + "r")
        if p_dict is None or ("0" not in p_dict):
            raise KeyError(f"Missing probability for {base_id}")
        pf_list.append(float(p_dict["0"]))
    joint_pf = np.prod(pf_list) if pf_list else 0.0
    beta_val = -norm.ppf(joint_pf) if joint_pf > 0 else np.inf

    # capacity
    comps_st = {e: 1 for e in edges}
    for base_id in failed_bases:
        comps_st[base_id] = 0
        rev = base_id + "r"
        if rev in comps_st:
            comps_st[rev] = 0
    arc_cap = {e: float(intact_capacity[e]) * comps_st[e] for e in edges}

    # max distance
    extra_meters = avg_velo * 1000.0 * (delay_time / 60.0)
    max_dist_case = {
        k: info["distance"] + extra_meters
        for k, info in demand_dict.items()
    }

    # system function
    if sys_name == "mcnf":
        if mcnf_func is None:
            raise ValueError("MCNF_systemfunc is not provided in ctx")
        eloss, total_dem = mcnf_func(arcs, edges, arc_cap, demand_dict, max_dist_case, arc_distance, avg_velo)
                            
    elif sys_name == "shortest":
        eloss, total_dem = shortestpath_systemfunc(
            arcs, edges, arc_cap, demand_dict
        )
    else:
        raise ValueError(f"Unknown sys_name: {sys_name}")

    if eloss is None:
        return (None, None)

    pi_val = (total_dem - eloss) / total_dem if total_dem else 0.0
    return (pi_val, beta_val)


def generate_lhs_bitstrings(num_components, pop_size, min_fail=1, max_fail=10, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    bitstrings = []
    n_bucket = max_fail - min_fail + 1
    per_bucket = pop_size // n_bucket

    for fail_cnt in range(min_fail, max_fail + 1):
        for _ in range(per_bucket):
            sampler = qmc.LatinHypercube(d=1, seed=random.randint(0, 1_000_000))
            lhs = sampler.random(n=fail_cnt).flatten()
            idx = np.unique((lhs * num_components).astype(int))
            while len(idx) < fail_cnt:
                idx = np.unique(np.append(idx, random.randint(0, num_components - 1)))
            bits = [1] * num_components
            for i in idx:
                bits[i] = 0
            bitstrings.append(bits)

    while len(bitstrings) < pop_size:
        fail_cnt = random.randint(min_fail, max_fail)
        idx = random.sample(range(num_components), fail_cnt)
        bits = [1] * num_components
        for i in idx:
            bits[i] = 0
        bitstrings.append(bits)

    return bitstrings


def lhs_population(num_components, pop_size, individual_cls, min_fail=1, max_fail=10, seed=None):
    bitstrings = generate_lhs_bitstrings(num_components, pop_size, min_fail, max_fail, seed)
    return [individual_cls(bits) for bits in bitstrings]


def ind_to_dict(ind):
    pi, beta = map(float, ind.fitness.values)
    failed = [i + 1 for i, bit in enumerate(ind) if bit == 0]
    return {"pi": pi, "beta": beta, "failed": failed}


def run_ga(case_id, delay, sys_name, ctx,
           pop_size, ngen, cxpb, mutpb,
           processes, max_stag, seed,
           show_front_details=False):

    COMPONENT_IDS = ctx["COMPONENT_IDS"]
    NUM_COMPONENTS = len(COMPONENT_IDS)

    print(f"\n▶ CASE {case_id} | {sys_name.upper()} (delay={delay} min)")

    fit_tag, ind_tag = f"Fit_{case_id}_{sys_name}", f"Ind_{case_id}_{sys_name}"
    if not hasattr(deap_creator, fit_tag):
        deap_creator.create(fit_tag, deap_base.Fitness, weights=(-1.0, -1.0))
        deap_creator.create(ind_tag, list, fitness=getattr(deap_creator, fit_tag))

    toolbox = deap_base.Toolbox()
    toolbox.register("attr_bool", lambda: 1)
    toolbox.register("individual", tools.initRepeat, getattr(deap_creator, ind_tag),
                     toolbox.attr_bool, n=NUM_COMPONENTS)
    toolbox.register("population", list, toolbox.individual)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", tools.mutFlipBit, indpb=mutpb)
    toolbox.register("select", tools.selNSGA2)

    eval_func = partial(evaluate_individual, delay_time=delay, sys_name=sys_name, ctx=ctx)

    evaluated_cache = {}

    def ind_key(ind): 
        return tuple(ind)

    def eval_population(pop):
        todo, keys = [], []
        for ind in pop:
            k = ind_key(ind)
            if k in evaluated_cache:
                ind.fitness.values = evaluated_cache[k]
            else:
                todo.append(ind)
                keys.append(k)
        if todo:
            fits = toolbox.map(eval_func, todo)
            for ind, k, fit in zip(todo, keys, fits):
                ind.fitness.values = fit
                evaluated_cache[k] = fit

    pop = lhs_population(
        NUM_COMPONENTS, pop_size,
        individual_cls=getattr(deap_creator, ind_tag),
        seed=seed
    )
    hof = tools.ParetoFront()
    pop_history, pareto_history = [], []

    with mp.Pool(processes) as pool:
        toolbox.register("map", pool.map)

        eval_population(pop)
        hof.update(pop)
        pop_history.append(pop.copy())
        pareto_history.append([ind.fitness.values for ind in hof])

        stagnant, prev_front = 0, set()
        with tqdm(total=ngen, desc=f"GA Case{case_id}-{sys_name.upper()}", leave=False) as pbar:
            for gen in range(1, ngen + 1):
                fronts = sortNondominated(pop, k=len(pop), first_front_only=False)
                F1 = fronts[0]
                F2 = fronts[1] if len(fronts) > 1 else []
                lower = [ind for fr in fronts[2:] for ind in fr]

                if len(F2) >= 2:
                    mating_pool = F2[:]
                else:
                    fallback_pool = F1 + lower
                    if fallback_pool:
                        assignCrowdingDist(fallback_pool)
                        fallback_pool.sort(
                            key=lambda ind: ind.fitness.crowding_dist,
                            reverse=True,
                        )
                        need = max(2, min(len(fallback_pool), max(2, pop_size // 5)))
                        mating_pool = (F2 + fallback_pool[:need]) if F2 else fallback_pool[:need]
                    else:
                        mating_pool = F1[:]

                MIX_WITH_F1, MIX_RATE = True, 0.10
                if MIX_WITH_F1 and F1 and len(mating_pool) >= 2:
                    assignCrowdingDist(F1)
                    F1_sorted = sorted(F1, key=lambda ind: ind.fitness.crowding_dist,
                                       reverse=True)
                    mating_pool += F1_sorted[:max(1, int(MIX_RATE * len(mating_pool)))]

                if not mating_pool:
                    mating_pool = pop[:]

                parents = [toolbox.clone(random.choice(mating_pool)) for _ in range(pop_size)]
                offspring = algorithms.varAnd(parents, toolbox, cxpb=cxpb, mutpb=mutpb)

                eval_population(offspring)
                pop = toolbox.select(pop + offspring, k=pop_size)
                hof.update(pop)

                pop_history.append(pop.copy())
                pareto_history.append([ind.fitness.values for ind in hof])

                cur_front = {tuple(ind.fitness.values) for ind in hof}
                stagnant = stagnant + 1 if cur_front == prev_front else 0
                prev_front = cur_front

                pbar.update(1)
                if show_front_details:
                    pareto = sortNondominated(pop, len(pop), first_front_only=True)[0]
                    best = min(pareto, key=lambda ind: ind.fitness.values[1])
                    tqdm.write(
                        f"Gen {gen:>4} | Pareto={len(pareto):>3}  "
                        f"Best beta={best.fitness.values[1]:.4f}, "
                        f"pi={best.fitness.values[0]:.4f}"
                    )

                if stagnant >= max_stag:
                    pbar.write(f"Early stop: unchanged {max_stag} generations.")
                    break

    return {"hof": list(hof), "pops": pop_history, "paretos": pareto_history}


# plotting util

def c_of_pi(pi_arr: np.ndarray, mode: str = "one_minus_pi") -> np.ndarray:
    return 1.0 - pi_arr if mode == "one_minus_pi" else 1.0 - pi_arr


def get_final_points(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    final = data["generations"][-1]
    pts = [(float(p["pi"]), float(p["beta"])) for p in final.get("pareto", [])]
    if not pts:
        pts = [(float(ind["pi"]), float(ind["beta"])) for ind in final["population"]]
    pts.sort(key=lambda x: x[1])
    return pts


def fmt_pdm_label(pdm: float) -> str:
    k = int(np.floor(np.log10(pdm) + 1e-12))
    return rf"$S_{{L}}=10^{{{k}}}$"


def plot_resilience_threshold(ax, pdm, lambda_, c_mode,
                              pi_lo=0.0, pi_hi=0.9999,
                              label_x_range=(0.80, 0.825)):
    pi = np.linspace(pi_lo, pi_hi, 4000)
    c = c_of_pi(pi, mode=c_mode)
    x = np.divide(pdm, lambda_ * c, out=np.full_like(pi, np.nan), where=(c > 0))
    mask = (x > 0.0) & (x < 1.0)
    if not np.any(mask):
        return
    pi_m = pi[mask]
    beta = -norm.ppf(x[mask])
    ax.plot(pi_m, beta, linestyle="dotted", color="k", linewidth=1.8, zorder=2)

    x_lo, x_hi = label_x_range
    sel = (pi_m >= x_lo) & (pi_m <= x_hi)
    idx = np.where(sel)[0][0] if np.any(sel) else min(np.searchsorted(pi_m, x_lo), len(pi_m) - 1)
    xi, yi = pi_m[idx], beta[idx]
    ymin, ymax = ax.get_ylim()
    y_offset = 0.02 * (ymax - ymin)
    ax.text(
        xi, yi + y_offset,
        fmt_pdm_label(pdm),
        color="k", fontsize=11,
        ha="left", va="bottom",
        zorder=3, clip_on=True
    )

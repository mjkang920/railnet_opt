from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import pytest
import numpy as np

# ---------- module under test ----------
ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "02_critical_scenario_prioritization"
sys.path.append(str(MODULE_DIR))

from module import (
    shortestpath_systemfunc,
    MCNF_systemfunc,
    safe_pi,
)

TOY_DIR = ROOT / "01_data" / "toynet"
jload = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))


# ---------- helpers ----------

def load_nodes_edges_any(data_dir: str | Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load nodes.json and edges.json and normalize them to dict form.

    nodes.json:
      1) dict: { "n1": {...}, "n2": {...}, ... }
      2) list: [ {"id": "n1", ...}, {"id": "n2", ...}, ... ]

    edges.json:
      1) dict: { "e1": {"from": u, "to": v, ...}, ... }
      2) list: [ {"eid": "e1", "from": u, "to": v, ...}, ... ]
              or {"eid": "e1", "source": u, "target": v, ...}
    """
    data_dir = Path(data_dir)

    # nodes
    nodes_raw = jload(data_dir / "nodes.json")
    if isinstance(nodes_raw, dict):
        nodes = nodes_raw
    elif isinstance(nodes_raw, list):
        nodes = {n["id"]: {k: v for k, v in n.items() if k != "id"} for n in nodes_raw}
    else:
        raise TypeError("nodes.json must be dict or list")

    # edges
    edges_raw = jload(data_dir / "edges.json")
    edges: Dict[str, Dict[str, Any]] = {}

    if isinstance(edges_raw, dict):
        for eid, e in edges_raw.items():
            if "from" in e and "to" in e:
                edges[eid] = e
            elif "source" in e and "target" in e:
                edges[eid] = {
                    "from": e["source"],
                    "to": e["target"],
                    **{k: v for k, v in e.items() if k not in ("source", "target")},
                }
            else:
                raise KeyError(f"Edge {eid} missing 'from'/'to' or 'source'/'target'")
    elif isinstance(edges_raw, list):
        for e in edges_raw:
            eid = e.get("eid")
            if not eid:
                raise KeyError("Edge entry in list missing 'eid'")
            if "from" in e and "to" in e:
                edges[eid] = {k: v for k, v in e.items() if k != "eid"}
            elif "source" in e and "target" in e:
                edges[eid] = {
                    "from": e["source"],
                    "to": e["target"],
                    **{k: v for k, v in e.items()
                       if k not in ("eid", "source", "target")},
                }
            else:
                raise KeyError(f"Edge {eid} missing 'from'/'to' or 'source'/'target'")
    else:
        raise TypeError("edges.json must be dict or list")

    return nodes, edges


def load_toynet_dataset() -> Tuple[
    Dict[str, Any], Dict[str, Any], list,
    Dict[str, float], Dict[str, float],
    Dict[str, Any], Dict[str, float], float
]:
    """
    Load the toynet dataset and return
    nodes, edges, arcs, arc_distance, intact_capacity, demand, max_distance, avg_velo.
    """
    nodes, edges_full = load_nodes_edges_any(TOY_DIR)

    # edges_full: {eid: {"from": ..., "to": ..., ...}}
    edges = {eid: (v["from"], v["to"]) for eid, v in edges_full.items()}
    arcs = list(edges.values())

    arc_distance = {
        eid: float(v["arc_distance"])
        for eid, v in edges_full.items()
        if "arc_distance" in v
    }
    intact_capacity = {
        eid: float(v["intact_capacity"])
        for eid, v in edges_full.items()
        if "intact_capacity" in v
    }

    # demand_02.json to demand_dict and max_distance
    demand_raw = jload(TOY_DIR / "demand_02.json")
    demand_dict: Dict[str, Any] = {}
    max_distance: Dict[str, float] = {}

    avg_velo = 20.0     # km/h for tests
    delay_time = 180.0  # minutes
    buffer_dist = (avg_velo * delay_time / 60.0) * 1000.0

    for idx, item in enumerate(demand_raw, start=1):
        k = f"k{idx}"
        dist = float(item["distance"])
        demand_dict[k] = {
            "origin":      item["origin_name"],
            "destination": item["destination_name"],
            "amount":      float(item["journeys"]),
            "distance":    dist,
        }
        max_distance[k] = dist + buffer_dist

    return nodes, edges, arcs, arc_distance, intact_capacity, demand_dict, max_distance, avg_velo


def make_arc_capacity_with_failures(
    intact_capacity: Dict[str, float],
    edges: Dict[str, tuple],
    failed_edges: list[str],
) -> Dict[str, float]:
    """
    Create an arc_capacity dict where given edges (and their reverse ids) have zero capacity.
    """
    comps_st = {e: 1 for e in edges}

    for base_id in failed_edges:
        if base_id in comps_st:
            comps_st[base_id] = 0
        rev = base_id + "r"
        if rev in comps_st:
            comps_st[rev] = 0

    arc_capacity_scenario = {
        e: float(intact_capacity[e]) * comps_st[e]
        for e in edges
    }
    return arc_capacity_scenario


# ---------- tests ----------

@pytest.mark.parametrize(
    "failed_edges",
    [
        ["e2", "e3"],
    ],
)
def test_shortestpath_systemfunc1(failed_edges):
    """
    Check total_pd and expected_loss for a fixed failure scenario.
    """
    (
        nodes,
        edges,
        arcs,
        arc_distance,
        intact_capacity,
        demand,
        max_distance,
        avg_velo,
    ) = load_toynet_dataset()

    expected_eloss, expected_totalpd = 0.0, 16800.0

    arc_cap_fail = make_arc_capacity_with_failures(
        intact_capacity, edges, failed_edges
    )

    eloss, totalpd = shortestpath_systemfunc(
        arcs=[],
        edges=edges,
        arc_capacity=arc_cap_fail,
        demand=demand,
    )

    assert eloss == pytest.approx(expected_eloss), \
        f"Expected {expected_eloss}, got {eloss}"
    assert totalpd == pytest.approx(expected_totalpd), \
        f"Expected {expected_totalpd}, got {totalpd}"


@pytest.mark.parametrize(
    "failed_edges",
    [
        ["e2", "e3"],
    ],
)
def test_MCNF_systemfunc1(failed_edges):
    """
    Check MCNF loss and total_pd for a fixed failure scenario.
    """
    (
        nodes,
        edges,
        arcs,
        arc_distance,
        intact_capacity,
        demand,
        max_distance,
        avg_velo,
    ) = load_toynet_dataset()

    expected_eloss, expected_totalpd = 5002.6, 16800.0

    arc_cap_fail = make_arc_capacity_with_failures(
        intact_capacity, edges, failed_edges
    )

    eloss, totalpd = MCNF_systemfunc(
        arcs=arcs,
        edges=edges,
        arc_capacity=arc_cap_fail,
        demand=demand,
        max_distance=max_distance,
        arc_distance=arc_distance,
        avg_velo=avg_velo,
    )

    assert eloss == pytest.approx(expected_eloss), \
        f"Expected {expected_eloss}, got {eloss}"
    assert totalpd == pytest.approx(expected_totalpd), \
        f"Expected {expected_totalpd}, got {totalpd}"


def test_safe_pi1():
    total_dem, eloss = 100.0, 40.0
    expected = 0.6
    pi = safe_pi(total_dem, eloss)
    assert pi == pytest.approx(expected), \
        f"Expected pi {expected}, got {pi}"


def test_safe_pi2():
    total_dem, eloss = 100.0, 100.0
    expected = 0.0
    pi = safe_pi(total_dem, eloss)
    assert pi == pytest.approx(expected), \
        f"Expected pi {expected}, got {pi}"


def test_safe_pi3():
    total_dem, eloss = 100.0, 0.0
    expected = 1.0
    pi = safe_pi(total_dem, eloss)
    assert pi == pytest.approx(expected), \
        f"Expected pi {expected}, got {pi}"

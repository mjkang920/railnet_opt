from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR   = PROJECT_ROOT / "01_data"
KOR_DATA   = DATA_DIR / "korea"
UK_DATA    = DATA_DIR / "uk"

CRIT_DIR   = PROJECT_ROOT / "02_critical_scenario_prioritization"
CRIT_OUT   = CRIT_DIR / "outputs"

# network inputs
input_files_kor = {
    "nodes":           KOR_DATA / "nodes.json",
    "edges":           KOR_DATA / "edges.json",
    "arc_distance":    KOR_DATA / "arc_distance.json",
    "intact_capacity": KOR_DATA / "intact_capacity.json",
    "probs":           KOR_DATA / "probs.json",
    "demand":          KOR_DATA / "demand_02.json",
}

input_files_uk = {
    "nodes":           UK_DATA / "nodes.json",
    "edges":           UK_DATA / "edges.json",
    "arc_distance":    UK_DATA / "arc_distance.json",
    "intact_capacity": UK_DATA / "intact_capacity.json",
    "probs":           UK_DATA / "probs.json",
    "demand":          UK_DATA / "demand_02.json",
}

# ga inputs
ga_files_kor = {
    "delay30": CRIT_OUT / "kor" / "Genetic_Algorithm" / "GA_delay30_mcnf.json",
    "delay60": CRIT_OUT / "kor" / "Genetic_Algorithm" / "GA_delay60_mcnf.json",
    "delay120": CRIT_OUT / "kor" / "Genetic_Algorithm" / "GA_delay120_mcnf.json",
}

ga_files_uk = {
    "delay30": CRIT_OUT / "uk" / "Genetic_Algorithm" / "GA_delay30_mcnf.json",
    "delay60": CRIT_OUT / "uk" / "Genetic_Algorithm" / "GA_delay60_mcnf.json",
    "delay120": CRIT_OUT / "uk" / "Genetic_Algorithm" / "GA_delay120_mcnf.json",
}

def get_ga_files(region: str = "kor", labels=("delay30", "delay60", "delay120")):
    region = region.lower()
    src = ga_files_kor if region == "kor" else ga_files_uk
    return [(lab, src[lab]) for lab in labels]

# basemap
basemap_files_kor = {
    "basemap_nodes": KOR_DATA / "basemap_nodes.json",
    "basemap_edges": KOR_DATA / "basemap_edges.json",
}

basemap_files_uk = {
    "basemap_nodes": UK_DATA / "basemap_nodes.json",
    "basemap_edges": UK_DATA / "basemap_edges.json",
}

def get_basemap_files(region: str = "kor"):
    region = region.lower()
    if region == "kor":
        return basemap_files_kor
    if region == "uk":
        return basemap_files_uk
    raise ValueError("region must be 'kor' or 'uk'")

from pathlib import Path

HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]   

DATA_DIR   = PROJECT_ROOT / "01_data"
KOR_DATA   = DATA_DIR / "korea"
UK_DATA    = DATA_DIR / "uk"

input_files_kor = {
    "edges":  KOR_DATA / "edges.json",
    "route":  KOR_DATA / "routes_nodes.json",
    "dept":   KOR_DATA / "dep_time.json",
    "demand": KOR_DATA / "demand_03.json",
    "nodes":  KOR_DATA / "nodes.json",     
}

input_files_uk = {
    "edges":  UK_DATA / "edges.json",
    "route":  UK_DATA / "routes_nodes.json",
    "dept":   UK_DATA / "dep_time.json",
    "demand": UK_DATA / "demand_03.json",
    "nodes":  UK_DATA / "nodes.json",     
}


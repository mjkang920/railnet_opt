from pathlib import Path

HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]

DATA_DIR = PROJECT_ROOT / "01_data"
TOYNET_DATA = DATA_DIR / "toynet"
KOR_DATA = DATA_DIR / "korea"
UK_DATA = DATA_DIR / "uk"

input_files_toynet = {
    "edges":  TOYNET_DATA / "edges.json",
    "route":  TOYNET_DATA / "routes_nodes.json",
    "dept":   TOYNET_DATA / "dep_time.json",
    "demand": TOYNET_DATA / "demand_03.json",
    "nodes":  TOYNET_DATA / "nodes.json",
    "cap_node": TOYNET_DATA / "nodes_capacity.json",
}

input_files_kor = {
    "edges":  KOR_DATA / "edges.json",
    "route":  KOR_DATA / "routes_nodes.json",
    "dept":   KOR_DATA / "dep_time.json",
    "demand": KOR_DATA / "demand_03.json",
    "nodes":  KOR_DATA / "nodes.json",
    "cap_node": KOR_DATA / "nodes_capacity.json",
}

input_files_uk = {
    "edges":  UK_DATA / "edges.json",
    "route":  UK_DATA / "routes_nodes.json",
    "dept":   UK_DATA / "dep_time.json",
    "demand": UK_DATA / "demand_03.json",
    "nodes":  UK_DATA / "nodes.json",
    "cap_node": UK_DATA / "nodes_capacity.json",
}

VALID_DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")

input_files_uk_real = {
    "edges":      UK_DATA / "edges.json",
    "nodes":      UK_DATA / "nodes.json",
    "route_dir":  UK_DATA / "routes_nodes",
    "dept_dir":   UK_DATA / "dep_time",
    "demand_dir": UK_DATA / "demand_03",
    "cap_node_dir": UK_DATA / "nodes_capacity",
}


def get_input_files(region: str, day: str | None = None) -> dict:
    
    region_norm = str(region).lower()

    if region_norm == "toynet":
        return input_files_toynet

    if region_norm in ("kor", "korea"):
        return input_files_kor

    if region_norm == "uk":
        return input_files_uk

    if region_norm == "uk_real":
        if day is None:
            raise ValueError(
                "The 'day' argument is required when region='uk_real'. "
                "Example: get_input_files('uk_real', 'MON')"
            )

        day_code = str(day).upper()
        if day_code not in VALID_DAYS:
            raise ValueError(
                f"Invalid day value: {day!r}. "
                f"Available values: {', '.join(VALID_DAYS)}"
            )

        return {
            "edges":  input_files_uk_real["edges"],
            "nodes":  input_files_uk_real["nodes"],
            "route":  input_files_uk_real["route_dir"]  / f"{day_code}.json",
            "dept":   input_files_uk_real["dept_dir"]   / f"{day_code}.json",
            "demand": input_files_uk_real["demand_dir"] / f"{day_code}.json",
            "cap_node": input_files_uk_real["cap_node_dir"] / f"{day_code}.json",
        }

    raise ValueError(
        f"Unknown region: {region!r}. "
        "Available values: 'toynet', 'kor', 'korea', 'uk', 'uk_real'"
    )
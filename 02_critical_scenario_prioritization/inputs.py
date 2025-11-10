# network inputs
input_files_kor = {
    "nodes": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\nodes.json",
    "edges": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\edges.json",
    "arc_distance": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\arc_distance.json",
    "intact_capacity": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\intact_capacity.json",
    "probs": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\probs.json",
    "demand": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\korea\demand_02.json",
}

input_files_uk = {
    "nodes": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\nodes.json",
    "edges": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\edges.json",
    "arc_distance": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\arc_distance.json",
    "intact_capacity": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\intact_capacity.json",
    "probs": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\probs.json",
    "demand": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\01_data\uk\demand_02.json",
}


# ga inputs
from pathlib import Path

ROOT = Path(r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs")

ga_files_kor = {
    "delay30": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\kor\Genetic_Algorithm\GA_delay30_mcnf.json",
    "delay60": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\kor\Genetic_Algorithm\GA_delay60_mcnf.json",
    "delay120": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\kor\Genetic_Algorithm\GA_delay120_mcnf.json",
}

ga_files_uk = {
    "delay30": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\uk\Genetic_Algorithm\GA_delay30_mcnf.json",
    "delay60": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\uk\Genetic_Algorithm\GA_delay60_mcnf.json",
    "delay120": r"C:\Users\Minji Kang\Documents\GitHub\railnet_opt\02_critical_scenario_prioritization\outputs\uk\Genetic_Algorithm\GA_delay120_mcnf.json",
}

def get_ga_files(region: str = "kor", labels=("delay30", "delay60", "delay120")):
    src = ga_files_kor if region.lower() == "kor" else ga_files_uk
    return [(lab, Path(src[lab])) for lab in labels]
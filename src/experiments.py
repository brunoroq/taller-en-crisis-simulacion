import csv
import json
import platform
from collections import defaultdict
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from statistics import mean, stdev

from numpy.random import SeedSequence
from scipy.stats import t

from .config import BASE, COMBINED, IMPROVEMENTS, LOAD, STATIONS, Scenario, Workshop
from .metrics import summarize_day
from .model import simulate_day


def replica_seeds(master_seed: int, replicas: int) -> list[int]:
    return [int(child.generate_state(1, dtype="uint64")[0]) for child in SeedSequence(master_seed).spawn(replicas)]


def simulate_scenarios(base: Workshop, scenarios: tuple[Scenario, ...], seeds: list[int]) -> tuple[list, list]:
    days, stations = [], []
    for scenario in scenarios:
        workshop = scenario.configure(base)
        for replica, seed in enumerate(seeds, start=1):
            daily, by_station = summarize_day(simulate_day(workshop, seed), workshop, scenario)
            identity = {"escenario": scenario.code, "factor": scenario.factor, "replica": replica, "semilla": seed}
            days.append({**identity, **daily})
            stations.extend({**identity, "estacion": name, **values} for name, values in by_station.items())
    return days, stations


def confidence_summary(values: list) -> dict:
    observed = [value for value in values if value is not None]
    n = len(observed)
    if n < 2:
        return {"n": n, "media": observed[0] if n else None, "de": None, "ic95_inf": None, "ic95_sup": None}
    average, deviation = mean(observed), stdev(observed)
    half_width = float(t.ppf(0.975, n - 1)) * deviation / n**0.5
    return {"n": n, "media": average, "de": deviation, "ic95_inf": average - half_width, "ic95_sup": average + half_width}


def aggregate(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)

    summaries = []
    for key, group in groups.items():
        identity = dict(zip(keys, key, strict=True))
        for metric in group[0].keys() - {*keys, "replica", "semilla"}:
            summaries.append({**identity, "indicador": metric, **confidence_summary([row[metric] for row in group])})
    return sorted(summaries, key=lambda row: (*(row[key] for key in keys), row["indicador"]))


def paired_changes(rows: list[dict]) -> list[dict]:
    base = {row["semilla"]: row for row in rows if row["escenario"] == "E0"}
    improvements = {scenario.code for scenario in (*IMPROVEMENTS, COMBINED)}
    deltas = []
    for row in rows:
        if row["escenario"] in improvements:
            reference = base[row["semilla"]]
            deltas.append({
                "escenario": row["escenario"], "factor": row["factor"],
                **{
                    metric: value - reference[metric] if value is not None and reference[metric] is not None else None
                    for metric, value in row.items() if metric not in {"escenario", "factor", "replica", "semilla"}
                },
            })
    return aggregate(deltas, ("escenario", "factor"))


def nominal_capacity(base: Workshop) -> list[dict]:
    repairs = sum(kind.share * mean(kind.repair) for kind in base.classes)
    visits = (1, 1, 1 / (1 - base.rework_probability), 1 / (1 - base.rework_probability))
    service = (mean(base.reception), mean(base.diagnosis), repairs, mean(base.quality))
    return [
        {
            "estacion": station,
            "servidores": count,
            "servicio_medio_por_visita_min": minutes,
            "visitas_esperadas_por_vehiculo": frequency,
            "capacidad_nominal_vehiculos_h": 60 * count / (minutes * frequency),
            "factor_equilibrio_trabajo": base.close_min * count / (base.expected_demand * minutes * frequency)
            if base.expected_demand else None,
        }
        for station, count, minutes, frequency in zip(STATIONS, base.servers, service, visits, strict=True)
    ]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_experiments(base: Workshop, replicas: int, master_seed: int, output: Path) -> tuple[list, list]:
    scenarios = (BASE, *LOAD, *IMPROVEMENTS, COMBINED)
    seeds = replica_seeds(master_seed, replicas)
    days, stations = simulate_scenarios(base, scenarios, seeds)
    daily_summary = aggregate(days, ("escenario", "factor"))
    station_summary = aggregate(stations, ("escenario", "factor", "estacion"))
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in (
        ("replicas", days), ("replicas_estaciones", stations), ("resumen", daily_summary),
        ("resumen_estaciones", station_summary), ("diferencias_pareadas_vs_E0", paired_changes(days)),
        ("capacidad_nominal", nominal_capacity(base)),
    ):
        write_csv(output / f"{name}.csv", rows)

    manifest = {
        "replicas_por_escenario": replicas,
        "semilla_maestra": master_seed,
        "python": platform.python_version(),
        "dependencias": {name: version(name) for name in ("ciw", "numpy", "scipy", "matplotlib")},
        "economia": "supuestos ilustrativos pendientes de validación" if base.economics else "desactivada",
        "configuracion_base": asdict(base),
        "escenarios": [asdict(scenario) for scenario in scenarios],
    }
    (output / "configuracion_ejecutada.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return daily_summary, station_summary

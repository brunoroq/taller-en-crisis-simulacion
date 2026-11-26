from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import mean

import numpy as np
from ciw.data_record import DataRecord

from .config import STATIONS, Scenario, Workshop
from .model import Day


@dataclass(frozen=True)
class Vehicle:
    kind: str
    arrival: float
    departure: float
    wait: float
    service: float
    reworks: int


def group_vehicles(visits: tuple[DataRecord, ...]) -> tuple[Vehicle, ...]:
    paths = defaultdict(list)
    for visit in visits:
        paths[visit.id_number].append(visit)

    vehicles = []
    for path in paths.values():
        first = min(path, key=lambda visit: visit.arrival_date)
        last = max(path, key=lambda visit: visit.exit_date)
        vehicles.append(Vehicle(
            kind=first.original_customer_class,
            arrival=first.arrival_date,
            departure=last.exit_date,
            wait=sum(visit.waiting_time for visit in path),
            service=sum(visit.service_time for visit in path),
            reworks=sum(visit.node == 4 and visit.destination == 3 for visit in path),
        ))
    return tuple(vehicles)


def overlap(start: float, end: float, left: float, right: float) -> float:
    return max(0.0, min(end, right) - max(start, left))


def days_mean(values) -> float | None:
    values = list(values)
    return mean(values) if values else None


def hourly(count: int, minutes: float) -> float | None:
    return count * 60 / minutes if minutes > 0 else None


def station_metrics(visits: list[DataRecord], servers: int, close: float, end: float) -> dict:
    completed = [visit for visit in visits if visit.exit_date <= close]
    data = {
        "servidores": servers,
        "visitas_cohorte": len(visits),
        "w_visita_cohorte_min": days_mean(visit.exit_date - visit.arrival_date for visit in visits),
        "wq_visita_cohorte_min": days_mean(visit.waiting_time for visit in visits),
        "mu_visita_cohorte_por_servidor_h": hourly(len(visits), sum(v.service_time for v in visits)),
        "w_visita_terminada_jornada_min": days_mean(v.exit_date - v.arrival_date for v in completed),
        "wq_visita_terminada_jornada_min": days_mean(v.waiting_time for v in completed),
        "mu_visita_terminada_jornada_por_servidor_h": hourly(
            len(completed), sum(v.service_time for v in completed)
        ),
        "pendientes_cierre": sum(v.arrival_date <= close < v.exit_date for v in visits),
    }
    windows = (
        ("jornada", 0, close, sum(0 <= v.arrival_date <= close for v in visits), len(completed)),
        ("vaciado", close, end, sum(close < v.arrival_date for v in visits), len(visits) - len(completed)),
    )
    for label, left, right, arrivals, departures in windows:
        duration = right - left
        present = sum(overlap(v.arrival_date, v.exit_date, left, right) for v in visits)
        waiting = sum(overlap(v.arrival_date, v.service_start_date, left, right) for v in visits)
        busy = sum(overlap(v.service_start_date, v.service_end_date, left, right) for v in visits)
        data.update({
            f"entradas_{label}": arrivals,
            f"salidas_{label}": departures,
            f"lambda_visitas_{label}_h": hourly(arrivals, duration),
            f"throughput_visitas_{label}_h": hourly(departures, duration),
            f"l_{label}": present / duration if duration else None,
            f"lq_{label}": waiting / duration if duration else None,
            f"utilizacion_{label}": busy / (servers * duration) if duration else None,
            f"minutos_persona_{label}": busy,
        })
    return data


def economic_metrics(
    workshop: Workshop, scenario: Scenario, vehicles: tuple[Vehicle, ...], stations: dict[str, dict]
) -> dict:
    costs = workshop.economics
    if costs is None:
        return {}

    prices = {kind.name: kind for kind in workshop.classes}
    revenue = sum(prices[v.kind].price_clp for v in vehicles)
    variable = sum(
        prices[v.kind].variable_cost_clp * (1 + costs.rework_material_fraction * v.reworks)
        for v in vehicles
    )
    staff = sum(count * wage for count, wage in zip(workshop.servers, costs.daily_wages_clp, strict=True))
    intervention = (
        costs.better_qc_cost_clp * scenario.better_qc + costs.scheduling_cost_clp * scenario.uniform_arrivals
    )
    overtime = sum(
        station["minutos_persona_vaciado"] * rate / 60
        for station, rate in zip(stations.values(), costs.overtime_rates_clp_h, strict=True)
    )
    return {
        "ingresos_clp": revenue,
        "costos_variables_clp": variable,
        "costos_personal_clp": staff,
        "costos_operacionales_clp": costs.operating_cost_clp,
        "costos_mejoras_clp": intervention,
        "costos_extra_clp": overtime,
        "margen_operacional_clp": revenue - variable - staff - costs.operating_cost_clp - intervention - overtime,
    }


def summarize_day(day: Day, workshop: Workshop, scenario: Scenario) -> tuple[dict, dict[str, dict]]:
    close = workshop.close_min
    end = max(close, day.end_min)
    visits_by_node = defaultdict(list)
    for visit in day.visits:
        visits_by_node[visit.node].append(visit)
    stations = {
        station: station_metrics(visits_by_node[node], servers, close, end)
        for node, (station, servers) in enumerate(zip(STATIONS, workshop.servers, strict=True), start=1)
    }

    vehicles = group_vehicles(day.visits)
    received = len(day.arrivals)
    completed = [vehicle for vehicle in vehicles if vehicle.departure <= close]
    pending = received - len(completed)
    cohort_times = [v.departure - v.arrival for v in vehicles]
    reworks = [v for v in day.visits if v.node == 4 and v.destination == 3]
    classes = Counter(kind for _, kind in day.arrivals)
    metrics = {
        "recibidos": received,
        "terminados_jornada": len(completed),
        "terminados_vaciado": len(vehicles) - len(completed),
        "pendientes_cierre": pending,
        "fraccion_pendiente_cierre": pending / received if received else None,
        "dia_sin_pendientes": int(pending == 0),
        "retrabajos": len(reworks),
        "retrabajos_jornada": sum(v.exit_date <= close for v in reworks),
        "retrabajos_vaciado": sum(v.exit_date > close for v in reworks),
        "extra_min": end - close,
        "lambda_jornada_h": hourly(received, close),
        "lambda_vaciado_h": hourly(0, end - close),
        "throughput_jornada_h": hourly(len(completed), close),
        "throughput_vaciado_h": hourly(len(vehicles) - len(completed), end - close),
        "throughput_cohorte_h": hourly(len(vehicles), end),
        "w_vehiculo_cohorte_min": days_mean(cohort_times),
        "wq_vehiculo_cohorte_min": days_mean(v.wait for v in vehicles),
        "p95_w_vehiculo_cohorte_min": float(np.percentile(cohort_times, 95)) if cohort_times else None,
        "w_vehiculo_terminado_jornada_min": days_mean(v.departure - v.arrival for v in completed),
        "wq_vehiculo_terminado_jornada_min": days_mean(v.wait for v in completed),
        "mu_equivalente_cohorte_por_h_persona": hourly(len(vehicles), sum(v.service for v in vehicles)),
        **{f"recibidos_{kind.name}": classes[kind.name] for kind in workshop.classes},
    }
    for label, duration in (("jornada", close), ("vaciado", end - close)):
        for measure in ("l", "lq"):
            metrics[f"{measure}_{label}"] = sum(station[f"{measure}_{label}"] for station in stations.values()) if duration else None
        busy = sum(station[f"minutos_persona_{label}"] for station in stations.values())
        metrics[f"utilizacion_{label}"] = busy / (sum(workshop.servers) * duration) if duration else None
    metrics.update(economic_metrics(workshop, scenario, vehicles, stations))
    return metrics, stations

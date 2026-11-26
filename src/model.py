from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import pairwise
from math import inf
from random import Random

import ciw
from ciw.data_record import DataRecord
from numpy.random import SeedSequence

from .config import Workshop


@dataclass(frozen=True)
class Day:
    arrivals: tuple[tuple[float, str], ...]
    visits: tuple[DataRecord, ...]
    end_min: float


class ScheduledArrivals(ciw.dists.Distribution):
    """Entrega los intervalos planificados y deja la próxima llegada en infinito."""

    def __init__(self, gaps: list[float]):
        self.gaps = deque(gaps)

    def sample(self, t=None, ind=None) -> float:
        return self.gaps.popleft() if self.gaps else inf


def generate_arrivals(workshop: Workshop, clock: Random, marks: Random) -> tuple[tuple[float, str], ...]:
    """Invierte la intensidad acumulada de un Poisson homogéneo de tasa uno."""
    names = [kind.name for kind in workshop.classes]
    shares = [kind.share for kind in workshop.classes]
    point = clock.expovariate(1)
    elapsed = 0.0
    intensity = 0.0
    arrivals = []
    for band in workshop.arrival_bands:
        rate = band.arrivals_per_hour / 60
        limit = intensity + rate * band.duration_min
        while point < limit:
            minute = elapsed + (point - intensity) / rate
            arrivals.append((minute, marks.choices(names, weights=shares)[0]))
            point += clock.expovariate(1)
        intensity = limit
        elapsed += band.duration_min
    return tuple(arrivals)


def simulate_day(workshop: Workshop, seed: int) -> Day:
    clock_seed, class_seed, ciw_seed = map(int, SeedSequence(seed).generate_state(3, dtype="uint64"))
    arrivals = generate_arrivals(workshop, Random(clock_seed), Random(class_seed))
    if not arrivals:
        return Day(arrivals, (), 0.0)

    times_by_class = defaultdict(list)
    for minute, kind in arrivals:
        times_by_class[kind].append(minute)

    arrivals_by_class = {}
    services_by_class = {}
    for kind in workshop.classes:
        gaps = [end - start for start, end in pairwise([0.0, *times_by_class[kind.name]])]
        arrivals_by_class[kind.name] = [
            ScheduledArrivals(gaps),
            None,
            None,
            None,
        ]
        services_by_class[kind.name] = [
            ciw.dists.Triangular(*limits)
            for limits in (workshop.reception, workshop.diagnosis, kind.repair, workshop.quality)
        ]

    ciw.seed(ciw_seed)
    network = ciw.create_network(
        arrival_distributions=arrivals_by_class,
        service_distributions=services_by_class,
        number_of_servers=list(workshop.servers),
        service_disciplines=[ciw.disciplines.FIFO] * 4,
        routing={
            kind.name: ciw.routing.TransitionMatrix(transition_matrix=[
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [0.0, 0.0, float(workshop.rework_probability), 0.0],
            ])
            for kind in workshop.classes
        },
    )
    simulation = ciw.Simulation(network)
    simulation.simulate_until_max_customers(len(arrivals), method="Complete")
    return Day(arrivals, tuple(simulation.get_all_records()), simulation.current_time)

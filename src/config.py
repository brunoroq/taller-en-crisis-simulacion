from dataclasses import dataclass, replace
from math import isclose


@dataclass(frozen=True)
class VehicleClass:
    name: str
    share: float
    repair: tuple[float, float, float]
    price_clp: int
    variable_cost_clp: int


@dataclass(frozen=True)
class Band:
    duration_min: float
    arrivals_per_hour: float


@dataclass(frozen=True)
class Economics:
    # Valores ilustrativos, pendientes de validación.
    daily_wages_clp: tuple[int, ...] = (30_000, 43_000, 48_000, 38_000)
    overtime_rates_clp_h: tuple[int, ...] = (6_000, 8_000, 9_000, 7_000)
    operating_cost_clp: int = 70_000
    rework_material_fraction: float = 0.35
    better_qc_cost_clp: int = 5_000
    scheduling_cost_clp: int = 3_000


@dataclass(frozen=True)
class Workshop:
    classes: tuple[VehicleClass, ...] = (
        VehicleClass("neumaticos", 0.35, (15, 30, 45), 50_000, 18_000),
        VehicleClass("electrico", 0.30, (30, 60, 90), 100_000, 32_000),
        VehicleClass("mecanica_general", 0.35, (60, 90, 150), 170_000, 65_000),
    )
    arrival_bands: tuple[Band, ...] = (Band(120, 3), Band(240, 1.5), Band(120, 2))
    reception: tuple[float, float, float] = (3, 5, 7)
    diagnosis: tuple[float, float, float] = (10, 15, 20)
    quality: tuple[float, float, float] = (5, 10, 15)
    servers: tuple[int, ...] = (1, 1, 3, 1)
    rework_probability: float = 0.05
    economics: Economics | None = Economics()

    @property
    def close_min(self) -> float:
        return sum(band.duration_min for band in self.arrival_bands)

    @property
    def expected_demand(self) -> float:
        return sum(band.duration_min * band.arrivals_per_hour / 60 for band in self.arrival_bands)

    def __post_init__(self) -> None:
        if not self.arrival_bands or any(
            band.duration_min <= 0 or band.arrivals_per_hour < 0 for band in self.arrival_bands
        ):
            raise ValueError("Cada período requiere duración positiva y tasa no negativa.")
        if not 0 <= self.rework_probability < 1:
            raise ValueError("La probabilidad de retrabajo debe estar en [0, 1).")
        if len(self.servers) != 4 or any(count < 1 for count in self.servers):
            raise ValueError("Se requieren cuatro estaciones con servidores positivos.")
        if (
            not self.classes
            or len({kind.name for kind in self.classes}) != len(self.classes)
            or any(kind.share < 0 for kind in self.classes)
            or not isclose(sum(kind.share for kind in self.classes), 1)
        ):
            raise ValueError("Las clases deben ser únicas y sus proporciones sumar uno.")


@dataclass(frozen=True)
class Scenario:
    code: str
    label: str
    factor: float = 1.0
    extra_mechanic: bool = False
    better_qc: bool = False
    uniform_arrivals: bool = False

    def configure(self, base: Workshop) -> Workshop:
        bands = base.arrival_bands
        if self.uniform_arrivals:
            bands = (Band(base.close_min, 60 * base.expected_demand / base.close_min),)
        bands = tuple(replace(band, arrivals_per_hour=band.arrivals_per_hour * self.factor) for band in bands)
        reception, diagnosis, mechanics, quality = base.servers
        return replace(
            base,
            arrival_bands=bands,
            servers=(reception, diagnosis, mechanics + int(self.extra_mechanic), quality),
            rework_probability=IMPROVED_REWORK_PROBABILITY if self.better_qc else base.rework_probability,
        )


STATIONS = ("recepcion", "diagnostico", "reparacion", "calidad")
STATION_LABELS = ("Recepción", "Diagnóstico", "Reparación", "Control de calidad")
IMPROVED_REWORK_PROBABILITY = 0.02
LOAD_FACTORS = (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
REPLICATES = 100
MASTER_SEED = 80912026

BASE = Scenario("E0", "Base")
LOAD = tuple(Scenario("E1", "Carga", factor) for factor in LOAD_FACTORS)
IMPROVEMENTS = (
    Scenario("E2", "Cuarto mecánico", extra_mechanic=True),
    Scenario("E3", "Menos retrabajo", better_qc=True),
    Scenario("E4", "Llegadas uniformes", uniform_arrivals=True),
)
# Configuración fijada tras el análisis de E0 y E2–E4 documentado en docs/resultados.md.
COMBINED = Scenario("E5", "Mecánico + calidad", extra_mechanic=True, better_qc=True)

import argparse
from dataclasses import replace
from pathlib import Path

from src.config import MASTER_SEED, REPLICATES, Workshop
from src.experiments import run_experiments


def main() -> None:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Simula jornadas de Taller en Crisis con Ciw.")
    parser.add_argument("--replicas", type=int, default=REPLICATES, help="réplicas por escenario, mínimo 50")
    parser.add_argument("--semilla", type=int, default=MASTER_SEED, help="semilla maestra para todos los escenarios")
    parser.add_argument("--sin-economia", action="store_true", help="omite los supuestos económicos ilustrativos")
    parser.add_argument("--salida", type=Path, default=root, help="directorio que contendrá results/ y figures/")
    args = parser.parse_args()
    if args.replicas < 50 or args.semilla < 0:
        parser.error("se requieren al menos 50 réplicas y una semilla no negativa")

    from src.plots import generate_figures

    base = replace(Workshop(), economics=None) if args.sin_economia else Workshop()
    days, stations = run_experiments(base, args.replicas, args.semilla, args.salida / "results")
    generate_figures(days, stations, args.salida / "figures")
    print(f"Simulación completada con {args.replicas} réplicas por escenario en {args.salida.resolve()}")


if __name__ == "__main__":
    main()

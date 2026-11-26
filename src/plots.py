from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, PercentFormatter

from .config import BASE, COMBINED, IMPROVEMENTS, LOAD_FACTORS, STATION_LABELS, STATIONS


BLUE = "#155e75"
ORANGE = "#af551a"
GRAY = "#566373"
PALETTE = (GRAY, BLUE, "#267b62", ORANGE, "#534f91")


def decimal_es(value: float, places: int) -> str:
    return f"{value:.{places}f}".replace(".", ",")


def save(figure, path: Path) -> None:
    figure.savefig(path, dpi=170, facecolor="white")
    plt.close(figure)


def values(rows: list[dict], scale: float = 1) -> tuple[np.ndarray, np.ndarray]:
    averages = np.asarray([row["media"] for row in rows], dtype=float) / scale
    high = np.asarray([row["ic95_sup"] for row in rows], dtype=float) / scale
    return averages, high - averages


def bars(axis, labels, rows, colors, ylabel: str, scale: float = 1) -> None:
    averages, errors = values(rows, scale)
    axis.bar(labels, averages, color=colors, yerr=errors, capsize=4, error_kw={"ecolor": "#1b2938"}, zorder=3)
    axis.set_ylabel(ylabel)
    axis.axhline(0, color="#7a8894", linewidth=0.8)


def curve(axis, rows, color: str, label: str | None = None) -> None:
    averages, errors = values(rows)
    axis.errorbar(LOAD_FACTORS, averages, yerr=errors, color=color, marker="o", capsize=4, label=label, zorder=3)


def load_axis(axis, ylabel: str) -> None:
    axis.set_xticks(LOAD_FACTORS, [f"{str(factor).rstrip('0').rstrip('.').replace('.', ',')}×" for factor in LOAD_FACTORS])
    axis.set_xlabel("Demanda respecto al escenario base")
    axis.set_ylabel(ylabel)


def generate_figures(days: list[dict], stations: list[dict], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    economic_file = output / "07_comparacion_economica.png"
    daily = {(r["escenario"], r["factor"], r["indicador"]): r for r in days}
    by_station = {(r["escenario"], r["factor"], r["estacion"], r["indicador"]): r for r in stations}
    improvements = (BASE, *IMPROVEMENTS, COMBINED)
    codes = [scenario.code for scenario in improvements]
    improvements_legend = "  ·  ".join(f"{s.code} {s.label.lower()}" for s in improvements)

    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 10, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "axes.axisbelow": True, "axes.grid.axis": "y", "grid.color": "#dfe7ec",
        "axes.formatter.use_locale": False, "figure.constrained_layout.use": True,
    }):
        labels = (*STATION_LABELS[:3], "Control\nde calidad")
        for name, metric, title, ylabel in (
            ("01_espera_estaciones", "wq_visita_cohorte_min", "Espera media por estación · E0", "Minutos por visita"),
            ("02_utilizacion_estaciones", "utilizacion_jornada", "Utilización durante la jornada · E0", "Tiempo disponible ocupado"),
        ):
            figure, axis = plt.subplots(figsize=(8.4, 4.6))
            rows = [by_station["E0", 1, station, metric] for station in STATIONS]
            bars(axis, labels, rows, (GRAY, GRAY, BLUE, GRAY), ylabel)
            axis.set_title(f"{title}\nMedia diaria e IC 95 %", loc="left")
            if metric == "utilizacion_jornada":
                axis.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
                axis.set_ylim(0, 1)
            save(figure, output / f"{name}.png")

        figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        figure.suptitle("Respuesta y ocupación de reparación frente a la carga · E1\nMedias diarias e IC 95 %")
        for metric, color, label in (
            ("w_vehiculo_cohorte_min", BLUE, "Promedio"),
            ("p95_w_vehiculo_cohorte_min", ORANGE, "Percentil 95 diario"),
        ):
            curve(axes[0], [daily["E1", factor, metric] for factor in LOAD_FACTORS], color, label)
        load_axis(axes[0], "Permanencia de la cohorte (minutos)")
        axes[0].legend(frameon=False)
        curve(axes[1], [by_station["E1", f, "reparacion", "utilizacion_jornada"] for f in LOAD_FACTORS], BLUE)
        load_axis(axes[1], "Utilización de reparación en jornada")
        axes[1].yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
        axes[1].set_ylim(0, 1)
        save(figure, output / "03_respuesta_carga.png")

        figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        figure.suptitle("Pendientes y tiempo extra frente a la carga · E1\nMedias diarias e IC 95 %")
        for axis, metric, label in zip(axes, ("pendientes_cierre", "extra_min"), ("Pendientes al cierre (vehículos)", "Tiempo para vaciar (minutos)"), strict=True):
            curve(axis, [daily["E1", factor, metric] for factor in LOAD_FACTORS], BLUE)
            load_axis(axis, label)
        save(figure, output / "04_pendientes_carga.png")

        figure, axis = plt.subplots(figsize=(8.4, 4.6))
        for metric, color, label in (
            ("lambda_jornada_h", GRAY, "Vehículos recibidos"),
            ("throughput_jornada_h", BLUE, "Vehículos entregados"),
        ):
            curve(axis, [daily["E1", factor, metric] for factor in LOAD_FACTORS], color, label)
        load_axis(axis, "Vehículos por hora de jornada")
        axis.set_title("Llegadas y throughput frente a la carga · E1\nMedias diarias e IC 95 %", loc="left")
        axis.legend(frameon=False)
        save(figure, output / "05_throughput_carga.png")

        figure, axes = plt.subplots(2, 2, figsize=(10, 7))
        figure.suptitle("Comparación de mejoras · Medias diarias e IC 95 %")
        for axis, metric, title, unit in (
            (axes[0, 0], "w_vehiculo_cohorte_min", "Permanencia de la cohorte", "Minutos por vehículo"),
            (axes[0, 1], "retrabajos", "Retrabajos de la cohorte", "Visitas por día"),
            (axes[1, 0], "pendientes_cierre", "Pendientes al cierre", "Vehículos por día"),
            (axes[1, 1], "extra_min", "Tiempo extra para vaciar", "Minutos por día"),
        ):
            bars(axis, codes, [daily[code, 1, metric] for code in codes], PALETTE, unit)
            axis.set_title(title, loc="left")
        figure.supxlabel(improvements_legend, fontsize=9)
        save(figure, output / "06_escenarios_mejora.png")

        if ("E0", 1, "margen_operacional_clp") in daily:
            figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
            figure.suptitle("Comparación económica ilustrativa · Medias diarias e IC 95 %")
            for axis, metric, title in (
                (axes[0], "margen_operacional_clp", "Margen operacional"),
                (axes[1], "costos_extra_clp", "Costo de horas extraordinarias activas"),
            ):
                bars(axis, codes, [daily[code, 1, metric] for code in codes], PALETTE, "Miles de CLP por día", scale=1000)
                axis.set_title(title, loc="left")
                axis.yaxis.set_major_formatter(FuncFormatter(lambda number, _: decimal_es(number, 0)))
            figure.supxlabel(improvements_legend + "\nPrecios y costos supuestos, pendientes de validación", fontsize=9)
            save(figure, economic_file)
        else:
            economic_file.unlink(missing_ok=True)

import unittest
from collections import Counter, defaultdict
from dataclasses import replace
from random import Random
from unittest.mock import Mock

from ciw.data_record import DataRecord

from src.config import BASE, IMPROVEMENTS, Workshop
from src.experiments import confidence_summary, nominal_capacity, replica_seeds
from src.metrics import group_vehicles, overlap, summarize_day
from src.model import Day, generate_arrivals, simulate_day


def visit(node, arrival, start, end, destination):
    return DataRecord(
        id_number=1, customer_class="neumaticos", original_customer_class="neumaticos", node=node,
        arrival_date=arrival, waiting_time=start - arrival, service_start_date=start, service_time=end - start,
        service_end_date=end, time_blocked=0, exit_date=end, destination=destination,
        queue_size_at_arrival=0, queue_size_at_departure=0, server_id=1, record_type="service",
    )


class ArrivalTests(unittest.TestCase):
    def test_inverse_intensity_crosses_bands_and_stops_at_close(self):
        clock = Mock()
        # Integrales acumuladas en minutos 120, 360 y 480: 6, 12 y 16.
        clock.expovariate.side_effect = [5, 1, 1.5, 5.5, 3]
        plan = generate_arrivals(Workshop(), clock, Random(10))
        self.assertEqual([minute for minute, _ in plan], [100, 120, 180, 390])

    def test_counts_by_band_and_class_are_consistent_with_inputs(self):
        workshop = Workshop()
        plans = [generate_arrivals(workshop, Random(i), Random(5000 + i)) for i in range(500)]
        counts = [0, 0, 0]
        categories = Counter()
        for day in plans:
            for when, category in day:
                self.assertTrue(0 <= when < 480)
                counts[(when >= 120) + (when >= 360)] += 1
                categories[category] += 1
        for actual, expected in zip(counts, (6, 6, 4), strict=True):
            self.assertAlmostEqual(actual / len(plans), expected, delta=0.4)
        for category in workshop.classes:
            self.assertAlmostEqual(categories[category.name] / sum(counts), category.share, delta=0.03)

    def test_uniform_profile_preserves_counts_and_marks_with_common_seed(self):
        base = Workshop()
        uniform = IMPROVEMENTS[2].configure(base)
        self.assertEqual(uniform.expected_demand, base.expected_demand)
        regular_day, uniform_day = (simulate_day(workshop, 2026) for workshop in (base, uniform))
        self.assertEqual([kind for _, kind in regular_day.arrivals], [kind for _, kind in uniform_day.arrivals])
        self.assertNotEqual(regular_day.arrivals, uniform_day.arrivals)


class CiwTests(unittest.TestCase):
    def test_reproducibility_and_seed_independence(self):
        seeds = replica_seeds(184, 50)
        self.assertEqual(seeds, replica_seeds(184, 50))
        self.assertEqual(len(set(seeds)), 50)
        workshop = Workshop()
        first = simulate_day(workshop, seeds[0])
        different = simulate_day(workshop, seeds[1])
        self.assertEqual(first, simulate_day(workshop, seeds[0]))
        self.assertNotEqual(first, different)

    def test_vehicle_paths_classes_and_rework(self):
        workshop = replace(Workshop(), rework_probability=0.6)
        day = simulate_day(workshop, 3)
        paths = defaultdict(list)
        repairs = {kind.name: kind.repair for kind in workshop.classes}
        for record in day.visits:
            paths[record.id_number].append(record)
            self.assertEqual(record.record_type, "service")
            self.assertLessEqual(record.arrival_date, record.service_start_date)
            self.assertLessEqual(record.service_start_date, record.service_end_date)
            self.assertGreaterEqual(record.waiting_time, 0)
            if record.node == 3:
                lower, _, upper = repairs[record.customer_class]
                self.assertLess(lower, record.service_time)
                self.assertLess(record.service_time, upper)

        self.assertEqual(len(paths), len(day.arrivals))
        self.assertEqual(set(paths), set(range(1, len(day.arrivals) + 1)))
        for vehicle_id, (arrival, cls) in enumerate(day.arrivals, start=1):
            path = sorted(paths[vehicle_id], key=lambda record: record.arrival_date)
            self.assertEqual([v.node for v in path], [1, 2] + [3, 4] * (len(path) // 2 - 1))
            self.assertEqual([v.destination for v in path], [v.node for v in path[1:]] + [-1])
            self.assertEqual({v.customer_class for v in path}, {cls})
            self.assertEqual({v.original_customer_class for v in path}, {cls})
            self.assertAlmostEqual(path[0].arrival_date, arrival)
            self.assertLess(path[0].arrival_date, workshop.close_min)

        global_values, stations = summarize_day(day, workshop, BASE)
        self.assertGreater(global_values["retrabajos"], 0)
        for index in ("reparacion", "calidad"):
            self.assertEqual(stations[index]["visitas_cohorte"], global_values["recibidos"] + global_values["retrabajos"])

    def test_zero_rework_and_fifo_shared_by_all_classes(self):
        scenario = replace(BASE, factor=2)
        workshop = replace(scenario.configure(Workshop()), rework_probability=0)
        day = simulate_day(workshop, 3)
        repairs = sorted((v for v in day.visits if v.node == 3), key=lambda v: v.arrival_date)
        self.assertEqual(len(repairs), len(day.arrivals))
        starts = [v.service_start_date for v in repairs]
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(len({v.server_id for v in repairs}), 3)
        self.assertTrue(any(sum(r.service_start_date <= x < r.service_end_date for r in repairs) == 3 for x in starts))

    def test_conservation_and_utilization_in_both_windows(self):
        scenario = replace(BASE, factor=2)
        workshop = scenario.configure(Workshop())
        for seed in (3, 8, 2026):
            with self.subTest(seed=seed):
                day = simulate_day(workshop, seed)
                daily, stations = summarize_day(day, workshop, scenario)
                self.assertEqual(daily["recibidos"], daily["terminados_jornada"] + daily["pendientes_cierre"])
                self.assertEqual(daily["pendientes_cierre"], daily["terminados_vaciado"])
                self.assertEqual(daily["pendientes_cierre"], sum(s["pendientes_cierre"] for s in stations.values()))
                self.assertEqual(daily["lambda_vaciado_h"], 0)
                for row in [daily, *stations.values()]:
                    for label in ("jornada", "vaciado"):
                        self.assertTrue(0 <= row[f"utilizacion_{label}"] <= 1 + 1e-12)
                        self.assertTrue(0 <= row[f"lq_{label}"] <= row[f"l_{label}"])
                self.assertAlmostEqual(
                    max(0, day.end_min - 480), daily["extra_min"]
                )


class MetricTests(unittest.TestCase):
    def test_integrates_observed_intervals_before_and_after_close(self):
        day = Day(((470, "neumaticos"),), (
            visit(1, 470, 472, 476, 2), visit(2, 476, 479, 490, 3),
            visit(3, 490, 495, 510, 4), visit(4, 510, 512, 520, -1),
        ), 520)
        daily, stations = summarize_day(day, Workshop(), BASE)
        self.assertEqual(daily["w_vehiculo_cohorte_min"], 50)
        self.assertEqual(daily["p95_w_vehiculo_cohorte_min"], 50)
        self.assertEqual(daily["wq_vehiculo_cohorte_min"], 12)
        self.assertIsNone(daily["w_vehiculo_terminado_jornada_min"])
        self.assertAlmostEqual(daily["l_jornada"], 10 / 480)
        self.assertAlmostEqual(daily["lq_jornada"], 5 / 480)
        self.assertAlmostEqual(daily["l_vaciado"], 1)
        self.assertAlmostEqual(daily["lq_vaciado"], 7 / 40)
        self.assertEqual(daily["throughput_jornada_h"], 0)
        self.assertEqual(daily["throughput_vaciado_h"], 1.5)
        self.assertEqual(stations["diagnostico"]["pendientes_cierre"], 1)
        self.assertEqual(stations["reparacion"]["utilizacion_vaciado"], 15 / (3 * 40))
        self.assertEqual(stations["reparacion"]["mu_visita_cohorte_por_servidor_h"], 4)
        self.assertEqual(daily["ingresos_clp"], 50_000)
        self.assertEqual(daily["costos_variables_clp"], 18_000)
        self.assertEqual(daily["costos_personal_clp"], 255_000)
        self.assertAlmostEqual(daily["costos_extra_clp"], (10 * 8_000 + 15 * 9_000 + 8 * 7_000) / 60)

    def test_little_as_a_full_observation_sample_path_identity(self):
        workshop = Workshop()
        day = simulate_day(workshop, 3)
        daily, _ = summarize_day(day, workshop, BASE)
        horizon = workshop.close_min + daily["extra_min"]
        l_observed = sum(overlap(v.arrival_date, v.exit_date, 0, horizon) for v in day.visits) / horizon
        lq_observed = sum(overlap(v.arrival_date, v.service_start_date, 0, horizon) for v in day.visits) / horizon
        lambda_min = daily["recibidos"] / horizon
        self.assertAlmostEqual(l_observed, lambda_min * daily["w_vehiculo_cohorte_min"])
        self.assertAlmostEqual(lq_observed, lambda_min * daily["wq_vehiculo_cohorte_min"])
        for vehicle in group_vehicles(day.visits):
            self.assertAlmostEqual(vehicle.departure - vehicle.arrival, vehicle.wait + vehicle.service)

    def test_empty_day_and_disabled_economy(self):
        workshop = replace(replace(BASE, factor=0).configure(Workshop()), economics=None)
        day = simulate_day(workshop, 2026)
        daily, stations = summarize_day(day, workshop, BASE)
        self.assertEqual(day, Day((), (), 0))
        self.assertEqual(daily["l_jornada"], 0)
        self.assertEqual(daily["extra_min"], 0)
        self.assertIsNone(daily["w_vehiculo_cohorte_min"])
        self.assertIsNone(stations["reparacion"]["utilizacion_vaciado"])
        self.assertNotIn("margen_operacional_clp", daily)

    def test_statistics_and_nominal_capacity(self):
        summary = confidence_summary([1, 2, None, 3])
        self.assertEqual(summary["n"], 3)
        self.assertEqual(summary["media"], 2)
        self.assertEqual(summary["de"], 1)
        self.assertAlmostEqual(summary["ic95_sup"], 4.4841377117)
        capacity = {entry["estacion"]: entry for entry in nominal_capacity(Workshop())}
        self.assertAlmostEqual(capacity["reparacion"]["capacidad_nominal_vehiculos_h"], 171 / 63.5)


if __name__ == "__main__":
    unittest.main()

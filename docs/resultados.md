# Resultados de Taller en Crisis

La corrida definitiva contiene 100 réplicas por configuración. Son 1.200 jornadas simuladas en E0, los siete puntos de E1 y E2–E5. La semilla maestra fue `80912026`. Los valores de las tablas están redondeados. Las salidas reproducibles, con desviaciones e intervalos, se encuentran en [`results/`](../results/).

## Escenario base E0

| Indicador | Media | IC 95 % |
| --- | ---: | ---: |
| Vehículos recibidos por jornada | 15,87 | 15,16 a 16,58 |
| Llegadas efectivas por hora de jornada | 1,98 | 1,90 a 2,07 |
| Entregas dentro de la jornada | 12,08 | 11,50 a 12,66 |
| Throughput regular (vehículos/h) | 1,51 | 1,44 a 1,58 |
| Pendientes al cierre | 3,79 | 3,36 a 4,22 |
| Tiempo extra transcurrido (min) | 110,0 | 98,6 a 121,5 |
| Permanencia W de la cohorte (min/vehículo) | 119,3 | 114,6 a 123,9 |
| Espera Wq de la cohorte (min/vehículo) | 21,3 | 17,4 a 25,1 |
| P95 diario de la permanencia (min) | 185,9 | 177,6 a 194,3 |
| L en jornada (vehículos) | 3,43 | 3,17 a 3,69 |
| Lq en jornada (vehículos) | 0,70 | 0,54 a 0,85 |
| Retrabajos de la cohorte (visitas/día) | 0,78 | 0,62 a 0,94 |

| Estación | Espera de la cohorte (min/visita) | Utilización en jornada | μ de la cohorte (visitas/servidor-h) |
| --- | ---: | ---: | ---: |
| Recepción | 0,54 | 16,5 % | 12,02 |
| Diagnóstico | 7,49 | 47,4 % | 3,99 |
| Reparación | 11,18 | 60,8 % | 0,96 |
| Control de calidad | 1,38 | 26,8 % | 5,99 |

**Reparación es el cuello de botella principal** por su espera, utilización y capacidad nominal. Diagnóstico genera la segunda mayor espera. La utilización de reparación promediada sobre las ocho horas está influida por el arranque vacío, las fluctuaciones de llegada y el trabajo que queda al cierre. [Espera por estación](../figures/01_espera_estaciones.png) · [Utilización por estación](../figures/02_utilizacion_estaciones.png)

## Prueba de carga E1

| Factor | Recibidos/día | Wq por vehículo (min) | Reparación ocupada en jornada | Pendientes al cierre | Extra (min) | Entregas en jornada (veh/h) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0,50 | 7,99 | 4,27 | 31,8 % | 1,46 | 55,6 | 0,82 |
| 0,75 | 11,84 | 9,60 | 46,3 % | 2,44 | 80,9 | 1,18 |
| 1,00 | 15,87 | 21,26 | 60,8 % | 3,79 | 110,0 | 1,51 |
| 1,25 | 19,82 | 35,88 | 71,8 % | 5,24 | 139,2 | 1,82 |
| 1,50 | 23,83 | 60,19 | 81,2 % | 7,65 | 182,1 | 2,02 |
| 1,75 | 27,65 | 98,28 | 85,7 % | 10,82 | 256,8 | 2,10 |
| 2,00 | 31,98 | 136,63 | 87,6 % | 14,67 | 345,7 | 2,16 |

- **Límite operativo ilustrativo.** Con metas de hasta dos horas extra y hasta 25 % de pendientes, evaluadas sobre las medias diarias, 1,00× es el mayor factor ensayado que cumple ambas. Con 1,25×, el promedio sube a 139,2 minutos extra y 25,3 % de pendientes. Las metas se aplicaron como criterio de lectura de los resultados y requieren validación con el taller. Los IC de E0 incluyen valores por encima de los umbrales.
- **Balance nominal.** La carga esperada de reparación es `63,5 / 0,95 = 66,84` minutos-mecánico por vehículo, contando retornos. Tres mecánicos equivalen a 180 minutos-mecánico por hora, de donde resulta una capacidad nominal de **2,69 vehículos/h** o **21,54 vehículos en ocho horas**. Con demanda base de 2 veh/h, el equilibrio de carga media se ubica cerca de **1,35×**. A 1×, el primer tramo ya tiene una tasa externa de 3 veh/h. A 2×, diagnóstico también alcanza su balance nominal de 4 veh/h en promedio. La capacidad nominal representa un balance de trabajo, mientras que las entregas regulares también dependen de la variabilidad, el arranque y la hora de llegada.
- **Saturación observada.** Entre 1,50× y 2× la demanda aumenta en 8,15 vehículos diarios, pero las entregas regulares aumentan en 1,13. El vaciado pasa de 182,1 a 345,7 min. Que todas las jornadas terminen vacías es consecuencia de interrumpir las llegadas y continuar el servicio. La simulación mide el desempeño dentro del turno y el trabajo desplazado al vaciado.

[Respuesta y utilización frente a carga](../figures/03_respuesta_carga.png) · [Pendientes y tiempo extra](../figures/04_pendientes_carga.png) · [Throughput regular](../figures/05_throughput_carga.png)

## Mejoras E2–E5 y análisis económico

E5 se fijó antes de la corrida definitiva. El piloto con `replica_seeds(80912025, 50)` comparó E0 y E2–E4. E2 y E3 redujeron la permanencia media de 119,70 a 109,10 y 116,82 min, respectivamente. También redujeron el tiempo extra de 99,44 a 92,37 y 94,01 min. E4 redujo la permanencia a 117,56 min y aumentó el tiempo extra a 101,10 min. Se combinó E2 con E3 para medir su efecto operacional conjunto con semillas independientes del piloto.

| Escenario | W de la cohorte (min) | Pendientes al cierre | Extra (min) | Retrabajos/día | Margen ilustrativo (miles de CLP/día) |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 · Base | 119,26 | 3,79 | 110,03 | 0,78 | 714,3 |
| E2 · Cuarto mecánico | 109,89 | 3,53 | 97,80 | 0,86 | 668,0 |
| E3 · Menos retrabajo | 116,28 | 3,74 | 102,15 | 0,37 | 717,3 |
| E4 · Llegadas uniformes | 115,02 | 4,06 | 115,26 | 0,77 | 709,5 |
| E5 · Cuarto mecánico y menos retrabajo | 106,93 | 3,45 | 92,31 | 0,33 | 672,5 |

- **E2** redujo la permanencia en 9,37 min [IC 95 % −12,49 a −6,25] y los pendientes en 0,26 vehículos diarios. El margen estimado disminuyó 46.229 CLP/día [−50.858 a −41.600]. Con igual cantidad de vehículos, el ahorro neto de materiales y horas activas extra previo al salario adicional fue de unos 1.771 CLP/día, frente al costo ilustrativo de 48.000 CLP/día.
- **E3** redujo los retrabajos en 0,41/día [−0,55 a −0,27] y el tiempo extra en 7,88 min [−13,50 a −2,26]. Su margen subió 3.028 CLP/día [−429 a 6.485]. Al sumar los 5.000 CLP/día presupuestados en la intervención, el ahorro medio previo al costo de implementarla fija un punto de equilibrio de unos **8.028 CLP/día** [4.571 a 11.485] bajo estos supuestos.
- **E4** redujo la permanencia en 4,24 min [−7,56 a −0,92] y aumentó los pendientes en 0,27 vehículos/día [0,08 a 0,46], con igual demanda total. El perfil uniforme reduce la concentración de primera hora y redistribuye parte de esas llegadas a horas posteriores. El aumento medio del vaciado fue 5,23 min [−3,86 a 14,31].
- **E5** logró el mayor recorte de permanencia, 12,32 min [−15,58 a −9,07], y de tiempo extra, 17,72 min [−24,95 a −10,49]. Su margen disminuyó 41.753 CLP/día [−46.482 a −37.025]. La capacidad adicional podría adquirir valor con demanda mayor o con un costo medible por entregas tardías. Esos beneficios quedan fuera de esta corrida.

Todos los intervalos de cambios corresponden a diferencias pareadas contra E0. Los importes son sensibles a precios, costos, demanda y condiciones de pago de horas extraordinarias. [Comparación operacional](../figures/06_escenarios_mejora.png) · [Comparación económica](../figures/07_comparacion_economica.png) · [Diferencias e intervalos](../results/diferencias_pareadas_vs_E0.csv)

## Próxima iteración

1. Registrar llegadas, clase y marcas de entrada, inicio y término por estación durante varias semanas. Registrar por separado duración y materiales de cada retrabajo, además de pendientes y horas pagadas después del cierre.
2. Probar primero E3 con un piloto real de calidad. Validar si el costo queda por debajo del ahorro y si la probabilidad de retrabajo se acerca al 2 % sin alargar el control.
3. Calibrar precios, costos, disponibilidad real de mecánicos y formas de agendar. Con esos datos, comparar una agenda que evite trabajos largos cerca del cierre y capacidad adicional concentrada en horas punta. Simular el arrastre entre días si el taller no vacía al cierre.

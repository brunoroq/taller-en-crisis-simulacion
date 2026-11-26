# Taller en Crisis · Resumen académico

**INFB8091 · Desempeño de Sistemas · UTEM · Segundo semestre de 2026**  
**Equipo Kernel en Crisis**

## Problemática

Un taller automotriz recibe vehículos de distinta complejidad y debe entregar los trabajos aceptados el mismo día. Las llegadas varían según la hora y un rechazo en control de calidad puede ocupar nuevamente a un mecánico. Se busca identificar el cuello de botella, medir qué carga cabe dentro del turno y comparar mejoras por desempeño y costo ilustrativo.

## Modelo conceptual

**Llegada → Recepción (1) → Diagnóstico (1) → Reparación (3) → Control de calidad (1) → Entrega.** Los tres mecánicos comparten una sola cola FIFO y pueden atender cualquier clase. Un vehículo rechazado en calidad vuelve a la cola de reparación y conserva su clase. Cada réplica comienza vacía a las 09:00. Se aceptan llegadas hasta antes de las 17:00 y el personal termina el trabajo pendiente después del cierre. La red es abierta, con llegadas Poisson por tramos, tiempos triangulares, clases de servicio y un bucle de retrabajo. Su comportamiento transitorio requiere simulación para evaluar las colas y el cierre. [Modelo y medición](modelo.md)

## Parámetros de entrada

| Franja | Llegadas medias (veh/h) | Vehículos esperados |
| --- | ---: | ---: |
| 09:00–11:00 | 3,0 | 6 |
| 11:00–15:00 | 1,5 | 6 |
| 15:00–17:00 | 2,0 | 4 |
| Total del turno | 2,0 en promedio | 16 |

| Operación | Tipo o proporción de llegadas | Triangular mín., moda, máx. (min) | Media teórica (min) |
| --- | --- | --- | ---: |
| Recepción | Todas | 3, 5, 7 | 5 |
| Diagnóstico | Todas | 10, 15, 20 | 15 |
| Reparación | Neumáticos, 35 % | 15, 30, 45 | 30 |
| Reparación | Sistema eléctrico, 30 % | 30, 60, 90 | 60 |
| Reparación | Mecánica general, 35 % | 60, 90, 150 | 100 |
| Control de calidad | Todas | 5, 10, 15 | 10 |

El perfil de llegadas representa un pico inicial, una baja al mediodía y un repunte al final. Los límites y modas de servicio representan tiempos mínimos, típicos y altos de trabajos de distinta complejidad. El promedio de 63,5 min por visita a reparación se obtiene ponderando las medias de las tres clases. Se supone un 5 % de rechazo en cada control de calidad, independiente entre visitas. Al retornar se vuelve a muestrear la triangular de reparación de la clase. Las tasas, proporciones, tiempos y probabilidad son supuestos que requieren medición en terreno. [Justificación y parámetros económicos](parametros.md)

## Indicadores de E0

Se usó Python 3.12.14 y Ciw 3.2.7. Cada configuración tiene 100 réplicas con semilla maestra `80912026`. El turno regular abarca los minutos 0 a 480. Se siguió la cohorte de ingresos hasta su entrega, incluidos los servicios después del cierre. Los indicadores temporales de la cohorte son promedios de estadísticas diarias.

| Indicador global de E0 | Media | IC 95 % |
| --- | ---: | ---: |
| Llegadas externas por día | 15,87 | 15,16 a 16,58 |
| Entregas dentro del turno por día | 12,08 | 11,50 a 12,66 |
| Pendientes al cierre por día | 3,79 | 3,36 a 4,22 |
| Tiempo de vaciado extra (min) | 110,03 | 98,60 a 121,47 |
| Tasa de llegadas y de entregas en turno (veh/h) | 1,98 y 1,51 | 1,90 a 2,07 y 1,44 a 1,58 |
| W y Wq por vehículo de la cohorte (min) | 119,26 y 21,26 | 114,58 a 123,94 y 17,44 a 25,07 |
| P95 diario medio de W en la cohorte (min) | 185,92 | 177,58 a 194,26 |
| L y Lq durante el turno (vehículos) | 3,43 y 0,70 | 3,17 a 3,69 y 0,54 a 0,86 |
| Retrabajos por cohorte diaria | 0,78 | 0,62 a 0,94 |

Reparación presentó 11,18 min de espera media por visita, 64,03 min de servicio y 60,82 % de utilización durante el turno. Diagnóstico fue la segunda estación con más espera, 7,49 min por visita. Los indicadores se recalcularon con 1.587 recorridos, 6.504 registros de visita y los estados entre eventos de Ciw. La ley de Little se comprobó en cada réplica usando la observación completa, con apertura y término vacíos. [Tabla completa, unidades y método de auditoría](auditoria.md#3-indicadores-consolidados-de-e0)

## Comparación de todos los escenarios

| Configuración | Cambio | Recibidos/día | Entregados en turno/día | Pendientes al cierre/día | W / Wq (min/vehículo) | Extra (min/día) | Utilización de reparación en turno |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | Base | 15,87 | 12,08 | 3,79 | 119,26 / 21,26 | 110,03 | 60,82 % |
| E1 · 0,50× | Carga | 7,99 | 6,53 | 1,46 | 101,74 / 4,27 | 55,59 | 31,84 % |
| E1 · 0,75× | Carga | 11,84 | 9,40 | 2,44 | 106,13 / 9,60 | 80,87 | 46,27 % |
| E1 · 1,00× | Carga base, mismas semillas de E0 | 15,87 | 12,08 | 3,79 | 119,26 / 21,26 | 110,03 | 60,82 % |
| E1 · 1,25× | Carga | 19,82 | 14,58 | 5,24 | 132,30 / 35,88 | 139,15 | 71,81 % |
| E1 · 1,50× | Carga | 23,83 | 16,18 | 7,65 | 157,05 / 60,19 | 182,13 | 81,15 % |
| E1 · 1,75× | Carga | 27,65 | 16,83 | 10,82 | 196,19 / 98,28 | 256,83 | 85,74 % |
| E1 · 2,00× | Carga | 31,98 | 17,31 | 14,67 | 234,59 / 136,63 | 345,67 | 87,61 % |
| E2 | Cuarto mecánico | 15,87 | 12,34 | 3,53 | 109,89 / 11,83 | 97,80 | 46,86 % |
| E3 | Retrabajo de 5 % a 2 % | 15,87 | 12,13 | 3,74 | 116,28 / 20,33 | 102,15 | 59,90 % |
| E4 | Llegadas a 2 veh/h constantes | 15,87 | 11,81 | 4,06 | 115,02 / 17,73 | 115,26 | 59,43 % |
| E5 | Cuarto mecánico y retrabajo al 2 % | 15,87 | 12,42 | 3,45 | 106,93 / 11,54 | 92,31 | 45,44 % |

W y Wq corresponden a la cohorte completa. Las cifras de utilización en E2 y E5 tienen cuatro puestos disponibles en reparación. Los IC t bilaterales por configuración y las diferencias pareadas contra E0 están en los CSV. El pareo conserva las semillas entre escenarios. Cambiar el orden de eventos puede cambiar qué vehículo recibe cada muestra de servicio o decisión de ruta. [Agregados](../results/resumen.csv) · [Diferencias pareadas](../results/diferencias_pareadas_vs_E0.csv) · [Gráficos](../figures/)

## Interpretación

- **Vaciado y uso de los mecánicos.** El 60,82 % promedia toda la jornada. Hubo 23 jornadas con cola en reparación al cierre. De los pendientes, 340 de 379 habían llegado desde las 15:00. En 59 de las 95 jornadas con vaciado, el último vehículo entregado era de mecánica general. En toda la muestra, el último vehículo de cada día pasó en promedio 79,15 minutos del vaciado en reparación, 16,54 en otros servicios y 14,34 esperando. La espera antes del cierre también puede dejar más trabajo para después de las 17:00. [Desglose de las trayectorias](auditoria.md#4-por-qué-el-vaciado-dura-110-minutos)
- **Capacidad nominal.** Reparación demanda `63,5/0,95 = 66,84` minutos-mecánico por vehículo, considerando retornos. Tres mecánicos aportan 180 minutos-mecánico por hora y el balance nominal es 2,69 veh/h, aproximadamente 1,35 veces la tasa media base. El arranque vacío, el horario de las llegadas y las demás estaciones afectan las entregas dentro del turno.
- **Saturación observada.** Aumentar la demanda entre 1,50× y 2,00× agrega 8,15 llegadas diarias y 1,13 entregas regulares. La espera y el vaciado siguen creciendo. El vaciado final ocurre porque se interrumpen las llegadas y continúan los servicios.
- **Límite operativo.** Con las metas ilustrativas de hasta 120 min extra y 25 % de pendientes evaluadas sobre medias diarias, el mayor punto ensayado que satisface ambas es 1,00×. En E0 solo 43 de 100 jornadas cumplen ambas metas simultáneamente. Un objetivo de cumplimiento por jornada requiere explicitar qué proporción de días debe alcanzar la meta.

## Justificación de las mejoras

- **E2 amplía el cuello de botella.** Reduce W en 9,37 min y el tiempo extra en 12,24 min. Con igual cohorte de ingresos, el margen ilustrativo cae en unos 46.229 CLP/día al añadir el costo del mecánico. Haría falta valorar capacidad, oportunidad de entrega y demanda adicional para evaluar el puesto.
- **E3 reduce la repetición de servicio.** Los retornos bajan de 0,78 a 0,37 por día y el vaciado se reduce 7,88 min [IC 95 % −13,50 a −2,26]. Con los costos supuestos, el margen cambia en +3.028 CLP/día [−429 a 6.485]. Se justifica validar primero esta intervención con un piloto y contrastar su costo con el ahorro simulado antes de comprometer gastos.
- **E4 desplaza parte de la demanda matinal al tramo de 11:00 a 15:00.** Después de las 15:00 conserva las mismas llegadas que E0 para cada semilla auditada. Reduce W en 4,24 min, aumenta el promedio de pendientes al cierre en 0,27 [0,075 a 0,465] y el IC del cambio en vaciado incluye cero. La operación podría evaluar criterios de agenda que consideren la duración de los trabajos cerca del cierre.
- **E5 combina las mejoras que redujeron el vaciado en un piloto de 50 réplicas.** En la corrida definitiva con semillas independientes del piloto, logra el mayor recorte de W (12,32 min) y de tiempo extra (17,72 min). El margen ilustrativo disminuye 41.753 CLP/día, de modo que su conveniencia depende del valor real de las entregas a tiempo y del costo del puesto adicional.

Los precios, materiales, remuneraciones y gastos son supuestos. La comparación imputa ingresos y costos variables a la cohorte de la jornada, incluidos los vehículos entregados en el vaciado. Las horas extra valorizan minutos-persona activos por estación. [Auditoría económica](auditoria.md#5-auditoría-económica)

## Limitaciones

- La carga, las mezclas, los servicios y los costos requieren datos de un taller. Los IC representan variabilidad entre réplicas con parámetros fijos.
- El taller abre vacío y termina todas las órdenes antes de la siguiente réplica. El resultado omite el arrastre entre días, las pausas y los límites de espacio, repuestos y disponibilidad.
- La probabilidad de retorno es común a las tres clases y la reparación de retorno usa la misma distribución que una inicial. Una corrección real puede ser más corta o más larga.
- El costo extra excluye el tiempo ocioso posterior al cierre. La evaluación no incorpora inversión, recargos reales ni un costo de entrega tardía.
- El límite de servicio depende de metas ilustrativas y de los puntos ensayados. Su uso para planificación requiere definir el nivel de servicio y medir una carga más fina cerca de su umbral.

## Cumplimiento académico

| Requisito de la pauta del Trabajo 2 | Evidencia o estado |
| --- | --- |
| Modelar un proceso real con colas y estaciones | Flujo de trabajo de un taller convencional, con parámetros iniciales para validar. |
| Dos o más colas en serie y una estación con tres servidores o más | Cuatro etapas consecutivas y tres mecánicos que consumen de una sola cola. |
| Modelo que requiera simulación y uso de Ciw | Red con Poisson no homogéneo, triangulares por clase, arranque vacío y retrabajo, ejecutada por Ciw 3.2.7. |
| Definir y justificar parámetros | Mezcla, tasas, triangulares y probabilidad de retorno documentadas con su derivación y su carácter supuesto. |
| Obtener indicadores, probar carga y determinar límites | Indicadores por visita y vehículo, 12 configuraciones, siete factores de carga, balance nominal y límite por metas ilustrativas. |
| Proponer mejoras, volver a simular y concluir | E2–E5 con comparaciones pareadas, justificación y análisis económico ilustrativo. |
| Repositorio GitHub con fuentes y resultados | Fuentes, pruebas, siete gráficos y CSV verificados en el repositorio local. La publicación en GitHub queda pendiente. |
| Detalle de prompts | Se conservaron el [encargo inicial](../prompts/001_desarrollo_inicial.md) y el [encargo de auditoría](../prompts/002_auditoria.md). |
| Presentación y exposición del grupo | Este resumen reúne la problemática, decisiones y evidencia que exige la pauta. La presentación y la exposición quedan pendientes. |

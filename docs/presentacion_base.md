# Taller en Crisis · Contenido base para la exposición

**INFB8091 · Desempeño de Sistemas · UTEM · Segundo semestre de 2026**  
**Equipo Kernel en Crisis**

## 1. Problemática y objetivos

Un taller automotriz recibe trabajos de distinta complejidad a lo largo del turno. Las llegadas cercanas al cierre y las reparaciones largas pueden extender la última entrega. Si un vehículo falla el control de calidad, vuelve a competir por el tiempo de los mecánicos.

- Identificar qué estación limita las entregas y concentra la espera.
- Evaluar cómo cambian las colas, las entregas regulares y el vaciado al aumentar la demanda.
- Comparar intervenciones con indicadores operacionales y costos ilustrativos.
- Determinar qué mediciones del taller hacen falta antes de recomendar una inversión o comprometer un nivel de servicio.

## 2. Modelo conceptual

**Llegadas → Recepción (1) → Diagnóstico (1) → Reparación (3) → Control de calidad (1) → Entrega.**

Una falla en calidad devuelve el vehículo a la **cola única** de reparación y conserva su clase e identificador. Los nodos aplican FIFO. Tres mecánicos polivalentes trabajan en paralelo en E0. Cada jornada comienza vacía. Las llegadas externas cesan al minuto 480 y el personal termina los trabajos pendientes. Los retornos cuentan como visitas adicionales a reparación y calidad. [Modelo y medición](modelo.md)

## 3. Parámetros

Las llegadas siguen un Poisson por tramos. Las tasas son **3,0 veh/h** de 09:00 a 11:00, **1,5 veh/h** de 11:00 a 15:00 y **2,0 veh/h** de 15:00 a 17:00. Suman 16 llegadas esperadas en el turno.

| Servicio | Mezcla de llegadas | Triangular en min (mínimo, moda, máximo) |
| --- | ---: | --- |
| Recepción | Todas las clases | (3, 5, 7) |
| Diagnóstico | Todas las clases | (10, 15, 20) |
| Neumáticos | 35 % | (15, 30, 45) |
| Sistema eléctrico | 30 % | (30, 60, 90) |
| Mecánica general | 35 % | (60, 90, 150) |
| Control de calidad | Todas las clases | (5, 10, 15) |

E0 utiliza **5 % de rechazo por control**. El retrabajo vuelve a usar la triangular de la clase. E3 y E5 prueban un rechazo de **2 %**. Los tiempos, la mezcla y las tasas, así como los precios y costos, son supuestos del modelo pendientes de medición real. [Inventario y evidencia pendiente](validacion_parametros.md)

## 4. Metodología de simulación

La corrida definitiva usó Ciw 3.2.7 y Python 3.12.14, con **100 jornadas por configuración** y semilla maestra **80912026**. Las 12 configuraciones abarcan E0, siete factores de E1 y E2–E5. E1 a 1,00× reproduce E0 con las mismas semillas. El calendario de llegadas se genera con la intensidad acumulada de cada tramo y Ciw ejecuta las colas, los servicios y las rutas.

La unidad de replicación es la jornada. Se informan medias diarias e IC t bilaterales del 95 %. Para E2–E5 se comparan diferencias con E0 por semilla. La semilla común conserva la comparación del volumen, la mezcla y, cuando el perfil se mantiene, las horas de llegada. Cambiar el orden de eventos puede cambiar la asignación individual de muestras de servicio o ruta. La auditoría verificó recorridos e indicadores contra los registros y estados, comprobó Little sobre la trayectoria completa que empieza y termina vacía y reprodujo las salidas originales. [Manifiesto](../results/configuracion_ejecutada.json) · [Auditoría](auditoria.md)

## 5. Indicadores y unidades

- **Por vehículo.** W es el tiempo transcurrido hasta la entrega final y Wq suma las esperas del recorrido, incluidos los retornos. El P95 publicado es la media de percentiles diarios de W. El throughput regular son entregas finales por hora del turno.
- **Por visita.** W, Wq y S son permanencia, espera y servicio activo en una entrada a la estación. Las tasas de entrada y salida cuentan visitas, incluidas las repetidas. La tasa μ de servicio por servidor es el promedio de las tasas diarias de visitas por hora activa de servidor.
- **Por ventana de reloj.** L y Lq son poblaciones medias presente y en cola, ponderadas por tiempo. La utilización divide el servicio activo por el total de minutos de servidor disponibles en esa ventana. El turno abarca 0–480 min. El vaciado abarca desde el cierre hasta la última entrega en jornadas con pendientes. Los tiempos de la cohorte siguen todos los vehículos aceptados hasta su entrega.
- **Cierre y cumplimiento.** Los pendientes se miden al minuto 480. Los minutos extra de reloj se cuentan hasta la última entrega. Las metas ilustrativas son ≤120 minutos extra y ≤25 % de vehículos pendientes respecto de los recibidos ese día.

## 6. Resultados del escenario base

E0 recibió **15,87 vehículos por jornada**, entregó **12,08** dentro del turno y dejó **3,79 pendientes**. El throughput regular fue de **1,510 veh/h**. W fue **119,26 min/vehículo**, Wq **21,26 min/vehículo** y el P95 diario medio **185,92 min**. El vaciado tomó **110,03 min** en promedio.

Los gráficos de carga muestran E0 en el punto 1,00× para permanencia, pendientes y throughput. El panel de mejoras muestra directamente E0 para permanencia, retrabajos, pendientes y vaciado. Los demás indicadores y los IC están en las tablas de respaldo. [Respuesta en 1,00×](../figures/03_respuesta_carga.png) · [Pendientes y vaciado en 1,00×](../figures/04_pendientes_carga.png) · [Llegadas y throughput en 1,00×](../figures/05_throughput_carga.png) · [Comparación contra E0](../figures/06_escenarios_mejora.png)

## 7. Cuello de botella y vaciado

**Reparación** registró la espera más alta, **11,18 min/visita**, y **60,82 % de utilización regular**. Diagnóstico registró la segunda espera más alta, **7,49 min/visita**. El porcentaje de reparación incluye las horas de menor actividad y el arranque vacío. [Espera por estación](../figures/01_espera_estaciones.png) · [Utilización regular por estación](../figures/02_utilizacion_estaciones.png)

La auditoría de trayectorias encontró que **340 de los 379 pendientes** habían llegado desde las 15:00 y que había cola de reparación al cierre en **23 de 100 jornadas**. En promedio, el último vehículo de cada jornada pasó **79,15 minutos** del vaciado en reparación, **16,54** en otros servicios y **14,34** esperando. Los promedios incluyen jornadas con vaciado cero. Para este desglose se usa la auditoría de eventos como respaldo. [Desglose del vaciado](auditoria.md#4-por-qué-el-vaciado-dura-110-minutos)

## 8. Análisis de carga y metas operacionales

| Concepto | Resultado e interpretación | Evidencia |
| --- | --- | --- |
| Capacidad nominal de reparación | **2,69 veh/h**. Tres mecánicos aportan 180 min-mecánico/h. El servicio esperado de reparación por vehículo, incluidos retornos, es 63,5/0,95 = 66,84 min-mecánico. El balance de carga media aparece cerca de **1,35×** la tasa base. | [Balance nominal](../results/capacidad_nominal.csv) |
| Saturación observada en el turno | Entre 1,50× y 2,00× el throughput regular solo subió de **2,022 a 2,164 veh/h**, mientras el vaciado aumentó de **182,13 a 345,67 min**. La espera de la cohorte subió de **60,19 a 136,63 min**. | [Respuesta y utilización](../figures/03_respuesta_carga.png) · [Pendientes y vaciado](../figures/04_pendientes_carga.png) · [Throughput](../figures/05_throughput_carga.png) |
| Límite operativo por las medias | **1,00×** es el mayor punto ensayado que satisface ambas metas al evaluar las medias diarias. E0 dio **110,03 min** y **23,31 %** de pendientes en promedio. A 1,25× dio **139,15 min** y **25,34 %**. | [Gráfico del vaciado y número de pendientes](../figures/04_pendientes_carga.png) · [Tabla de fracción pendiente](#carga-e1) |
| Cumplimiento conjunto por jornada | En E0, **43 de 100** jornadas cumplen ambas metas (IC 95 % Wilson **33,7 % a 52,8 %**). A 0,50× cumplen 74 de 100 y a 2,00× cumplen 3 de 100. | [Tabla de cumplimiento conjunto](#cumplimiento-diario-de-las-metas) · [Réplicas](../results/replicas.csv) |

Cumplir las metas en promedio no garantiza cumplirlas cada día. El límite operativo depende de los umbrales, del criterio de cumplimiento y de los puntos ensayados, y puede alcanzarse antes del balance nominal de carga. La saturación matemática se relaciona con el balance entre demanda y capacidad bajo los supuestos del sistema. La corrida de horizonte finito permite observar deterioro dentro del turno. Para hablar de estabilidad de largo plazo harían falta un régimen de llegadas y una política de operación compatibles con ese análisis.

## 9. Comparación de mejoras

- **E2, cuarto mecánico.** Reduce el vaciado en **12,24 min/día** (IC pareado −19,96 a −4,52) y la permanencia en **9,37 min/vehículo**. Agrega costo regular del puesto.
- **E3, menos retrabajo.** Reduce **0,41 retornos/día** y **7,88 min/día** de vaciado (IC pareado −13,50 a −2,26). Es candidata a un piloto que mida el costo, los rechazos y el tiempo de inspección. La diferencia de margen incluye cero y su superioridad económica sigue por validar.
- **E4, llegadas uniformes.** Reduce la permanencia en **4,24 min/vehículo**, pero sube los pendientes en **0,27 vehículos/día**. Redistribuye llegadas matinales hacia el tramo 11:00–15:00. En las parejas auditadas coinciden las llegadas desde las 15:00. El IC del cambio en vaciado incluye cero.
- **E5, cuarto mecánico y menos retrabajo.** Presenta la mayor reducción media de permanencia y vaciado entre las mejoras ensayadas, **12,33 min/vehículo** y **17,72 min/día**. La combinación se escogió tras un piloto simulado con semillas distintas de las definitivas.

El gráfico 06 compara **medias absolutas con IC por escenario**. La inferencia sobre cambios frente a E0 usa los IC de las diferencias pareadas de la tabla de respaldo. [Comparación operacional](../figures/06_escenarios_mejora.png) · [Diferencias pareadas](#mejoras-e2e5)

## 10. Factibilidad económica

En E0, la cohorte completa generó **1.700.000 CLP/día** de ingresos y un **margen ilustrativo de 714.267 CLP/día**, bajo la configuración de precios y costos. La cohorte incluye las entregas en vaciado. Todos los escenarios de mejora reconocen el mismo ingreso medio porque conservan el volumen y la mezcla del día. E3 estimó **+3.028 CLP/día** de margen frente a E0 (IC pareado **−429 a +6.485**). E2 y E5 redujeron el vaciado con una caída de margen ilustrativa de aproximadamente **46.229** y **41.753 CLP/día**, respectivamente. [Margen y costo de servicio activo extra](../figures/07_comparacion_economica.png) · [Resultados económicos](#economía-de-la-cohorte)

En E0, **110,03 minutos de reloj** de vaciado correspondieron a **239,59 minutos-persona** de servicio activo extra (IC 95 % 207,39 a 271,80), con un costo imputado de unos **34.457 CLP/día**. Los minutos-persona se sumaron por jornada desde los registros por estación. Distintos recursos pueden trabajar simultáneamente. Los minutos-persona activos no equivalen necesariamente a las horas extraordinarias remuneradas. La remuneración real puede incorporar presencia en espera, mínimos o recargos. La conveniencia económica de las intervenciones depende de validar esos términos y los costos unitarios. [Método de costo extra](auditoria.md#5-auditoría-económica) · [Réplicas por estación](../results/replicas_estaciones.csv)

## 11. Limitaciones y decisiones pendientes

- Las distribuciones representan un taller hipotético. Falta medir la demanda por franja, la mezcla, los tiempos por visita y la frecuencia y duración de los retrabajos.
- Cada réplica parte vacía. El arrastre real de órdenes, las pausas, la disponibilidad de puestos y las restricciones de repuestos pueden cambiar el desempeño.
- Los IC representan variabilidad de simulación con parámetros fijos. La variación debida a supuestos de calibración y a costos reales queda fuera de esos intervalos.
- Hace falta acordar el porcentaje de jornadas que debe cumplir ambas metas y la política de pago de horas extra. El costo de un cuarto puesto y los resultados de un piloto de calidad requieren evidencia local.

## 12. Conclusiones para la exposición

Reparación es el principal cuello de botella de E0. El horario de llegadas y la duración del trabajo en curso explican por qué hay vaciado aun con capacidad ociosa en otros momentos. La prueba de carga distingue el balance nominal, la saturación observada y el límite por nivel de servicio. E3 justifica un piloto de validación. E5 ofrece la mayor reducción operativa observada entre las mejoras ensayadas, con mayor costo bajo los valores ilustrativos. Para una recomendación al taller, los próximos antecedentes son mediciones reales, política de cierre y pago, y una meta explícita de cumplimiento por jornada.

## Tablas de respaldo

Cada celda con corchetes muestra **media [IC 95 %]**. Los IC t provienen de los CSV de agregados y diferencias pareadas, salvo el servicio medio derivado por réplica y el cumplimiento conjunto. Un límite t negativo para una magnitud no negativa procede de la aproximación simétrica. Las tablas preservan el cálculo original y redondean desde los valores exportados. [Agregados globales](../results/resumen.csv) · [Agregados por estación](../results/resumen_estaciones.csv) · [Diferencias pareadas](../results/diferencias_pareadas_vs_E0.csv)

### Escenario base global

| Indicador global E0 | Observación | n | Media [IC 95 %] |
| --- | --- | ---: | ---: |
| Vehículos recibidos por día | Turno | 100 | 15,87 [15,16 a 16,58] |
| Entregas dentro del turno por día | Turno | 100 | 12,08 [11,50 a 12,66] |
| Pendientes al cierre por día | Estado al minuto 480 | 100 | 3,79 [3,36 a 4,22] |
| Entregas durante el vaciado por día | Vaciado, incluye ceros | 100 | 3,79 [3,36 a 4,22] |
| Fracción diaria pendiente (%) | Estado al minuto 480 | 100 | 23,31 [21,06 a 25,57] |
| Jornadas sin pendientes (%) | Estado al minuto 480 | 100 | 5,00 [0,65 a 9,35] |
| Llegadas externas (veh/h) | Turno | 100 | 1,984 [1,896 a 2,072] |
| Throughput (veh/h) | Turno | 100 | 1,510 [1,437 a 1,583] |
| Throughput (veh/h) | Apertura a fin de observación | 100 | 1,614 [1,549 a 1,680] |
| Permanencia W (min/veh) | Cohorte completa | 100 | 119,26 [114,58 a 123,94] |
| Espera Wq (min/veh) | Cohorte completa | 100 | 21,26 [17,44 a 25,07] |
| P95 diario de W (min) | Cohorte completa | 100 | 185,92 [177,58 a 194,26] |
| W de vehículos entregados en el turno (min/veh) | Subconjunto entregado hasta el cierre | 100 | 113,90 [109,32 a 118,47] |
| Wq de vehículos entregados en el turno (min/veh) | Subconjunto entregado hasta el cierre | 100 | 19,47 [15,80 a 23,14] |
| Servicio activo acumulado (min-persona/veh) | Cohorte completa | 100 | 98,00 [95,79 a 100,22] |
| Productividad equivalente (veh/h-persona activa) | Cohorte completa | 100 | 0,620 [0,606 a 0,634] |
| L (veh presentes) | Turno | 100 | 3,429 [3,171 a 3,686] |
| Lq (veh en cola) | Turno | 100 | 0,697 [0,539 a 0,855] |
| Utilización global (%) | Turno | 100 | 45,53 [43,54 a 47,52] |
| Llegadas externas (veh/h) | Vaciado de duración positiva | 95 | 0,000 [0,000 a 0,000] |
| Throughput (veh/h) | Vaciado de duración positiva | 95 | 2,370 [2,050 a 2,690] |
| L (veh presentes) | Vaciado de duración positiva | 95 | 2,318 [2,122 a 2,514] |
| Lq (veh en cola) | Vaciado de duración positiva | 95 | 0,285 [0,192 a 0,378] |
| Utilización global (%) | Vaciado de duración positiva | 95 | 33,89 [31,83 a 35,94] |
| Retornos a reparación (visitas/día) | Cohorte completa | 100 | 0,78 [0,62 a 0,94] |
| Retornos a reparación (visitas/día) | Turno | 100 | 0,59 [0,46 a 0,72] |
| Retornos a reparación (visitas/día) | Vaciado, incluye ceros | 100 | 0,19 [0,11 a 0,27] |
| Tiempo extra transcurrido (min/día) | Vaciado, incluye ceros | 100 | 110,03 [98,60 a 121,47] |
| Recibidos de neumáticos (veh/día) | Turno | 100 | 5,72 [5,26 a 6,18] |
| Recibidos eléctricos (veh/día) | Turno | 100 | 4,45 [4,07 a 4,83] |
| Recibidos de mecánica general (veh/día) | Turno | 100 | 5,70 [5,23 a 6,17] |

El servicio activo acumulado por vehículo se obtuvo invirtiendo la productividad equivalente de cada réplica (60/μ, en min-persona/vehículo) y calculando un IC t sobre las 100 medias diarias. Los seis puestos de la red realizan tareas distintas. La productividad global es un indicador laboral equivalente. [Réplicas globales](../results/replicas.csv)

### Estaciones del escenario base

**Turno regular, 100 jornadas.** Los flujos son visitas y L y Lq cuentan vehículos presentes y esperando en el nodo.

| Estación | Servidores | Entradas (visitas/h) | Salidas (visitas/h) | L | Lq | Utilización (%) | Pendientes al cierre (veh) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Recepción | 1 | 1,984 [1,896 a 2,072] | 1,962 [1,873 a 2,052] | 0,183 [0,173 a 0,193] | 0,019 [0,015 a 0,023] | 16,47 [15,70 a 17,23] | 0,17 [0,09 a 0,25] |
| Diagnóstico | 1 | 1,962 [1,873 a 2,052] | 1,859 [1,774 a 1,944] | 0,734 [0,668 a 0,799] | 0,260 [0,210 a 0,310] | 47,41 [45,28 a 49,53] | 0,83 [0,63 a 1,03] |
| Reparación | 3 | 1,933 [1,847 a 2,018] | 1,621 [1,550 a 1,693] | 2,205 [2,015 a 2,396] | 0,381 [0,261 a 0,501] | 60,82 [57,94 a 63,70] | 2,49 [2,15 a 2,83] |
| Control de calidad | 1 | 1,621 [1,550 a 1,693] | 1,584 [1,511 a 1,656] | 0,306 [0,289 a 0,323] | 0,038 [0,032 a 0,044] | 26,84 [25,62 a 28,06] | 0,30 [0,20 a 0,40] |

**Cohorte completa, 100 jornadas.** Incluye las visitas repetidas. S se obtuvo mediante 60/μ por réplica y luego se promedió. μ se promedió directamente sobre tasas diarias.

| Estación | Visitas/día | Servicio S (min/visita) | W (min/visita) | Wq (min/visita) | μ (visitas/h-servidor activo) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Recepción | 15,87 [15,16 a 16,58] | 5,00 [4,95 a 5,05] | 5,54 [5,43 a 5,65] | 0,54 [0,44 a 0,64] | 12,024 [11,907 a 12,141] |
| Diagnóstico | 15,87 [15,16 a 16,58] | 15,05 [14,94 a 15,15] | 22,53 [21,40 a 23,66] | 7,49 [6,36 a 8,61] | 3,992 [3,964 a 4,020] |
| Reparación | 16,65 [15,92 a 17,38] | 64,03 [62,18 a 65,87] | 75,21 [71,32 a 79,10] | 11,18 [8,22 a 14,14] | 0,958 [0,929 a 0,987] |
| Control de calidad | 16,65 [15,92 a 17,38] | 10,05 [9,95 a 10,14] | 11,42 [11,20 a 11,65] | 1,38 [1,20 a 1,55] | 5,986 [5,930 a 6,043] |

**Vaciado.** Los flujos, L, Lq y la utilización se promedian sobre **95** ventanas de duración positiva. Los minutos-persona se promedian sobre las **100** jornadas, con cero en las cinco sin vaciado. Una estación puede recibir visitas internas después del cierre.

| Estación | Entradas (visitas/h) | Salidas (visitas/h) | L | Lq | Utilización (%) | Min-persona activos/día |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Recepción | 0,000 [0,000 a 0,000] | 0,101 [0,048 a 0,153] | 0,004 [0,000 a 0,008] | 0,001 [−0,001 a 0,002] | 0,39 [0,09 a 0,70] | 0,39 [0,13 a 0,64] |
| Diagnóstico | 0,101 [0,048 a 0,153] | 0,515 [0,410 a 0,620] | 0,123 [0,092 a 0,153] | 0,029 [0,016 a 0,042] | 9,38 [7,38 a 11,39] | 11,20 [8,69 a 13,70] |
| Reparación | 0,598 [0,491 a 0,704] | 2,097 [1,916 a 2,277] | 1,757 [1,583 a 1,930] | 0,199 [0,116 a 0,281] | 51,94 [48,25 a 55,62] | 189,72 [162,85 a 216,60] |
| Control de calidad | 2,097 [1,916 a 2,277] | 2,453 [2,139 a 2,767] | 0,434 [0,385 a 0,484] | 0,057 [0,036 a 0,078] | 37,73 [34,26 a 41,21] | 38,28 [33,91 a 42,65] |

[Réplicas por estación](../results/replicas_estaciones.csv)

### Carga E1

| Carga | Recibidos/día | Entregas en turno (veh/h) | W (min/veh) | Wq (min/veh) | Utilización de reparación (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 · 0,50× | 7,99 [7,46 a 8,52] | 0,816 [0,754 a 0,878] | 101,74 [98,54 a 104,94] | 4,27 [3,28 a 5,26] | 31,84 [29,66 a 34,01] |
| E1 · 0,75× | 11,84 [11,20 a 12,48] | 1,175 [1,101 a 1,249] | 106,13 [103,08 a 109,17] | 9,60 [7,50 a 11,70] | 46,27 [43,40 a 49,14] |
| E1 · 1,00× | 15,87 [15,16 a 16,58] | 1,510 [1,437 a 1,583] | 119,26 [114,58 a 123,94] | 21,26 [17,44 a 25,07] | 60,82 [57,94 a 63,70] |
| E1 · 1,25× | 19,82 [19,04 a 20,60] | 1,823 [1,759 a 1,886] | 132,30 [125,91 a 138,68] | 35,88 [30,32 a 41,44] | 71,81 [69,13 a 74,48] |
| E1 · 1,50× | 23,83 [22,94 a 24,72] | 2,022 [1,964 a 2,081] | 157,05 [148,39 a 165,70] | 60,19 [52,23 a 68,14] | 81,15 [79,10 a 83,21] |
| E1 · 1,75× | 27,65 [26,62 a 28,68] | 2,104 [2,046 a 2,161] | 196,19 [184,08 a 208,29] | 98,28 [87,07 a 109,48] | 85,74 [84,19 a 87,28] |
| E1 · 2,00× | 31,98 [30,85 a 33,11] | 2,164 [2,105 a 2,222] | 234,59 [220,87 a 248,31] | 136,63 [123,67 a 149,59] | 87,61 [86,48 a 88,75] |

| Carga | Pendientes al cierre (veh/día) | Fracción diaria pendiente (%) | Vaciado (min/día) | P95 diario de W (min) |
| --- | ---: | ---: | ---: | ---: |
| E1 · 0,50× | 1,46 [1,24 a 1,68] | 18,59 [15,83 a 21,36] | 55,59 [46,18 a 64,99] | 149,34 [143,65 a 155,04] |
| E1 · 0,75× | 2,44 [2,12 a 2,76] | 20,76 [18,22 a 23,30] | 80,87 [71,42 a 90,33] | 161,68 [155,93 a 167,43] |
| E1 · 1,00× | 3,79 [3,36 a 4,22] | 23,31 [21,06 a 25,57] | 110,03 [98,60 a 121,47] | 185,92 [177,58 a 194,26] |
| E1 · 1,25× | 5,24 [4,69 a 5,79] | 25,34 [23,25 a 27,43] | 139,15 [125,51 a 152,80] | 203,29 [192,31 a 214,27] |
| E1 · 1,50× | 7,65 [6,89 a 8,41] | 30,72 [28,47 a 32,98] | 182,13 [164,11 a 200,14] | 242,11 [228,91 a 255,31] |
| E1 · 1,75× | 10,82 [9,78 a 11,86] | 37,27 [34,62 a 39,91] | 256,83 [231,59 a 282,07] | 310,06 [287,75 a 332,37] |
| E1 · 2,00× | 14,67 [13,52 a 15,82] | 44,36 [42,06 a 46,66] | 345,67 [316,81 a 374,53] | 371,53 [346,88 a 396,18] |

El P95 de la tabla es el promedio de los percentiles calculados por jornada. E1 a 1,00× contiene las mismas observaciones que E0. [Respuesta y utilización](../figures/03_respuesta_carga.png) · [Pendientes y vaciado](../figures/04_pendientes_carga.png) · [Throughput](../figures/05_throughput_carga.png)

### Mejoras E2–E5

| Escenario | W (min/veh) | Wq (min/veh) | Pendientes (veh/día) | Vaciado (min/día) | Retrabajos (visitas/día) |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 | 119,26 [114,58 a 123,94] | 21,26 [17,44 a 25,07] | 3,79 [3,36 a 4,22] | 110,03 [98,60 a 121,47] | 0,78 [0,62 a 0,94] |
| E2 | 109,89 [107,23 a 112,55] | 11,83 [10,09 a 13,58] | 3,53 [3,15 a 3,91] | 97,80 [87,05 a 108,54] | 0,86 [0,68 a 1,04] |
| E3 | 116,28 [111,89 a 120,68] | 20,33 [16,74 a 23,92] | 3,74 [3,33 a 4,15] | 102,15 [91,68 a 112,62] | 0,37 [0,26 a 0,48] |
| E4 | 115,02 [111,00 a 119,04] | 17,73 [14,68 a 20,78] | 4,06 [3,61 a 4,51] | 115,26 [102,70 a 127,81] | 0,77 [0,58 a 0,96] |
| E5 | 106,93 [104,45 a 109,42] | 11,54 [9,84 a 13,23] | 3,45 [3,07 a 3,83] | 92,31 [82,57 a 102,06] | 0,33 [0,23 a 0,43] |

Cambios frente a E0 calculados por parejas de semilla.

| Escenario menos E0 | Cambio W (min/veh) | Cambio pendientes (veh/día) | Cambio vaciado (min/día) | Cambio retrabajos (visitas/día) | Cambio margen (CLP/día) |
| --- | ---: | ---: | ---: | ---: | ---: |
| E2 | −9,37 [−12,49 a −6,25] | −0,26 [−0,48 a −0,04] | −12,24 [−19,96 a −4,52] | 0,08 [−0,09 a 0,25] | −46.228,75 [−50.857,78 a −41.599,72] |
| E3 | −2,98 [−4,35 a −1,60] | −0,05 [−0,14 a 0,04] | −7,88 [−13,50 a −2,26] | −0,41 [−0,55 a −0,27] | 3.027,83 [−429,46 a 6.485,12] |
| E4 | −4,24 [−7,56 a −0,92] | 0,27 [0,07 a 0,47] | 5,22 [−3,86 a 14,31] | −0,01 [−0,22 a 0,20] | −4.771,82 [−9.615,81 a 72,18] |
| E5 | −12,33 [−15,58 a −9,07] | −0,34 [−0,59 a −0,09] | −17,72 [−24,95 a −10,49] | −0,45 [−0,63 a −0,27] | −41.753,29 [−46.481,67 a −37.024,90] |

[Gráfico de medias absolutas](../figures/06_escenarios_mejora.png)

### Cumplimiento diario de las metas

Se filtraron las filas de `replicas.csv` por escenario y factor. Para cada día con vehículos recibidos se verificó en la misma fila `extra_min <= 120` y `4 * pendientes_cierre <= recibidos`. Las 1.200 filas tuvieron al menos una llegada. El porcentaje usa como denominador jornadas evaluables, 100 en cada configuración. Se calculó un IC de Wilson bilateral del 95 % para la proporción conjunta. El veredicto sobre medias proviene de comparar por separado las medias de ambas métricas con sus umbrales. Falta acordar un porcentaje mínimo objetivo de cumplimiento por jornada.

| Configuración | Jornadas evaluables | Cumplen tiempo | Cumplen pendientes | Cumplen ambas | Cumplimiento conjunto (%) [IC 95 % Wilson] | Las medias cumplen ambas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 100 | 54 | 58 | 43 | 43,0 [33,7 a 52,8] | Sí |
| E1 · 0,50× | 100 | 91 | 77 | 74 | 74,0 [64,6 a 81,6] | Sí |
| E1 · 0,75× | 100 | 80 | 63 | 57 | 57,0 [47,2 a 66,3] | Sí |
| E1 · 1,00× | 100 | 54 | 58 | 43 | 43,0 [33,7 a 52,8] | Sí |
| E1 · 1,25× | 100 | 46 | 53 | 40 | 40,0 [30,9 a 49,8] | No |
| E1 · 1,50× | 100 | 29 | 36 | 25 | 25,0 [17,5 a 34,3] | No |
| E1 · 1,75× | 100 | 12 | 19 | 12 | 12,0 [7,0 a 19,8] | No |
| E1 · 2,00× | 100 | 4 | 7 | 3 | 3,0 [1,0 a 8,5] | No |
| E2 | 100 | 68 | 67 | 54 | 54,0 [44,3 a 63,4] | Sí |
| E3 | 100 | 62 | 59 | 47 | 47,0 [37,5 a 56,7] | Sí |
| E4 | 100 | 55 | 52 | 39 | 39,0 [30,0 a 48,8] | Sí |
| E5 | 100 | 74 | 65 | 53 | 53,0 [43,3 a 62,5] | Sí |

Las proporciones son descriptivas de cada configuración bajo los supuestos y se informan con su propio intervalo. Las columnas de cada meta cuentan jornadas, y el cumplimiento conjunto exige ambas en una misma jornada. [Réplicas existentes](../results/replicas.csv)

### Economía de la cohorte

**E0 en CLP por jornada, con IC t.**

| Rubro E0 | CLP/día [IC 95 %] |
| --- | ---: |
| Ingresos | 1.700.000,00 [1.615.360,28 a 1.784.639,72] |
| Costos variables | 626.276,00 [594.385,31 a 658.166,69] |
| Personal regular | 255.000,00 [255.000,00 a 255.000,00] |
| Costos operacionales | 70.000,00 [70.000,00 a 70.000,00] |
| Costos de mejoras | 0,00 [0,00 a 0,00] |
| Costos de servicio activo extra | 34.456,89 [29.783,27 a 39.130,51] |
| Margen operacional ilustrativo | 714.267,11 [663.828,87 a 764.705,34] |

**Todas las configuraciones en miles de CLP por jornada.** Cada cifra incluye la cohorte aceptada del turno y el servicio activo en vaciado. Los márgenes de los factores altos incorporan ingresos por trabajos terminados después del cierre. La comparación de factibilidad debe incluir el deterioro de los tiempos de entrega y la política de pago real.

| Configuración | Ingresos | Variables | Personal regular | Operación | Mejoras | Servicio activo extra [IC 95 %] | Margen [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 | 1.700,00 | 626,28 | 255,00 | 70,00 | 0,00 | 34,46 [29,78 a 39,13] | 714,27 [663,83 a 764,71] |
| E1 · 0,50× | 857,70 | 315,11 | 255,00 | 70,00 | 0,00 | 12,17 [9,52 a 14,83] | 205,42 [168,72 a 242,11] |
| E1 · 0,75× | 1.256,40 | 460,40 | 255,00 | 70,00 | 0,00 | 20,44 [17,23 a 23,65] | 450,57 [405,84 a 495,29] |
| E1 · 1,00× | 1.700,00 | 626,28 | 255,00 | 70,00 | 0,00 | 34,46 [29,78 a 39,13] | 714,27 [663,83 a 764,71] |
| E1 · 1,25× | 2.120,20 | 779,31 | 255,00 | 70,00 | 0,00 | 48,60 [42,36 a 54,84] | 967,28 [913,60 a 1.020,97] |
| E1 · 1,50× | 2.552,00 | 938,21 | 255,00 | 70,00 | 0,00 | 74,20 [65,04 a 83,35] | 1.214,60 [1.156,55 a 1.272,64] |
| E1 · 1,75× | 2.980,70 | 1.099,59 | 255,00 | 70,00 | 0,00 | 113,05 [100,01 a 126,10] | 1.443,06 [1.376,84 a 1.509,28] |
| E1 · 2,00× | 3.442,70 | 1.269,11 | 255,00 | 70,00 | 0,00 | 161,05 [145,91 a 176,18] | 1.687,55 [1.616,93 a 1.758,16] |
| E2 | 1.700,00 | 627,95 | 303,00 | 70,00 | 0,00 | 31,02 [26,56 a 35,48] | 668,04 [617,19 a 718,89] |
| E3 | 1.700,00 | 620,70 | 255,00 | 70,00 | 5,00 | 32,00 [27,68 a 36,32] | 717,29 [666,41 a 768,18] |
| E4 | 1.700,00 | 625,92 | 255,00 | 70,00 | 3,00 | 36,59 [31,59 a 41,58] | 709,50 [659,78 a 759,21] |
| E5 | 1.700,00 | 620,34 | 303,00 | 70,00 | 5,00 | 29,15 [25,01 a 33,29] | 672,51 [621,19 a 723,83] |

El gráfico 07 compara E0 y E2–E5. Las filas E1 provienen del CSV de resultados. [Comparación económica](../figures/07_comparacion_economica.png) · [Agregados](../results/resumen.csv)

# Auditoría académica y técnica · Taller en Crisis

La reconstrucción independiente de E0 coincide con las exportaciones en las 100 réplicas. Los 110,03 minutos extra son tiempo de reloj hasta la última entrega. La utilización de reparación del 60,82 % promedia la ocupación de tres mecánicos durante las ocho horas regulares. Los registros muestran que las llegadas tardías y el servicio que resta en esos vehículos explican gran parte del vaciado. También se observaron colas y retrabajos.

## 1. Alcance y método

La auditoría usó Python 3.12.14, Ciw 3.2.7 y la semilla maestra `80912026`. Se ejecutaron las 11 pruebas del repositorio y `pip check`. Una corrida con `main.py --salida <directorio_temporal>` produjo los mismos 14 archivos que la corrida publicada, comparados por SHA-256. Se revisaron los balances de vehículos y margen de las 1.200 filas del experimento.

Para verificar E0 se volvieron a simular las 100 semillas obtenidas de `replica_seeds`. Se observó el estado inicial y el estado posterior a cada `event_and_return_nextnode` de `ciw.Simulation`, mediante una subclase temporal que ejecuta primero el evento original. Cada observación registró el número de vehículos por nodo, los identificadores de servidores ocupados y los contadores acumulados de llegadas y entregas. Se integró el último estado de cada intervalo hasta el siguiente evento, cortando al minuto 480 y a la última entrega. En paralelo, los registros de servicio proporcionaron el recorrido por ID, las horas de entrada, inicio y fin de cada visita, y el destino de cada salida. Se reconstruyeron las métricas sin llamar a `summarize_day`, `station_metrics` ni `economic_metrics`.

Se cotejaron los 1.587 recorridos, las 6.504 visitas y las 100 filas globales y 400 de estación de E0. El máximo residuo en minutos-persona del turno fue `1,14 × 10⁻¹² min` y en el margen fue `1,16 × 10⁻¹⁰ CLP`. Los agregados se recalcularon con DE muestral e IC t bilateral del 95 %. La semilla, parámetros y versiones están en el manifiesto. [Manifiesto](../results/configuracion_ejecutada.json) · [Resultados por jornada](../results/replicas.csv) · [Resultados por jornada y estación](../results/replicas_estaciones.csv)

## 2. Auditoría de la red

| Comprobación | Evidencia |
| --- | --- |
| Uso de Ciw y configuración | `ciw.create_network` y `ciw.Simulation` ejecutaron el flujo recepción → diagnóstico → reparación → calidad. Se observaron cuatro nodos con 1, 1, 3 y 1 servidores. La salida final se registró desde calidad. |
| Cola común de mecánicos | Reparación es un solo nodo FIFO con tres servidores. Para todas las visitas de reparación se conservó el orden de inicio al ordenar por entrada a la cola, incluso entre clases y en reingresos. Se observaron estados con los tres mecánicos ocupados y trabajo en cola. |
| Clases | Los 1.587 ID mantuvieron la misma clase de entrada, clase actual y clase original en todas sus visitas. Recepción, diagnóstico y calidad comparten parámetros entre clases. Reparación selecciona la triangular de la clase del vehículo. |
| Triangulares | La firma instalada es `Triangular(lower, mode, upper)`. El constructor recibe cada tupla en ese orden y el muestreador interno usa `random.triangular(lower, upper, mode)`. Todas las duraciones observadas quedaron dentro de su soporte. Las medias de reparación por visita, agrupadas sobre todas las réplicas, fueron 30,55, 60,55 y 100,33 min, cercanas a sus medias teóricas de 30, 60 y 100 min. |
| Llegadas por tramo | El Poisson unitario se invierte con intensidad acumulada 6, 12 y 16 en los minutos 120, 360 y 480. El punto exponencial pendiente cruza al siguiente tramo sin reiniciarse. La distribución finita suministra a Ciw el calendario por clase. Se observaron 618, 566 y 403 entradas, equivalentes a 3,09, 1,42 y 2,02 veh/h en sus respectivos tramos. Todas las llegadas externas ocurrieron antes de 480. |
| Retrabajos | Las 78 salidas de calidad hacia reparación conservaron su ID y clase. La frecuencia observada fue 78/1.665 controles (4,68 % frente al 5 % configurado). Hubo 1.587 visitas en recepción y diagnóstico, y 1.665 en reparación y calidad. Las visitas nuevas por retorno incrementaron únicamente el conteo de esas estaciones. |
| Pendientes al cierre | Al minuto 480 se tomaron los estados después de procesar los eventos con marca ≤480. Los 379 pendientes coinciden con la diferencia entre 1.587 entradas externas y 1.208 entregas regulares y con las 379 entregas posteriores. Por estado había 17 en recepción, 83 en diagnóstico, 249 en reparación y 30 en calidad. |

[Configuración](../src/config.py) · [Construcción de la red](../src/model.py) · [Pruebas](../tests/test_simulation.py)

## 3. Indicadores consolidados de E0

**J** mide la jornada regular, de 0 a 480 min. **C** identifica la cohorte recibida antes del cierre, seguida hasta que termina su recorrido. **V** abarca desde el cierre hasta la última entrega, cuando existe vaciado. En la tabla, `λ` son entradas y `X` son salidas por hora de J. `S` es servicio activo medio. `W` es permanencia completa y `Wq` es espera completa en C. En estaciones se mide cada visita, incluidos retornos. En la fila global se mide cada vehículo, sumando sus servicios y esperas. `L` y `Lq` son poblaciones medias presentes y en cola, ponderadas por los minutos de J. `ρ` divide los minutos activos por los minutos disponibles de todos los servidores de la fila.

| Estación | Servidores | λ J (entradas/h) | S C (min) | μ C (salidas/h activa por servidor) | W C (min) | Wq C (min) | L J | Lq J | ρ J | X J (salidas/h) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Recepción | 1 | 1,984 | 5,00 | 12,024 | 5,54 | 0,54 | 0,183 | 0,019 | 16,47 % | 1,963 |
| Diagnóstico | 1 | 1,963 | 15,05 | 3,992 | 22,53 | 7,49 | 0,734 | 0,260 | 47,41 % | 1,859 |
| Reparación | 3 | 1,933 | 64,03 | 0,958 | 75,21 | 11,18 | 2,205 | 0,381 | 60,82 % | 1,621 |
| Control de calidad | 1 | 1,621 | 10,05 | 5,986 | 11,42 | 1,38 | 0,306 | 0,038 | 26,84 % | 1,584 |
| **Sistema completo** | **6** | **1,984** | **98,00** | **0,620¹** | **119,26** | **21,26** | **3,429** | **0,697** | **45,53 %** | **1,510** |

¹ En la red, `μ` representa vehículos por hora-persona activa sumada en las cuatro estaciones. Los seis puestos comprenden tareas distintas en serie y la cifra describe productividad laboral equivalente. Por estación, se calculó `60 / S` dentro de cada réplica y luego se promediaron las tasas. Por ejemplo, `60 / 64,03` da aproximadamente 0,937, mientras que el promedio de tasas diarias publicado para reparación es 0,958. Los estimadores se distinguen por el orden de agregación.

| Otros indicadores globales | E0 | Observación |
| --- | ---: | --- |
| Ingresos de vehículos | 15,87 veh/día | Llegadas externas en J |
| Entregados en jornada | 12,08 veh/día | Entregas en J |
| Pendientes al cierre y entregados en vaciado | 3,79 veh/día | Estado al cierre y entregas en V |
| Fracción pendiente | 23,31 % | Media de `pendientes/recibidos` por jornada |
| W y Wq de entregados en jornada | 113,90 y 19,47 min | Vehículos con entrega en J |
| P95 diario medio de permanencia | 185,92 min | Percentil diario de C, promediado entre réplicas |
| Retrabajos | 0,78 visitas/día | 0,59 retornos por día en J y 0,19 en V |
| Tiempo de vaciado | 110,03 min/día | Entre el cierre y la última entrega, contando 5 jornadas con cero |
| λ y X en vaciado | 0,000 y 2,370 veh/h | V, media de 95 ventanas de duración positiva |
| L, Lq y ρ en vaciado | 2,318 veh, 0,285 veh y 33,89 % | V, media de 95 ventanas de duración positiva |
| X de la cohorte | 1,614 veh/h | Todas las entregas sobre `max(480, última entrega)` |

`L`, `Lq` y `ρ` se reconstruyeron a partir del estado entre eventos. En cada estado, la cola es la población del nodo menos sus servidores ocupados. Las tasas se obtuvieron de los contadores y marcas de los registros. `S`, `W` y `Wq` se comprobaron con las diferencias fin−inicio, salida−entrada e inicio−entrada, respectivamente. El balance por visita fue `L = Lq + servidores × ρ` en cada ventana, dada la ausencia de bloqueos. [Agregados globales](../results/resumen.csv) · [Agregados por estación](../results/resumen_estaciones.csv)

**Ley de Little.** Se comprobó sobre la trayectoria completa `[0, H]`, con `H = max(480, última entrega)` y el sistema vacío en ambos extremos. Para cada réplica y para cada nodo o la red, `N` cuenta las visitas completas o los vehículos completos, según corresponda. Se verificaron `L = (N/H) × W` y `Lq = (N/H) × Wq` usando `H` en minutos y las poblaciones integradas desde los estados. Las 1.000 verificaciones tuvieron un residuo máximo de `1,78 × 10⁻¹⁵`. Al cierre regular hay trayectorias incompletas. Por esa razón no se multiplicó una tasa de J por un W de C ni se usó el balance de Little para calcular las ocupaciones publicadas.

## 4. Por qué el vaciado dura 110 minutos

### Congestión observada

| Tramo | Utilización media de reparación | Fracción de tiempo con tres mecánicos ocupados | Fracción de tiempo con cola en reparación |
| --- | ---: | ---: | ---: |
| 09:00–11:00 | 41,6 % | 20,5 % | 8,0 % |
| 11:00–15:00 | 69,8 % | 46,7 % | 27,9 % |
| 15:00–17:00 | 62,1 % | 35,3 % | 16,7 % |
| 16:00–17:00, subconjunto | 66,2 % | 40,2 % | 18,1 % |

En 43 jornadas los tres mecánicos estaban ocupados a las 17:00 y en 23 había cola de reparación al cierre. De los 249 vehículos registrados en ese nodo al cierre, 45 esperaban y 204 estaban en servicio. La jornada empieza con los tres mecánicos libres y los primeros vehículos deben completar recepción y diagnóstico para llegar a reparación. La ociosidad de las primeras horas no se puede trasladar al cierre para procesar llegadas posteriores.

### Llegadas tardías y duración del trabajo

| Hora de llegada | Vehículos recibidos | Entregados después de las 17:00 | Fracción de ese tramo pendiente al cierre |
| --- | ---: | ---: | ---: |
| 09:00–11:00 | 618 | 2 | 0,3 % |
| 11:00–15:00 | 566 | 37 | 6,5 % |
| 15:00–16:00 | 202 | 141 | 69,8 % |
| 16:00–16:30 | 103 | 101 | 98,1 % |
| 16:30–17:00 | 98 | 98 | 100 % |

De los 379 pendientes, 340 (89,7 %) llegaron desde las 15:00 y 199 (52,5 %) llegaron en la última hora. De las 95 jornadas con vaciado, el último vehículo entregado había llegado desde las 15:00 en 93 y desde las 16:00 en 70. Ese último vehículo fue de mecánica general en 59 de las 95 jornadas. Los mínimos del recorrido inicial, incluso con servidores inmediatamente disponibles, son de 33 min en neumáticos, 48 min en eléctrico y 78 min en mecánica general. Por su hora de entrada y clase, 189 pendientes ya carecían de tiempo para completar el recorrido mínimo antes de las 17:00.

Con la duración de servicios registrada para cada vehículo y sus visitas conservadas, 328 de los 379 pendientes seguirían terminando tarde si se sumaran los servicios sin esperar. Para 320 de ellos bastaba el tiempo de la primera pasada para terminar tarde. Los 51 restantes habrían terminado dentro de jornada al quitar las esperas y conservar todos sus servicios. Estos cálculos usan los mismos recorridos como referencia diagnóstica. Una intervención real puede cambiar duraciones, secuencia y retornos.

### Retrabajos y desglose del tiempo de cierre

Se observaron 78 retornos, 19 de ellos disparados después de las 17:00, distribuidos en 18 jornadas. El último vehículo tuvo algún retorno en 16 de las 95 jornadas con vaciado. Para cada una se midieron únicamente los tramos posteriores a 480 de ese último vehículo. Su trayectoria cubre todo el vaciado porque todos los vehículos habían llegado antes del cierre. Las cinco jornadas sin vaciado aportan cero.

| Estado del último vehículo durante el vaciado | Promedio (min/jornada) |
| --- | ---: |
| Servicio en su primera reparación | 67,90 |
| Servicio en reparaciones de retorno | 11,25 |
| Otros servicios en la primera pasada | 15,03 |
| Controles de calidad tras un retorno | 1,51 |
| Esperas de la primera pasada | 12,57 |
| Esperas durante retornos | 1,77 |
| **Total transcurrido** | **110,03** |

Se hizo además el siguiente ejercicio retrospectivo. Para cada jornada, `aᵢ` es la llegada del vehículo `i`, `Sᵢ¹` es la suma de servicios de sus primeras cuatro visitas y `Sᵢ` la suma de todas. El vaciado sin esperas de primera pasada es `max(0, maxᵢ(aᵢ + Sᵢ¹) − 480)`. Al reemplazar `Sᵢ¹` por `Sᵢ`, se incorporan los retornos registrados. Esto produjo **81,47 min** de primera pasada sin espera, **7,74 min** adicionales al incluir retornos sin espera y **20,82 min** de diferencia entre ese cálculo y el vaciado observado. Las tres cifras suman 110,03 min. Los términos dependen del orden de la comparación y el último vehículo puede cambiar al retirar un componente. Este ejercicio puede eliminar esperas de antes del cierre y supone disponibilidad inmediata. El desglose anterior mide el estado efectivo durante el vaciado. Son dos lecturas de las mismas trayectorias.

La intervención ya simulada E3 bajó la probabilidad de retorno de 5 % a 2 %. Redujo el vaciado en 7,88 min/día, con IC pareado del 95 % de −13,50 a −2,26 min. Ese resultado cuantifica el cambio en el modelo al aplicar E3. Queda por validar cuánto retrabajo se evitaría en el taller real y cuánto duraría cada corrección. [Diferencias pareadas](../results/diferencias_pareadas_vs_E0.csv)

### Capacidad, saturación y meta operativa

- **Capacidad nominal.** La mezcla implica 63,5 min por visita de reparación. Con retorno geométrico de probabilidad 5 %, la carga esperada es `63,5/0,95 = 66,84` min-mecánico por vehículo. Con tres mecánicos son 2,69 veh/h o 21,54 vehículos equivalentes en ocho horas de trabajo continuo. El equilibrio de carga media del cuello de botella es aproximadamente 1,35×. Es un balance de trabajo esperado del nodo bajo los supuestos; las entregas requieren completar la red, con arranque, colas y horarios de llegada.
- **Saturación.** Entre 1,50× y 2× se recibieron 8,15 vehículos más por día y se entregaron apenas 1,13 adicionales dentro del turno. La utilización regular de reparación subió de 81,2 % a 87,6 %, la espera media por vehículo de 60,19 a 136,63 min y el vaciado de 182,13 a 345,67 min. La combinación de espera, cola, vaciado y throughput describe la saturación dentro del turno. Al interrumpir las llegadas, el vaciado puede completar el trabajo incluso con carga diaria superior a la capacidad nominal.
- **Límite operativo.** Con las metas ilustrativas de media ≤120 min extra y media diaria ≤25 % de vehículos pendientes, 1,00× es el mayor punto ensayado que satisface ambas. A 1,25× se observan 139,15 min y 25,3 % pendientes. El valor exacto entre puntos queda sin medir. En E0 los IC individuales de las medias cruzan ambas metas y solo **43 de 100 jornadas** cumplieron ambas simultáneamente. La interpretación depende de si el taller fija una meta de medias o un nivel de servicio por jornada. Los umbrales se eligieron para interpretar la simulación y requieren aprobación.

## 5. Auditoría económica

Los montos se documentan en [la configuración](../src/config.py) y en [los supuestos del proyecto](parametros.md). Todos son supuestos ilustrativos. Entre los materiales revisados no hay tarifas reales de un taller, cotizaciones de insumos, contratos de trabajo, boletas ni documentación externa que sustente los importes. Las medias siguientes son cálculos simulados bajo esos valores.

| Clase | Precio por vehículo entregado (CLP) | Materiales de la primera reparación (CLP/vehículo) |
| --- | ---: | ---: |
| Neumáticos | 50.000 | 18.000 |
| Eléctrico | 100.000 | 32.000 |
| Mecánica general | 170.000 | 65.000 |

| Estación | Costo regular (CLP/persona-día) | Tarifa extra (CLP/hora activa) | Min-persona activos extra por día E0 | Costo extra medio E0 (CLP/día) |
| --- | ---: | ---: | ---: | ---: |
| Recepción | 30.000 | 6.000 | 0,39 | 38,79 |
| Diagnóstico | 43.000 | 8.000 | 11,20 | 1.493,04 |
| Reparación | 48.000 | 9.000 | 189,72 | 28.458,63 |
| Control de calidad | 38.000 | 7.000 | 38,28 | 4.466,44 |
| **Total E0** | **255.000 por jornada con los seis puestos** | | **239,59** | **34.456,89** |

Se cargan 70.000 CLP/día de operación, 35 % del costo variable de la clase por cada retrabajo y cero ingreso adicional por retorno. Se asignan 5.000 CLP/día por la mejora de calidad y 3.000 por la agenda en los escenarios respectivos. Un cuarto mecánico agrega 48.000 CLP/día de costo regular, con la misma tarifa activa extra que los otros mecánicos. Los 255.000 CLP de E0 equivalen a `30.000 + 43.000 + 3 × 48.000 + 38.000`.

Para cada ID se compararon los ingresos de la entrega final con el costo variable de la primera reparación más los materiales de sus retornos. Se incluye toda la cohorte aceptada antes del cierre, aunque un vehículo se entregue en vaciado. Los costos fijos se cargan por jornada de ingreso y el trabajo activo posterior al cierre se imputa a esa misma jornada. En E0, el ingreso medio fue de 1.700.000 CLP, los materiales iniciales fueron 615.860 CLP, los materiales de retorno 10.416 CLP y el margen 714.267,11 CLP por jornada. Los totales se reconciliaron en cada réplica.

El costo extra se recalculó por ID de servidor, sumando la fracción de cada servicio entre el cierre y la entrega final y multiplicándola por la tarifa de su estación. Coincidió con la integración de los estados de servidores ocupados. Los 239,59 min-persona y los 110,03 min de reloj pueden coexistir porque varios recursos trabajan a la vez. La política actual costea servicio activo. Quedan por validar el costo de permanencia del personal en espera de trabajo, los recargos o mínimos de pago, la inversión del cuarto puesto y la imputación contable si el taller permite arrastre entre jornadas.

## 6. Inconsistencias y decisiones para revisión

| Hallazgo | Impacto | Corrección propuesta o decisión humana |
| --- | --- | --- |
| La explicación anterior de E4 dice que las llegadas se desplazan a horas posteriores sin acotar el tramo. Ambas intensidades acumuladas valen 12 a las 15:00 y ambas tasas son 2 veh/h desde entonces. Al comparar las 100 parejas de semillas, coincidieron los 403 tiempos y clases posteriores a las 15:00, con diferencia máxima de `5,68 × 10⁻¹⁴ min`. | Sería incorrecto atribuir el aumento de pendientes de E4 a más llegadas después de las 15:00. El cambio actúa hasta esa hora. El arrastre de cola y la reasignación de muestras Ciw son mecanismos plausibles. La auditoría no cuantificó su contribución individual. | Precisar que E4 redistribuye llegadas de 09:00–11:00 hacia 11:00–15:00 y obtiene +0,27 pendientes diarios [0,075 a 0,465]. La variación de tiempo extra, +5,22 min [−3,86 a 14,31], es incierta. La formulación se corrige en el resumen académico de esta fase. |
| La definición textual de μ describe el recíproco del tiempo medio sin explicitar que se promedian recíprocos diarios. | Una división directa con las medias de la tabla genera discrepancias aparentes. El cálculo publicado reproduce los registros. | Etiquetar `media de tasas diarias` en la presentación. Si se exige una tasa agrupada por todas las visitas de la corrida, acordar el estimador y publicar su denominador. |
| Un umbral sobre medias diarias se puede confundir con compromiso por jornada. | E0 cumple ambas metas en promedio, pero ambas se cumplen a la vez en 43/100 días simulados. | Definir con el profesor o el taller la unidad de servicio, el porcentaje objetivo y el horario aceptable de entrega antes de usar el límite como capacidad comprometida. |
| Los costos extra representan tiempo activo y las cifras económicas son ilustrativas. | El resultado de margen depende de la política de pago y del costo de materiales. Podría subestimar el costo si se paga disponibilidad posterior al cierre. | Obtener evidencia de tarifas, costos y disponibilidad. Validar E3 antes de usar su punto de equilibrio estimado para una decisión real. |
| Reproducibilidad verificada en el entorno actual, con dependencias directas fijadas. | Los requisitos permiten versiones transitivas distintas en una instalación nueva. El manifiesto registra la versión de Python y cuatro dependencias directas. | Registrar la instalación completa o fijar transitivas si la entrega exige identidad de archivos en otros equipos. |

La fase deja documentadas las precisiones de interpretación y agrega el resumen académico. No se detectaron errores numéricos en las métricas auditadas de E0. El código, los parámetros y las exportaciones de la corrida publicada se conservaron.
